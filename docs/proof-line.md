# Proof Line

[Back to README](../README.md)

## Purpose

This page explains the current Cosmocrat proof line in reader order.

It is a descriptive surface. It does not redefine kernel behavior, client
behavior, or receipt semantics.

## Reading Order

The proof line should be read in this sequence:

1. **K7 Phase A proof freeze**
   - fixes the first local deployed-boundary proof baseline
2. **K7 Phase B proof freeze**
   - shows the same governed send path on a fresh Azure staging VM
3. **K7 Phase B hardening refresh freeze**
   - strengthens the Azure proof posture without reopening kernel or
     client semantics

## Governed Client and Receipt Relationship

Merged canon fixes a narrow relationship between the governed client and
Chronicle receipt evidence:

1. the governed client proposes a mutation
2. the kernel evaluates policy and authority
3. the kernel returns `ALLOW`, `DENY`, or `DEFER`
4. the response includes durable receipt evidence directly or through the
   receipt query handle
5. the governed client executes only after valid authorization and exact
   receipt verification

Within the proof freezes, the only governed proof surfaces used are:

- `POST /decision`
- `GET /receipts/{id}`

This is why the proof line is about governed decisioning, durable receipt
evidence, replay safety, and fail-closed behavior rather than generic
workflow execution.

## Evidence Taxonomy

For this reference surface, use the same evidence taxonomy defined in
[integration-composition.md](./integration-composition.md#naming-rule):

- **Chronicle receipt-of-record** is the only proof-line authority
  surface.
- **Runtime wrapper receipt** is operational evidence only.
- **Run metadata, traces, and logs** are operational diagnostics only.
  They can support investigation, but they do not clear governance proof
  requirements by themselves.

This repo explains the Chronicle proof line only. It does not treat
runtime wrapper evidence as a substitute for receipt-of-record truth.

## What Each Frozen Phase Proves

### Phase A

Phase A fixes the first bounded local proof baseline:

- dedicated container stack
- built images instead of source bind mounts
- fixed bootstrap order
- exact receipt verification before external side effects

### Phase B

Phase B proves the same governed path on a fresh Azure Linux VM:

- same bounded stack shape
- internal-only network posture
- same governed proof surfaces
- staged proof of replay safety and fail-closed behavior

### Hardening Refresh

The hardening refresh keeps the same proof semantics while strengthening
the staged deployment posture:

- pinned image references
- validated config provenance
- minimal restart and health-check routine
- refreshed Azure artifact set as the current clean proof baseline

## Scenario Coverage

Across the merged proof line, the frozen scenario set includes:

- happy-path `ALLOW`
- replay-safe no-resend
- policy `DENY`
- policy `DEFER`
- authority-caused non-`ALLOW`
- kernel unavailable fail-closed
- receipt verification failure fail-closed

The consistent outcome is narrow and commercial:

- governance is durable
- receipt evidence is mandatory
- replay is controlled
- missing or invalid evidence halts side effects

## Source

Merged canon inputs from `OrionArchitekton/orion-estate-audit`:

- `architecture/COSMOCRAT_K7_PHASE_A_PROOF_FREEZE_20260310.md`
- `architecture/COSMOCRAT_K7_PHASE_B_PROOF_FREEZE_20260310.md`
- `architecture/COSMOCRAT_K7_PHASE_B_HARDENING_REFRESH_FREEZE_20260311.md`
- `COSMOCRAT_CLIENT_ADAPTER_CONTRACT_V1.md`
