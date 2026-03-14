# Reference Deployment and Composition

[Back to README](../README.md)

## Purpose

This page explains the current reference deployment and composition shape
for the Cosmocrat proof posture.

It is explanatory only. It does not serve as operational runtime
authority and it does not provide deployment instructions.

## Current Explanatory Baseline

The current clean reference baseline is the refreshed Azure VM proof
posture canonized in the K7 Phase B hardening refresh freeze.

That baseline is useful here because it shows:

- a deployable container proof posture exists
- the proof path is configuration-driven
- the hardened staged proof remains inside the governed boundary

Azure VM is the explanatory reference baseline in this surface. It is not
a durable-home decision or a runtime placement directive.

## Composition Layers

The reference deployment/composition story is easiest to read as four
layers:

1. **Governed boundary**
   - the kernel exposes the governed proof surfaces
   - the governed client interacts with the kernel through the fixed
     contract boundary
2. **Staged proof stack**
   - `kernel-postgres`
   - `kernel`
   - `auxo-postgres`
   - `mailpit`
   - `auxo-tech`
   - `proof-runner`
3. **Deployment posture**
   - built images only
   - internal-only network posture
   - fixed bootstrap order
   - exact receipt verification before side effects
4. **Reference explanation layer**
   - packaging descriptors
   - topology explanation
   - proof interpretation
   - linked supporting inputs

These layers are presented so a reader can understand the shape of the
reference posture without treating this repository as an operational
surface.

## Reference Environment Patterns

Merged canon currently supports three environment readings:

- **Phase A local proof**
  - establishes the first bounded container proof baseline
- **Phase B Azure staging proof**
  - shows the same governed path on a clean staged VM
- **Phase B hardening refresh**
  - strengthens the staged proof baseline with hardened image, config,
    and restart posture

For this repository, the active reference posture is the hardened Azure
baseline because it is the clearest current explanatory surface for
deployment and proof understanding.

## What This Page Does Not Do

This page does not:

- provide Docker Compose files
- provide Kubernetes manifests
- tell an operator how to run or recover the stack
- grant authority over runtime placement
- move any deployment assets out of audit canon

## Source

- [Stage E Reference Architectures Package Map](https://github.com/OrionArchitekton/orion-estate-audit/blob/main/architecture/COSMOCRAT_STAGE_E_REFERENCE_ARCHITECTURES_PACKAGE_MAP_20260313.md)
- [K7 Phase B Proof Freeze](https://github.com/OrionArchitekton/orion-estate-audit/blob/main/architecture/COSMOCRAT_K7_PHASE_B_PROOF_FREEZE_20260310.md)
- [K7 Phase B Hardening Refresh Freeze](https://github.com/OrionArchitekton/orion-estate-audit/blob/main/architecture/COSMOCRAT_K7_PHASE_B_HARDENING_REFRESH_FREEZE_20260311.md)
