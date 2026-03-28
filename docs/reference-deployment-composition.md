# Reference Deployment and Composition

[Back to README](../README.md)

## Purpose

This page explains the current reference deployment and composition shape
for the Cosmocrat estate.

It is explanatory only. It does not serve as operational runtime
authority and it does not provide deployment instructions.

## Current Reader Rule

Read this page when you need the current answer to:

- where the deploy/reference composition story lives now
- which repo owns the actual operational stack
- how kernel, runtime, infra, and a business lane relate in the current
  canon
- what is executable now versus still local, bootstrap, or later-stage
  work

If you need the actual operational/package surfaces, the current home is
`orion-infra`, not this repository.

## Current Composition Roles

The current reference composition story is easiest to read as four
named roles:

<table>
  <thead>
    <tr>
      <th>Role</th>
      <th>Current repo home</th>
      <th>Current posture</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Governance plane</td>
      <td><code>cosmocrat-kernel</code></td>
      <td>Admitted service in shared stack</td>
    </tr>
    <tr>
      <td>Thin execution substrate</td>
      <td><code>orion-runtime</code></td>
      <td>Boundary-only; not infra rollout</td>
    </tr>
    <tr>
      <td>Shared deployment and ops root</td>
      <td><code>orion-infra</code></td>
      <td>Ops root for stores + kernel</td>
    </tr>
    <tr>
      <td>Business lane consumer position</td>
      <td>lane-owned business repo</td>
      <td>Unbound consumer</td>
    </tr>
  </tbody>
</table>

This page explains that shape. It does not make any of those repos
change ownership.

## Current Operator Reading Path

The current low-risk reading path is:

1. start here for the explanatory composition view
2. then read `orion-infra/README.md` for the shared deploy/ops boundary
3. then read `orion-infra/docs/CANONICAL_EXECUTABLE_COMPOSITION.md`
4. then inspect
   `orion-infra/deploy/cosmocrat/compose/canonical-stack.compose.yml`

Those are the current operational/package sources. This repository
remains the explanation layer only.

## Current Executable Posture

The current canonical executable composition root lives in
`orion-infra/deploy/cosmocrat/compose/canonical-stack.compose.yml`.

That stack currently renders:

- shared stores from the infra-owned bootstrap slice
  - Postgres
  - Redis
  - MinIO
  - ClickHouse
- one `cosmocrat-kernel` service bound through the existing kernel
  container contract

The same compose root explicitly keeps two other positions unbound:

- `orion-runtime` remains a `contract_slot_only`
- the lane position remains `not_yet_bound`

This is the key current-state point: the shared stack is real, but it is
not yet a runtime-plus-lane deployment surface.

## Local Bootstrap Versus Later Staged Deployment

Current canon separates three readings:

- **Executable now in the shared stack**
  - infra-owned shared stores
  - one kernel service
- **Local or bootstrap consumer posture now**
  - runtime adoption remains thin and caller-supplied
  - lane behavior remains lane-owned and may be proven or run in its own
    bounded surface
- **Later staged deployment expectation**
  - runtime or lane participation may be admitted later, but only after
    canon explicitly binds them into an operational home

This page should therefore be read as:

- current operator explanation now
- explicit slot posture now
- future staged admission later

It should not be read as evidence that runtime or a lane already deploys
through `orion-infra` by default.

## Business Lane Role

The March 27 audit controller requires this artifact to name one
business-lane role. The current role is:

- a lane-owned consumer position that receives or produces business
  workflow truth outside shared infra layers

The current compose root names a lane slot and leaves it unbound. That is
the correct current explanation. A business lane still exists in the
topology, but it is not admitted here as a default executable consumer in
this pass.

## What This Page Does Not Do

This page does not:

- provide Docker Compose files or Kubernetes manifests
- tell an operator how to run, recover, or promote the stack
- grant authority over runtime placement
- bind a runtime or lane into the current shared stack by implication
- move any deployment assets out of `orion-infra`

## Source

Current explanatory canon for this page is grounded in:

- the March 27 estate action plan `P05`
- `orion-infra/README.md`
- `orion-infra/docs/CANONICAL_EXECUTABLE_COMPOSITION.md`
- `orion-infra/deploy/cosmocrat/compose/canonical-stack.compose.yml`

Those sources define the current deploy/reference explanation without
turning this repository into an operational deployment home.
