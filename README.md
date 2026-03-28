# Cosmocrat Reference Architectures

Agent and reviewer navigation guide: [AGENTS.md](AGENTS.md)

This repository is the docs-only reference surface for Cosmocrat's
`cosmocrat-reference-architectures` lane.

It exists to help a reader understand:

- the product boundary around the Cosmocrat kernel
- the current default deploy/reference composition reading path
- the proof line from governed decision to durable receipt evidence
- the linked Stage C supporting inputs that remain outside owned
  reference-architectures content

## Reading Order

1. [Topology and Boundary](./docs/topology-boundary.md)
2. [Reference Deployment and Composition](./docs/reference-deployment-composition.md)
   - start here for the current deploy/reference explanation, then follow
     the named `orion-infra` operational sources from that page
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
composition root still lives in `orion-infra`.

It does not authorize or contain:

- runtime authority assets
- Docker or Kubernetes operational assets
- policy packs
- SDK or contracts enactment
- memory-governance implementation
- repo migration
- Stage F runtime or business-stack work

## Authority

This working surface is derived from merged canon on the private audit
repo `OrionArchitekton/orion-estate-audit`, especially:

- `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_NOTE_20260313.md`
- `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_EXECUTION_BRIEF_20260313.md`
- `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_PACKAGE_MAP_20260313.md`
- `architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_ENTRYPOINT_20260313.md`
