# API Reference (MCP Odoo)

## Core classes
- `MCPOdoo(url, database, api_key, user="admin", version=None, timeout=10.0, retry_attempts=3, retry_backoff=0.3)`
  - Auto-selects XML-RPC (<19) or JSON-2 (>=19) unless `version` is forced.
- `OdooConnector` interface implemented by:
  - `XMLRPCConnector` (Odoo 14–18)
  - `JSON2Connector` (Odoo 19+)

## Methods (unified)
- `search(model, domain) -> list[int]`
- `read(model, ids, fields=None) -> list[dict]`
- `search_read(model, domain, fields=None) -> list[dict]`
- `create(model, values: dict) -> int`
- `write(model, ids, values: dict) -> bool`
- `unlink(model, ids) -> bool`
- `fields_get(model, attributes=None) -> dict`
- `call_method(model, method, *args, **kwargs) -> Any`

## CLI commands
- `mcp-odoo version --url URL`
- `mcp-odoo search --url URL --database DB --api-key KEY --model MODEL --domain '[]'`
- `mcp-odoo read --url URL --database DB --api-key KEY --model MODEL --ids 1,2 --fields '["name"]'`
- `mcp-odoo create --url URL --database DB --api-key KEY --model MODEL --values '{"name":"X"}'`
- `mcp-odoo write --url URL --database DB --api-key KEY --model MODEL --ids 1 --values '{"phone":"+33"}'`
- `mcp-odoo unlink --url URL --database DB --api-key KEY --model MODEL --ids 1`
- `mcp-odoo call --url URL --database DB --api-key KEY --model MODEL --method METHOD --args '[]' --kwargs '{}'`
Common options: `--retry-attempts`, `--retry-backoff`.

## Configuration (env / .env)
- `ODOO_URL`, `ODOO_DATABASE`, `ODOO_USER`, `ODOO_API_KEY`
- Optional: `ODOO_VERSION`, `MCP_RETRY_ATTEMPTS`, `MCP_RETRY_BACKOFF`, `MCP_TIMEOUT`

## Error handling
- Exceptions: `AuthenticationError`, `ValidationError`, `NotFoundError`, `RateLimitError`, `ServerError`, `APIError`, `VersionDetectionError`.
- JSON-2 HTTP codes are mapped to these exceptions; XML-RPC Faults map to `APIError`.

## Retries
- Network-level retries with exponential backoff (default 3 attempts, 0.3s base) for XML-RPC/HTTP errors; functional errors are not retried.

## Caching
- `fields_get` responses cached (LRU 128 entries) per connector instance.
