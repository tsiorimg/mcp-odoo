# Getting Started

This guide shows how to install MCP Odoo locally and run it against Odoo 14–19 using either the CLI or the Python API.

## 1) Install

### Via Poetry (recommended for dev)
```bash
poetry install --with dev
poetry shell
```

### Via pip editable
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## 2) Configure environment
Create a `.env` (or export env vars) with your instance info:
```
ODOO_URL=http://localhost:8069
ODOO_DATABASE=mcp_test
ODOO_USER=admin
ODOO_API_KEY=<your_api_key_or_password>
# Optional overrides
ODOO_VERSION=17.0
MCP_RETRY_ATTEMPTS=3
MCP_RETRY_BACKOFF=0.3
```

## 3) Quick CLI usage
```bash
mcp-odoo version --url $ODOO_URL
mcp-odoo search --url $ODOO_URL --database $ODOO_DATABASE --api-key $ODOO_API_KEY --model res.partner --domain '[]'
mcp-odoo create --url $ODOO_URL --database $ODOO_DATABASE --api-key $ODOO_API_KEY --model res.partner --values '{"name":"CLI Contact"}'
mcp-odoo call --url $ODOO_URL --database $ODOO_DATABASE --api-key $ODOO_API_KEY --model res.partner --method search --kwargs '{"domain":[["is_company","=",true]]}'
```

Retry controls for flaky networks:
`--retry-attempts 3 --retry-backoff 0.3`

## 4) Python API
```python
from mcp_odoo.core.factory import MCPOdoo

mcp = MCPOdoo(
    url="http://localhost:8069",
    database="mcp_test",
    api_key="your_key",  # password works for XML-RPC
)
partner_id = mcp.create("res.partner", {"name": "SDK Contact"})
partner = mcp.read("res.partner", [partner_id], ["name"])[0]
```

## 5) Spin up local Odoo for tests
```bash
docker-compose -f docker/docker-compose.test.yml up -d odoo-14 db-14 odoo-17 db-17 odoo-19 db-19
./docker/scripts/wait-for-odoo.sh localhost:8069
```
For integration tests:
```bash
ODOO14_URL=http://localhost:8069 ODOO14_PASSWORD=admin \
ODOO17_URL=http://localhost:8070 ODOO17_PASSWORD=admin \
ODOO19_URL=http://localhost:8071 ODOO19_API_KEY=<api_key_19> \
pytest tests/integration -q
```

## 6) Typical production usage
- Use API keys (Bearer) for Odoo 19+.
- Prefer bot users; rotate keys every 90 days.
- Set timeouts and retry/backoff via env vars.

## Troubleshooting
- 404 on `/web/version`: older images may expose `/web/webclient/version_info` (auto-handled).
- 401 on JSON-2: ensure API key is valid and database header `X-Odoo-Database` matches.
- XML-RPC 500 during init: make sure the database exists (`odoo -d mcp_test -i base --stop-after-init`).
