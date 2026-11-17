"""gitleaks: scan every commit a pull request brings into main (series issue 20).

Run by .github/workflows/gitleaks-scan.yml on every pull request and every push to main.
Standard library only. Spec: specs/gitleaks-pr-scan-spec.md.

Pull request: every commit reachable from the head and not from the base (git's two-dot
base..head), merge commits included, each merge with its own patch against its first parent,
no first-parent walk and no commit limit. Push: before..after the same way.
"""

import dataclasses
import hashlib
import io
import os
import re
import secrets
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

# The tool: gitleaks 8.24.3 (the version gitleaks-action ff98106 ran), from its official
# release. The sha256 is the archive's line in that release's gitleaks_8.24.3_checksums.txt.
GITLEAKS_VERSION = "8.24.3"
ARCHIVE_NAME = f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz"
ARCHIVE_URL = ("https://github.com/gitleaks/gitleaks/releases/download/"
               f"v{GITLEAKS_VERSION}/{ARCHIVE_NAME}")
ARCHIVE_SHA256 = "9991e0b2903da4c8f6122b5c3186448b927a5da4deef1fe45271c3793f4ee29c"
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024  # the archive is about 7 MB
DOWNLOAD_TIMEOUT = 120  # seconds

OBJECT_ID = re.compile(r"[0-9a-f]{40}")
ZERO_ID = "0" * 40  # a push event's `before` when the branch was just created
# Each merge commit's own change, as a patch against its first parent. Without it `git log -p`
# prints no patch for a merge (git's --diff-merges default for log), so a line that only the
# merge adds would never reach gitleaks.
MERGE_PATCHES = "--diff-merges=first-parent"


class ScanRefused(Exception):
    """Anything the scan cannot positively verify. The job fails with the rule's name."""

    def __init__(self, rule, detail):
        super().__init__(f"{rule}: {detail}")
        self.rule = rule


@dataclasses.dataclass(frozen=True)
class Event:
    name: str
    base: object  # a commit id, or None for a push that created the branch
    head: str


def _commit_id(environ, key, zero_allowed=False):
    value = environ.get(key)
    if value is None or not OBJECT_ID.fullmatch(value) or (value == ZERO_ID and not zero_allowed):
        raise ScanRefused("bad-commit-id", f"{key} is {value!r}, not a 40-hex commit id")
    return value


def read_event(environ):
    """The event the step's env: block describes."""
    name = environ.get("SCAN_EVENT", "")
    if name == "push":
        before = _commit_id(environ, "SCAN_PUSH_BEFORE", zero_allowed=True)
        after = _commit_id(environ, "SCAN_PUSH_AFTER")
        return Event("push", None if before == ZERO_ID else before, after)
    if name == "pull_request":
        return Event("pull_request", _commit_id(environ, "SCAN_PR_BASE"),
                     _commit_id(environ, "SCAN_PR_HEAD"))
    raise ScanRefused("unknown-event", f"event {name!r} is neither pull_request nor push")


def scan_range(event):
    """The git revision range the scan covers: every commit reachable from the head and not
    from the base (two dots), or the pushed commit alone when the push created the branch."""
    if event.base is None:
        return f"{event.head}^!"
    return f"{event.base}..{event.head}"


def log_options(event):
    """The --log-opts text gitleaks hands to `git log -p -U0` (split on single spaces)."""
    return f"{MERGE_PATCHES} {scan_range(event)}"


