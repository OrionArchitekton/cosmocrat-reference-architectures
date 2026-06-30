# Cosmocrat Reference Architectures Repo Contract

Date: 2026-06-30

Status: binding repo-local contract.

## Current Name

- `cosmocrat-reference-architectures`

## Recommended Name

- `cosmocrat-reference-architectures`

## Role

- `governance-reference`

## Purpose

`cosmocrat-reference-architectures` is the docs-only explanatory surface for
Cosmocrat topology, deployment composition, and proof-line interpretation. It
makes product boundaries legible without becoming an implementation, runtime,
policy-pack, SDK, or operational deployment repo.

It explains the reference posture. It does not authorize repo movement,
runtime migration, or Stage F business-stack work.

## Owns

- documentation-class topology narratives
- boundary maps and reference-composition explanations
- proof-line and durable-receipt interpretation
- linked Stage C supporting inputs that remain outside owned content
- docs-integrity validation for the explanatory surface

## Does Not Own

- kernel logic or kernel semantic changes
- governed client implementation
- runtime execution assets
- Docker, Kubernetes, or operational deployment assets
- operator runbooks, dashboards, or recovery instructions
- policy-pack content
- SDK or contracts enactment
- memory-governance implementation
- repo migration authority or Stage F business-stack work

## Allowed Dependencies

- estate canon from `orion-estate-audit`
- kernel and SDK repos as named authoritative implementation homes
- `orion-infra` as the current operational/package source for reference
  deployment composition reading paths
- local explanatory docs under `docs/`
- linked frozen Stage C inputs only where admitted by canon

## Forbidden Logic / Forbidden Ownership

- runnable application, package, build, or deploy artifacts
- operational deployment manifests or recovery procedures
- policy-pack, SDK, or kernel contract implementation
- runtime authority assets or business workflow logic
- absorbing additional Stage C assets by convenience
- treating snapshot contract text as current kernel or SDK authority

## PR Reject Rules

- reject PRs that add runnable code, package manifests, or deploy assets
- reject PRs that turn reference explanation into runtime or operator authority
- reject PRs that move kernel, SDK, policy-pack, or memory-governance ownership
  into this repo
- reject PRs that authorize repo movement or Stage F pull-forward
- reject PRs that absorb frozen supporting inputs as owned content

## Verification

For docs-only contract changes:

```bash
git diff --check origin/main...HEAD
```

For broader docs changes, follow `AGENTS.md` and run the repo-defined
docs-integrity checks.

## Basis

- `AGENTS.md`
- `README.md`
- `docs/topology-boundary.md`
- `docs/reference-deployment-composition.md`
- `docs/linked-supporting-inputs.md`
- `docs/integration-composition.md`
- `docs/proof-line.md`
- `repos/repo_contract_registry_20260317.csv` in
  `OrionArchitekton/orion-estate-audit`
- `COSMOCRAT_PRODUCT_FAMILY_REPO_CONTRACT_20260317.md` in
  `OrionArchitekton/orion-estate-audit`
- `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_NOTE_20260313.md`
  in `OrionArchitekton/orion-estate-audit`
