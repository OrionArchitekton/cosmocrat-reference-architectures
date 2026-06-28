# Cosmocrat Reference Architectures

Docs-only reference surface that explains Cosmocrat's product boundary,
deployment composition, and governed proof line for readers and reviewers.

Agent and reviewer navigation guide: [AGENTS.md](AGENTS.md)

This repository is the docs-only reference surface for Cosmocrat — a
governed control-plane product built around a narrow decision kernel. It
contains explanatory Markdown only: no runnable application, no package
manifest, no build, no tests, and no deployable assets. The kernel, SDK,
and operational deploy stack live in separate repositories (see
[Where the code lives](#where-the-code-lives)).

It exists to help a reader understand:

- the product boundary around the Cosmocrat kernel
- the current default deploy/reference composition reading path
- the proof line from a governed decision to durable receipt evidence
- the linked Stage C supporting inputs that remain outside owned
  reference-architectures content

## Reading Order

1. [Topology and Boundary](./docs/topology-boundary.md)
2. [Reference Deployment and Composition](./docs/reference-deployment-composition.md)
   - start here for the current deploy/reference explanation, then follow
     the named operational sources from that page
3. [Integration Composition](./docs/integration-composition.md)
4. [Proof Line](./docs/proof-line.md)
5. [Linked Supporting Inputs](./docs/linked-supporting-inputs.md)

## Supporting Input Rule

In this repository (see [Linked Supporting Inputs](./docs/linked-supporting-inputs.md)
for details):

- the Stage C architecture companion is treated as owned
  reference-architecture content
- the only Stage C artifacts that remain linked supporting inputs are the
  demo kit, receipt pack, and replay bundle

## Boundary

This is a documentation-class reference surface only.

It explains the current composition shape, but the actual operational
composition root lives in a separate infrastructure repository, not here.

It does not authorize or contain:

- runtime authority assets
- Docker or Kubernetes operational assets
- policy packs
- SDK or contracts enactment
- memory-governance implementation
- repo migration
- Stage F runtime or business-stack work

## Where the code lives

Nothing in this repository is runnable. The implementations the docs
describe live elsewhere:

- **Kernel** (decision evaluation, Chronicle receipt persistence,
  HTTP contract): a separate `cosmocrat-kernel` repository.
- **SDK** (request/response JSON schemas the governed client uses): a
  separate `cosmocrat-sdk` repository.
- **Operational composition root** (the canonical Compose stack that
  renders the shared stores and the kernel service): a separate
  infrastructure repository.

These are distinct repositories and may not all be publicly accessible.
This repo links to them by name in the docs; deep links are deliberately
described rather than guaranteed-resolvable for external readers.

## Contract snapshot

The integration docs ([integration-composition.md](./docs/integration-composition.md))
describe the kernel's runtime contract in detail: the `COSMOCRAT_CORE_*`
environment variables, the `POST /decision` and `GET /receipts/{id}`
surfaces, HTTP status codes, and the request/response shapes.

That contract is owned by the kernel and SDK repositories, not by this
repo. This repository cannot self-validate those claims, because the
kernel and SDK code are not present here. Treat the contract description
as a snapshot of the Stage E reference posture (architecture canon dated
2026-03-13; proof freezes dated 2026-03-10 to 2026-03-11). For the
authoritative, current contract, read the kernel and SDK repositories
directly.

## Validation

This repo is docs-only — there is nothing to install or run. Doc quality
is enforced by GitHub Actions:

- **docs-integrity** — `git diff --check` hygiene, a required-files
  presence check (`README.md` plus the five `docs/*.md` pages),
  `markdownlint-cli2` over `README.md` and `docs/**/*.md` (default rule
  set; no markdownlint config is committed), and a `lychee` link-integrity
  pass.
- **gitleaks** — full-history secret scan.
- **required-checks-fail-closed** — a Python gate
  (`.github/scripts/verify_required_checks.py`, Python 3.12, stdlib only)
  that polls the GitHub checks API and fails closed unless both
  `docs-integrity` and `gitleaks` reach a successful terminal state.

To check your changes locally before pushing, run the same diff-hygiene
gate the CI uses:

```bash
git diff --check origin/main...HEAD
```

Note: the `lychee` link check excludes links into the separate
`cosmocrat-kernel`, `cosmocrat-sdk`, and internal-audit repositories, so
CI does not validate those targets. Confirm those references manually if
you depend on them.

## License

No `LICENSE` file is present in this repository. Until one is added, no
explicit reuse terms are granted; treat the contents as all rights
reserved.