def _git(source, *args):
    """Run git in the checkout; return (exit code, stdout text)."""
    out = subprocess.run(["git", "-C", source, *args], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    return out.returncode, out.stdout.decode("utf-8", "replace").strip()


def count_range(source, event):
    """`git rev-list --count` of the scan range, after checking each id names a commit."""
    for commit in (event.base, event.head):
        if commit is None:
            continue
        rc, _ = _git(source, "rev-parse", "--verify", "--quiet", "--end-of-options",
                     f"{commit}^{{commit}}")
        if rc != 0:
            raise ScanRefused("commit-not-found", f"{commit} is not a commit in the checkout")
    if event.name == "pull_request":
        rc, _ = _git(source, "merge-base", event.base, event.head)
        if rc != 0:
            raise ScanRefused("no-merge-base",
                              f"base {event.base} and head {event.head} share no history")
    rc, out = _git(source, "rev-list", "--count", scan_range(event))
    if rc != 0 or not out.isdigit():
        raise ScanRefused("git-error", f"git rev-list --count {scan_range(event)} failed")
    count = int(out)
    if count == 0:
        raise ScanRefused("empty-range", f"{scan_range(event)} holds no commit to scan")
    return count


def verified_binary(data, dest, expected=ARCHIVE_SHA256):
    """Check the archive's sha256 before opening it, then write its gitleaks binary into dest."""
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ScanRefused("checksum-mismatch",
                          f"{ARCHIVE_NAME} has sha256 {actual}, the release lists {expected}")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        try:
            member = tar.getmember("gitleaks")
        except KeyError:
            member = None
        if member is None or not member.isreg():
            raise ScanRefused("archive-member", f"{ARCHIVE_NAME} holds no regular file gitleaks")
        binary = tar.extractfile(member).read()
    path = os.path.join(dest, "gitleaks")
    with open(path, "wb") as f:
        f.write(binary)
    os.chmod(path, 0o700)
    return path


def check_version(binary):
    """The binary must report exactly the pinned version."""
    out = subprocess.run([binary, "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    printed = out.stdout.decode("utf-8", "replace").strip()
    if out.returncode != 0 or printed != GITLEAKS_VERSION:
        raise ScanRefused("gitleaks-version", f"the binary reports {printed!r} (exit "
                          f"{out.returncode}), not {GITLEAKS_VERSION}")
    return printed


def gitleaks_log_command(source, options):
    """The exact git command gitleaks 8.24.3 runs for `gitleaks git --log-opts=<options> <source>`
    (sources/git.go, NewGitLogCmd, tag v8.24.3): the options are split on single spaces."""
    return ["git", "-C", source, "log", "-p", "-U0", *options.split(" ")]


def _binary_marker(line):
    """go-gitdiff v0.9.1 ParseBinaryMarker: the line after a file header that marks it binary."""
    return (line in ("GIT binary patch", "Binary files differ", "Files differ")
            or (line.startswith("Binary files ") and line.endswith("differ")))


def expected_commits(stream):
    """The commits of the patch stream that gitleaks 8.24.3 counts as scanned.

    gitleaks counts a commit when one of its file patches is neither binary nor a deletion
    (detect/git.go, DetectGit: the IsBinary/IsDelete skip comes before addCommit). go-gitdiff
    v0.9.1, the parser it uses, starts a commit at a line beginning "commit ", a file at a line
    beginning "diff --git ", marks a deletion by a "deleted file mode " header line and a binary
    file by the marker line after the header. Patch content lines start with "+", "-", " " or
    "\\", and commit message lines are indented, so none of them can be taken for these.
    """
    found = set()
    commit = None
    state = {"open": False, "header": False, "skip": False}

    def close_file():
        if state["open"] and not state["skip"] and commit:
            found.add(commit)
        state.update(open=False, header=False, skip=False)

    for line in stream.split("\n"):
        if line.startswith("commit "):
            close_file()
            commit = line[len("commit "):].split(" ", 1)[0]
        elif line.startswith("diff --git "):
            close_file()
            state.update(open=True, header=True)
        elif state["header"]:
            if line.startswith("@@ "):
                state["header"] = False
            elif line.startswith("deleted file mode "):
                state["skip"] = True
            elif _binary_marker(line):
                state.update(skip=True, header=False)
    close_file()
    return found


SCANNED_LINE = re.compile(r"(\d+) commits scanned\.")
LEAKS_LINE = re.compile(r"leaks found: \d+")
EXIT_LEAKS = 2  # passed to gitleaks as --exit-code


def judge(returncode, log, expected, in_range):
    """gitleaks' exit and log (stderr) against the counts; returns gitleaks' count."""
    if returncode == EXIT_LEAKS:
        found = LEAKS_LINE.search(log)
        raise ScanRefused("leaks-found", (found.group(0) if found else "gitleaks exit 2")
                          + "; the findings above are redacted")
    if returncode != 0:
        raise ScanRefused("gitleaks-error", f"gitleaks exited {returncode}")
    if "partial scan" in log:
        raise ScanRefused("gitleaks-error", "gitleaks reports a partial scan")
    if not re.search(r"\bINF no leaks found$", log, re.M):
        raise ScanRefused("gitleaks-error", "gitleaks did not report 'no leaks found'")
    counts = SCANNED_LINE.findall(log)
    if len(counts) != 1:
        raise ScanRefused("count-line-missing",
                          f"gitleaks logged {len(counts)} 'commits scanned' lines, not one")
    scanned = int(counts[0])
    if scanned > in_range:
        raise ScanRefused("count-exceeds-range",
                          f"gitleaks scanned {scanned} commits, the range holds {in_range}")
    if scanned != expected:
        raise ScanRefused("count-mismatch", f"gitleaks scanned {scanned} commits, the patch "
                          f"stream holds {expected} it should count")
    return scanned


def patch_stream(source, event):
    """The patch stream gitleaks reads for this event, as text (undecodable bytes kept)."""
    out = subprocess.run(gitleaks_log_command(source, log_options(event)), check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out.stdout.decode("utf-8", "surrogateescape")


def _say(line):
    print(line, flush=True)


def fetch_archive(environ):
    """The release archive's bytes, downloaded from ARCHIVE_URL, or read from the local copy
    that SCAN_GITLEAKS_ARCHIVE names (the evidence runs). Its sha256 is checked next either way."""
    local = environ.get("SCAN_GITLEAKS_ARCHIVE")
    try:
        if local:
            with open(local, "rb") as f:
                data = f.read(MAX_ARCHIVE_BYTES + 1)
        else:
            with urllib.request.urlopen(ARCHIVE_URL, timeout=DOWNLOAD_TIMEOUT) as response:
                data = response.read(MAX_ARCHIVE_BYTES + 1)
    except (OSError, ValueError) as error:
        raise ScanRefused("download-error", f"{ARCHIVE_NAME}: {error}") from None
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ScanRefused("download-error",
                          f"{ARCHIVE_NAME} is larger than {MAX_ARCHIVE_BYTES} bytes")
    return data


def gitleaks_args(binary, source, options):
    """gitleaks 8.24.3 over the log options, findings redacted, its own exit code for a leak, no
    remote lookup. No --config: as under the action, it reads a root .gitleaks.toml if any."""
    return [binary, "git", f"--log-opts={options}", "--redact", "--verbose", "--no-banner",
            "--no-color", "--platform", "none", f"--exit-code={EXIT_LEAKS}", source]


def run_gitleaks(binary, source, options, environ):
    """Run gitleaks with every GITLEAKS_ variable removed; return (exit, stdout, stderr)."""
    env = {key: value for key, value in environ.items() if not key.startswith("GITLEAKS_")}
    out = subprocess.run(gitleaks_args(binary, source, options), env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (out.returncode, out.stdout.decode("utf-8", "replace"),
            out.stderr.decode("utf-8", "replace"))


def run_scan(environ, source, archive_sha256):
    """The whole scan; returns normally only when every rule holds."""
    event = read_event(environ)
    options = log_options(event)
    _say(f"event: {event.name}")
    _say(f"range: {scan_range(event)}")
    _say(f"log options: {options}")
    in_range = count_range(source, event)
    _say(f"commits in range (git rev-list --count): {in_range}")
    try:
        stream = patch_stream(source, event)
    except subprocess.CalledProcessError as error:
        raise ScanRefused("git-error",
                          f"git log -p -U0 {options} exited {error.returncode}") from None
    expected = len(expected_commits(stream))
    _say(f"expected commits (file patches gitleaks counts): {expected}")
    data = fetch_archive(environ)
    with tempfile.TemporaryDirectory(prefix="gitleaks-") as dest:
        binary = verified_binary(data, dest, archive_sha256)
        version = check_version(binary)
        _say(f"tool: gitleaks {version} from {ARCHIVE_NAME}, sha256 {archive_sha256} checked")
        returncode, findings, log = run_gitleaks(binary, source, options, environ)
    # Between these markers the runner takes no line as a workflow command, so a file's content
    # quoted in gitleaks' output cannot set an output, mask or annotation for the job.
    token = secrets.token_hex(16)
    _say("gitleaks output:")
    _say(f"::stop-commands::{token}")
    _say((findings + log).rstrip("\n"))
    _say(f"::{token}::")
    scanned = judge(returncode, log, expected, in_range)
    _say(f"commits scanned (gitleaks): {scanned}")


def main(environ=None, source=".", archive_sha256=ARCHIVE_SHA256):
    """Run the scan; the last line printed is RESULT: PASS or RESULT: FAIL <rule>: <detail>."""
    environ = os.environ if environ is None else environ
    try:
        run_scan(environ, source, archive_sha256)
    except ScanRefused as refusal:
        _say(f"RESULT: FAIL {refusal}")
        return 1
    except Exception as error:  # anything unforeseen fails the check too
        _say(f"RESULT: FAIL error: {type(error).__name__}: {error}")
        return 1
    _say("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
