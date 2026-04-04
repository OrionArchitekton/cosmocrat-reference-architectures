#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


PASSING_CHECK_RUN_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PENDING_STATES = {"PENDING", "EXPECTED", "MISSING"}


def fetch_json(url: str, token: str) -> tuple[object, str]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "reference-architectures-required-checks",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp), resp.headers.get("Link", "")


def next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        if not section.startswith("<") or ">;" not in section:
            continue
        return section[1 : section.index(">;")]
    return None


def fetch_paginated_items(url: str, token: str, item_key: str | None = None) -> list[dict]:
    items: list[dict] = []
    next_url: str | None = url

    while next_url:
        payload, link_header = fetch_json(next_url, token)
        if item_key is None:
            if not isinstance(payload, list):
                raise ValueError("expected paginated list payload")
            items.extend(payload)
        else:
            if not isinstance(payload, dict):
                raise ValueError("expected paginated object payload")
            items.extend(payload.get(item_key, []))
        next_url = next_link(link_header)

    return items


def get_http_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def is_retryable_http_error(exc: urllib.error.HTTPError, body: str) -> bool:
    if exc.code == 429 or exc.code >= 500:
        return True
    if exc.code != 403:
        return False
    if exc.headers.get("Retry-After"):
        return True
    if exc.headers.get("X-RateLimit-Remaining") == "0":
        return True
    lowered = body.lower()
    return "rate limit" in lowered or "secondary rate limit" in lowered


def latest_matching_item(items: list[dict], key: str, value: str) -> dict | None:
    matches = [item for item in items if item.get(key) == value]
    if not matches:
        return None

    def sort_key(item: dict) -> tuple[int, str, str]:
        return (
            int(item.get("id") or 0),
            item.get("completed_at")
            or item.get("updated_at")
            or item.get("created_at")
            or "",
            item.get("started_at") or "",
        )

    return max(matches, key=sort_key)


def check_state(name: str, check_runs: list[dict], statuses: list[dict]) -> str:
    item = latest_matching_item(check_runs, "name", name)
    if item:
        if item.get("status") != "completed":
            return "PENDING"
        conclusion = (item.get("conclusion") or "MISSING").upper()
        if conclusion in PASSING_CHECK_RUN_CONCLUSIONS:
            return "SUCCESS"
        return conclusion

    item = latest_matching_item(statuses, "context", name)
    if item:
        state = (item.get("state") or "MISSING").upper()
        if state in {"PENDING", "EXPECTED"}:
            return "PENDING"
        if state == "SUCCESS":
            return "SUCCESS"
        return state

    return "MISSING"


def check_state_with_fallback(
    name: str,
    primary_check_runs: list[dict],
    primary_statuses: list[dict],
    fallback_check_runs: list[dict],
    fallback_statuses: list[dict],
    fallback_enabled: bool,
) -> str:
    primary_state = check_state(name, primary_check_runs, primary_statuses)
    if primary_state != "MISSING" or not fallback_enabled:
        return primary_state
    return check_state(name, fallback_check_runs, fallback_statuses)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--merge-sha")
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--required-checks", required=True)
    parser.add_argument("--max-attempts", type=int, default=40)
    parser.add_argument("--sleep-seconds", type=int, default=15)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GH_TOKEN or GITHUB_TOKEN is required", file=sys.stderr)
        return 1

    required = [item.strip() for item in args.required_checks.split(",") if item.strip()]
    if not required:
        print("required checks list must not be empty", file=sys.stderr)
        return 1
    if args.max_attempts <= 0:
        print("MAX_ATTEMPTS must be a positive integer", file=sys.stderr)
        return 1
    if args.sleep_seconds <= 0:
        print("SLEEP_SECONDS must be a positive integer", file=sys.stderr)
        return 1

    repo = urllib.parse.quote(args.repo, safe="/")
    primary_sha = args.merge_sha or args.head_sha
    fallback_sha = args.head_sha if args.head_sha != primary_sha else None
    if not primary_sha:
        print("unable to determine a commit SHA to evaluate", file=sys.stderr)
        return 1

    def commit_urls(ref: str) -> tuple[str, str]:
        sha = urllib.parse.quote(ref, safe="")
        return (
            f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs?per_page=100",
            f"https://api.github.com/repos/{repo}/commits/{sha}/statuses?per_page=100",
        )

    primary_check_runs_url, primary_statuses_url = commit_urls(primary_sha)
    fallback_enabled = fallback_sha is not None
    if fallback_enabled:
        fallback_check_runs_url, fallback_statuses_url = commit_urls(fallback_sha)
    else:
        fallback_check_runs_url = ""
        fallback_statuses_url = ""

    last_non_success_by_check: dict[str, str] = {}

    for attempt in range(1, args.max_attempts + 1):
        try:
            primary_check_runs = fetch_paginated_items(primary_check_runs_url, token, "check_runs")
            primary_statuses = fetch_paginated_items(primary_statuses_url, token)
            fallback_check_runs = (
                fetch_paginated_items(fallback_check_runs_url, token, "check_runs")
                if fallback_enabled
                else []
            )
            fallback_statuses = (
                fetch_paginated_items(fallback_statuses_url, token) if fallback_enabled else []
            )
        except urllib.error.HTTPError as exc:
            body = get_http_error_body(exc)
            if is_retryable_http_error(exc, body) and attempt < args.max_attempts:
                retry_after = exc.headers.get("Retry-After")
                wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else args.sleep_seconds
                print(f"GitHub API transient error on attempt {attempt}: {exc}", file=sys.stderr)
                time.sleep(wait_seconds)
                continue
            detail = f"{exc}: {body}" if body else str(exc)
            print(f"GitHub API request failed: {detail}", file=sys.stderr)
            return 1
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < args.max_attempts:
                print(f"GitHub API transient network failure on attempt {attempt}: {exc}", file=sys.stderr)
                time.sleep(args.sleep_seconds)
                continue
            print(f"GitHub API network request failed after {attempt} attempts: {exc}", file=sys.stderr)
            return 1
        except (json.JSONDecodeError, ValueError) as exc:
            print(
                "GitHub API response parsing failed (likely permanent error, not retrying): "
                f"{exc}",
                file=sys.stderr,
            )
            return 1

        pending = False
        has_failure = False
        for name in required:
            state = check_state_with_fallback(
                name,
                primary_check_runs,
                primary_statuses,
                fallback_check_runs,
                fallback_statuses,
                fallback_enabled,
            )
            if state == "SUCCESS":
                last_non_success_by_check.pop(name, None)
                print(f"check '{name}' OK ({state})")
                continue
            if state in PENDING_STATES:
                last_non_success_by_check[name] = state
                print(f"check '{name}' not ready yet ({state})")
                pending = True
                continue
            previous_state = last_non_success_by_check.get(name)
            last_non_success_by_check[name] = state
            if previous_state != state:
                print(f"check '{name}' currently failing ({state})", file=sys.stderr)
            else:
                print(f"check '{name}' still failing ({state})")
            has_failure = True

        if not pending:
            if not has_failure:
                return 0
            print(
                "non-success terminal states observed; waiting for reruns until timeout "
                f"(attempt {attempt}/{args.max_attempts})"
            )

        if attempt == args.max_attempts:
            details = "; ".join(
                f"{name}: {state}" for name, state in last_non_success_by_check.items()
            )
            if details:
                print(
                    "required checks did not reach a successful terminal state in time "
                    f"({details})",
                    file=sys.stderr,
                )
            else:
                print(
                    "required checks did not reach a successful terminal state in time",
                    file=sys.stderr,
                )
            return 1

        time.sleep(args.sleep_seconds)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
