# Integration Composition

[Back to README](../README.md)

## Purpose

This page explains how the governed integration seams connect inside the
reference deployment composition. It ties together the SDK contract, auth
resolver, policy evaluation, Chronicle persistence, and authority
validation into a single readable flow.

It is explanatory only. It does not provide deployment instructions,
executable scripts, or runtime authority.

For the current deploy/reference explanation and operational-home
reading path, start with
[Reference Deployment and Composition](./reference-deployment-composition.md).
This page is about governed seam behavior, not deploy-home ownership.

## Naming Rule

This page uses the following evidence terms deliberately:

- **Chronicle receipt-of-record** refers to the authoritative receipt in
  Chronicle in the kernel. In the `POST /decision` response, the inline
  `receipt` object is a Chronicle receipt-of-record reference only. The
  authoritative receipt is resolved through `GET /receipts/{id}`.
- **Runtime wrapper receipt** refers to any runtime-local operational
  wrapper evidence outside this reference deployment contract.
- **Run metadata, traces, and logs** refers to execution diagnostics only.

Only the Chronicle receipt-of-record clears the governed proof line on
this page.

## Boot Order

The reference deployment baseline follows a fixed bootstrap sequence:

1. **Chronicle database** — Postgres with the Chronicle receipt schema
   must be running and reachable before the kernel can persist decisions.
2. **Kernel** — starts fail-closed. `/health` returns `200` immediately
   (liveness only). `/ready` returns non-`200` status until all runtime
   seams are wired.
3. **Auth resolver wiring** — the host process installs a transport auth
   resolver into `app.state.auth_resolver`. Without this, `/decision`
   returns `503 auth_resolver_unavailable`.
4. **Policy file** — the kernel reads a compiled policy YAML from the
   path in `COSMOCRAT_CORE_POLICY_PATH`. A missing or unreadable policy
   does not prevent startup but causes `DEFER` responses with Chronicle
   receipt-of-record evidence and `POLICY_UNAVAILABLE`.
5. **Governed client** — connects to the kernel only after `/ready`
   returns HTTP `200`. Sends `POST /decision` with the SDK request
   contract.

Authority configuration (`COSMOCRAT_CORE_AUTHORITY_*` env vars) is
optional. Missing authority does not block `/ready`. It can cause policy
`ALLOW` results to be downgraded to governed `DEFER` or `DENY` at
runtime.

## Dependency Map

```text
governed client
    │
    ▼
kernel (/decision, /receipts/{id})
    │         │          │              │
    ▼         ▼          ▼              ▼
auth      Chronicle   policy file   authority config
resolver  (Postgres)  (YAML)        (optional)
```

The kernel is the only governed surface the client talks to. All four
kernel-internal dependencies are independent: the auth resolver handles
transport identity, Chronicle persists decisions and receipts, the policy
file drives deterministic evaluation, and authority config (when present)
validates per-request authorization tokens. The governed client does not
directly access any of them.

The runtime is not part of this authoritative receipt chain. If runtime
wrapper evidence exists around this flow, it is operational only and does
not replace the Chronicle receipt-of-record.

## Environment Configuration

The kernel reads configuration from environment variables with the
`COSMOCRAT_CORE_` prefix. The key groups are:

**Core settings:**

- `COSMOCRAT_CORE_ENVIRONMENT` — deployment environment name
- `COSMOCRAT_CORE_HOST` — bind host (default `0.0.0.0`)
- `COSMOCRAT_CORE_PORT` — bind port (default `8080`)
- `COSMOCRAT_CORE_PUBLIC_BASE_URL` — if set, receipt `query_ref` is
  expanded from relative `/receipts/{id}` to absolute
  `{base_url}/receipts/{id}`

**Chronicle settings:**

- `COSMOCRAT_CORE_CHRONICLE_BACKEND` — `postgres` or `sqlite`
- `COSMOCRAT_CORE_CHRONICLE_POSTGRES_DSN` — Postgres connection string
- `COSMOCRAT_CORE_CHRONICLE_SQLITE_PATH` — local path (test/dev only)
- `COSMOCRAT_CORE_RECEIPT_SIGNING_SECRET` — signing key for receipt
  HMAC integrity
- `COSMOCRAT_CORE_RECEIPT_SIGNING_KEY_ID` — key identifier in receipts

**Policy settings:**

- `COSMOCRAT_CORE_POLICY_PATH` — filesystem path to compiled policy YAML

**Authority settings (optional):**

- `COSMOCRAT_CORE_AUTHORITY_ACTIVE_SECRET` — signing key for authority
  token validation
- `COSMOCRAT_CORE_AUTHORITY_PREVIOUS_SECRET` — previous key for rotation
- `COSMOCRAT_CORE_AUTHORITY_ISSUER` — optional issuer constraint
- `COSMOCRAT_CORE_AUTHORITY_AUDIENCE` — optional audience constraint

