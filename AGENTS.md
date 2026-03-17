# Cosmocrat Reference Architectures Agent Guide

## Repo Role

`cosmocrat-reference-architectures` is the docs-only Stage E reference
surface for Cosmocrat.

Use it to:
- explain topology and boundary shape
- explain reference deployment and composition at a documentation level
- explain the proof line from governed decision to durable receipt evidence
- preserve linked supporting inputs without absorbing runtime or operator assets

Do not treat this repo as:
- an implementation repo
- an operational deployment repo
- a runtime authority surface
- a policy-pack repo
- an sdk or contracts enactment repo
- a place to pull Stage F runtime or business-stack work forward

## Operating Rule

This file is a navigation and operating guide, not a new doctrine layer.

Do not restate canon if a pointer is enough.
Do not silently widen reference-architectures content into runtime,
deployment, policy, or sdk territory.
Prefer small explanatory and navigation changes over broad rewrites.

## Authority Order

When reviewing or editing this repo, load authority in this order:

1. `OrionArchitekton/orion-estate-audit`
   - `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_NOTE_20260313.md`
   - `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_ENTRYPOINT_20260313.md`
   - `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_EXECUTION_BRIEF_20260313.md`
   - `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_ADMISSION_BAR_NOTE_20260313.md`
   - `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_PACKAGE_MAP_20260313.md`
   - `architecture/COSMOCRAT_STAGE_E_REFERENCE_DEPLOYMENT_AND_PROOF_VIEW_20260313.md`
   - `architecture/COSMOCRAT_STAGE_E_PRODUCTIZATION_CLOSURE_NOTE_20260315.md`
   - `architecture/COSMOCRAT_STAGE_E_CANONICAL_ROLLOUT_NOTE_20260312.md`
2. Rollout-pack and kernel/client boundary foundations in the audit repo
   - `architecture/rollout_pack_v1/COSMOCRAT_REPO_TOPOLOGY_V1.md`
   - `architecture/rollout_pack_v1/COSMOCRAT_SYSTEM_DEFINITION_V1.md`
   - `COSMOCRAT_KERNEL_CONTRACT.md`
   - `COSMOCRAT_CLIENT_ADAPTER_CONTRACT_V1.md`
3. Local explanatory docs in this repo
4. Local workflow and integrity checks

## Start Here

For most work, start with:

- [`README.md`](README.md)
- [`docs/topology-boundary.md`](docs/topology-boundary.md)
- [`docs/reference-deployment-composition.md`](docs/reference-deployment-composition.md)
- [`docs/integration-composition.md`](docs/integration-composition.md)
- [`docs/proof-line.md`](docs/proof-line.md)
- [`docs/linked-supporting-inputs.md`](docs/linked-supporting-inputs.md)

## Local Working Surfaces

- [`docs/topology-boundary.md`](docs/topology-boundary.md): product and repo boundary explanation
- [`docs/reference-deployment-composition.md`](docs/reference-deployment-composition.md): reference deployment and composition explanation
- [`docs/integration-composition.md`](docs/integration-composition.md): integration reading of the reference posture
- [`docs/proof-line.md`](docs/proof-line.md): proof posture and receipt-line explanation
- [`docs/linked-supporting-inputs.md`](docs/linked-supporting-inputs.md): linked Stage C supporting inputs that remain outside owned content
- [`.github/workflows/`](.github/workflows): docs/integrity workflows

## Current Boundary Rules

This repo currently admits only:
- documentation-class topology narratives
- boundary maps
- deployment and composition explanation
- proof-line explanation
- linked supporting inputs that remain outside owned content
- supporting docs-integrity validation

This repo does not admit:
- runtime authority assets
- Docker or Kubernetes operational assets
- operator runbooks or recovery instructions
- policy-pack content
- sdk or contracts enactment
- memory-governance implementation
- repo migration or runtime migration authority
- Stage F runtime or business-stack work

## Supporting Input Rule

Treat linked Stage C supporting inputs carefully:

- the Stage C architecture companion is already admitted into owned
  reference-architectures content by canon
- the demo kit, receipt pack, and replay bundle remain linked frozen
  inputs only

Do not absorb additional Stage C assets by convenience.

## Editing Rules

- Keep diffs small.
- Prefer explanatory clarification and cross-reference updates over prose expansion.
- Do not add runnable deployment artifacts.
- Do not add Docker, Kubernetes, or operator content.
- Do not turn this repo into an implementation or runtime planning surface.
- If a change starts implying repo movement, runtime placement, or deploy-home authority, stop and re-check the Stage E reference-architectures notes.

## Validation

Before pushing:

1. run `git diff --check origin/main...HEAD`
2. run any docs-integrity checks already defined by the repo workflow
3. make sure the diff stays documentation-only

## Review Posture

- Boundary review, not redesign review.
- Exact file, exact scope drift, exact authority.
- If the change improves explanation without widening the repo boundary, say so directly.
- If a change needs runtime, deployment, policy, sdk, or migration authority, treat that as a reopen trigger rather than normal repo maintenance.
