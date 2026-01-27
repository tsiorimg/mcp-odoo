# Migration Guide: XML-RPC → JSON-2 (Odoo 19+)

JSON-2 is the new external API starting in Odoo 19 and will replace XML-RPC by Odoo 20. This guide helps you move safely.

## 1) Detect and plan
- Use `/web/version` to detect the major version.
- If `>=19`, prefer JSON-2; keep XML-RPC fallback only for legacy.

## 2) Credentials
- Generate API keys (Bearer) for integration/bot users.
- Rotate keys every 90 days; store in secret manager.

## 3) Endpoint mapping
| Action          | XML-RPC                               | JSON-2                                 |
|-----------------|---------------------------------------|----------------------------------------|
| search          | `execute_kw(..., 'search', [domain])` | `POST /json/2/<model>/search`          |
| read            | `execute_kw(..., 'read', [ids])`      | `POST /json/2/<model>/read`            |
| search_read     | `execute_kw(..., 'search_read', ...)` | `POST /json/2/<model>/search_read`     |
| create          | `execute_kw(..., 'create', [vals])`   | `POST /json/2/<model>/create` (`vals_list`) |
| write           | `execute_kw(..., 'write', [ids, vals])` | `POST /json/2/<model>/write` (`ids`, `vals`) |
| unlink          | `execute_kw(..., 'unlink', [ids])`    | `POST /json/2/<model>/unlink` (`ids`)  |

## 4) Request/response differences
- JSON-2 is HTTP+JSON; one transaction per request.
- Errors are HTTP-coded (400/401/404/422/429/5xx) instead of XML-RPC Faults.
- For `create`, send `{"vals_list": [ {...} ]}`.
- Include headers: `Authorization: bearer <key>`, `X-Odoo-Database: <db>`, `Content-Type: application/json`.

## 5) Migration steps
1. **Dual-stack**: keep XML-RPC code but route 19+ to JSON-2 via factory.
2. **Credential switch**: replace passwords by API keys where possible.
3. **Payload adjustments**: adapt create/write payloads (`vals_list`, `vals`).
4. **Error handling**: map HTTP codes; add retries/backoff for network faults only.
5. **Rollout**: enable per-model or per-environment; monitor logs.
6. **Decommission**: remove XML-RPC once all targets are 19+ or 20.

## 6) Performance tips
- Cache `fields_get` (already built-in).
- Batch creates with `vals_list` to reduce round-trips.
- Keep payloads small; JSON-2 uses single-transaction per call.

## 7) Testing
- Unit: mock HTTP with `respx`, ensure correct payloads and error mapping.
- Integration: run Docker 19 service and validate CRUD + custom calls.
- Perf: benchmark search/read vs XML-RPC for your datasets.

## 8) Checklist
- [ ] API keys provisioned and rotated
- [ ] JSON-2 headers set
- [ ] `create` uses `vals_list`
- [ ] Error mapping validated (400/401/404/422/429/5xx)
- [ ] Logs capture retries and durations
- [ ] Integration tests green on 19+