For the full auth resolver integration pattern, see
[auth_resolver_integration.md](https://github.com/OrionArchitekton/cosmocrat-kernel/blob/main/runbooks/auth_resolver_integration.md)
in the kernel repo.

## Request and Response Contract

The governed client sends requests and receives responses matching the
contract defined in
[cosmocrat-sdk](https://github.com/OrionArchitekton/cosmocrat-sdk).

**Request shape** (from `schemas/request.schema.json`):

- `request_id` — caller-assigned identifier
- `idempotency_key` — stable key for safe retries (must also be sent as
  the `Idempotency-Key` header)
- `requested_at` — ISO 8601 timestamp
- `client` — `client_id` and `client_version`
- `actor` — `actor_id`, `actor_type`, optional `session_id`
- `action` — `action_type`, `action_category`, `mutation_kind`
- `resource` — `resource_type`, optional `resource_id`, `resource_scope`
- `context` — `tenant_id`, `lane`, `purpose`, `policy_context`,
  `authority_context`, `evidence_refs`

**Response shape** (from `schemas/response.schema.json`):

- `decision` — `ALLOW`, `DENY`, or `DEFER`
- `decision_id` — kernel-assigned identifier
- `reason_code` and `rationale` — why the decision was made
- `policy_ref` — `policy_pack_id`, `policy_version`, optional
  `policy_hash`
- `authority_ref` — `authority_status`, optional `authority_token_id`
- `receipt` — `receipt_id`, `query_ref`, `written_at`
- `retry_after_ms` — backoff hint for `DEFER` decisions

The governed client must fail closed when the response is missing a
`decision` field or a durable `receipt.query_ref`.

In this contract, the inline `receipt` object is a Chronicle
receipt-of-record reference, not a runtime wrapper receipt.

## Governed Decision Flow

The reference deployment proves this sequence:

1. **Client sends** `POST /decision` with bearer token, `idempotency_key`,
   and SDK request body.
2. **Kernel extracts** bearer token from `Authorization` header.
3. **Kernel extracts** `Idempotency-Key` from request header.
4. **Body validation** — parses and validates the request body against the
   Pydantic contract. A malformed body fails here with `422
   contract_validation_failed` before any principal resolution.
5. **Idempotency check** — verifies the `Idempotency-Key` header matches
   `body.idempotency_key`. Mismatch returns `422 idempotency_mismatch`.
6. **Auth resolver** — maps the bearer token to an `ApiCallerPrincipal`
   with `subject_id`, `client_id`, and scopes.
7. **Transport gate** — verifies `decision:write` scope and non-null
   `client_id`.
8. **Chronicle persist/replay** — if the `idempotency_key` was seen
   before with the same logical request, the stored decision and receipt
   are replayed without re-evaluation. Otherwise, decision evaluation
   runs inside the persist path:
   - **Policy evaluation** — deterministic rule matching against the
     compiled policy YAML. Produces `ALLOW`, `DENY`, or `DEFER`.
   - **Authority composition** (if configured) — validates authority
     tokens from `context.authority_context`. Can make policy `ALLOW`
     terminal, downgrade to governed `DEFER`, or override to `DENY` on
     semantic mismatch.
   - **Chronicle commit** — the decision and Chronicle receipt-of-record
     are committed before the response is returned.
9. **Client receives** the decision response with inline Chronicle
   receipt-of-record reference. The client can query
   `GET /receipts/{id}` for the full authoritative receipt.
10. **Client decides** whether to execute. `ALLOW` permits execution.
    `DENY` and `DEFER` do not.

## Fail-Closed Posture

The reference deployment demonstrates fail-closed behavior at every
layer:

- **No auth resolver** → `503 auth_resolver_unavailable`
- **No Chronicle** → `503 chronicle_unavailable`
- **Invalid bearer token** → `401 authentication_invalid`
- **Missing scope or client** → `403 access_denied`
- **Bad request body** → `422 contract_validation_failed`
- **No matching policy rule** → `DENY` with Chronicle receipt-of-record
- **Unavailable policy file** → `DEFER` with Chronicle receipt-of-record
  and `POLICY_UNAVAILABLE`
- **Authority semantic mismatch** → `DENY`
- **Missing authority config** → governed `DEFER` (for policy `ALLOW`
  results that need authority)
- **Kernel transport failure** → governed client fails closed (no
  execution)
- **Receipt verification failure** → governed client fails closed (no
  execution)

In every case, the default is non-execution. Execution requires an
explicit `ALLOW` with a valid receipt.

## Proof Scenario Mapping

The seven frozen proof scenarios map to this flow:

| Scenario | Decision | Receipt | Side effect |
| --- | --- | --- | --- |
| happy path | `ALLOW` | issued | executed |
| replay no-resend | `ALLOW` (replayed) | same receipt | not re-executed |
| policy deny | `DENY` | issued | not executed |
| policy defer | `DEFER` | issued | not executed |
| authority defer | `DEFER` | issued | not executed |
| kernel unavailable | — | — | fail-closed |
| receipt verification failure | — | — | fail-closed |

For the full proof line reading order, see
[proof-line.md](./proof-line.md).

## What This Page Does Not Do

This page does not:

- provide Docker Compose files or Kubernetes manifests
- tell an operator how to run or recover the stack
- grant authority over runtime placement
- define the durable-home deployment target
- move any deployment assets out of audit canon

## Source

Merged canon inputs:

- [cosmocrat-kernel runbooks](https://github.com/OrionArchitekton/cosmocrat-kernel/tree/main/runbooks)
- [cosmocrat-sdk schemas](https://github.com/OrionArchitekton/cosmocrat-sdk/tree/main/schemas)
- `OrionArchitekton/orion-estate-audit` architecture freeze notes
