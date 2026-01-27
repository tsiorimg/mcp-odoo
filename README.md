# MCP Odoo (Python)

Multi-API connector platform for Odoo 14–19 combining XML-RPC (14–18) and JSON-2 (19+), following the design in `plan-mcpOdoo.prompt.md`.

## Status
Core architecture and connectors implemented; integration tests green on 14/17/19.

## Installation rapide
```bash
poetry install --with dev
```

## Usage (aperçu)
```python
from mcp_odoo.core.factory import ConnectorFactory

connector = ConnectorFactory.create(url="https://mycompany.odoo.com", database="prod", api_key="xxx")
partners = connector.search("res.partner", [("is_company", "=", True)])
```

### CLI rapide
```bash
mcp-odoo version --url http://localhost:8069
mcp-odoo search --url http://localhost:8069 --database db --api-key KEY --model res.partner --domain '[]'
mcp-odoo read --url http://localhost:8069 --database db --api-key KEY --model res.partner --ids 1,2 --fields '["name","email"]'
mcp-odoo create --url http://localhost:8069 --database db --api-key KEY --model res.partner --values '{"name":"CLI Contact"}'
mcp-odoo write --url http://localhost:8069 --database db --api-key KEY --model res.partner --ids 1 --values '{"phone":"+33123456789"}'
mcp-odoo unlink --url http://localhost:8069 --database db --api-key KEY --model res.partner --ids 1
mcp-odoo call --url http://localhost:8069 --database db --api-key KEY --model res.partner --method search --args '[]' --kwargs '{"domain":[["is_company","=",true]]}'
```

Consultez `docs/` et `examples/` pour des guides complets (en construction).

## Remaining work
- Add CI workflow (GitHub Actions) for unit + integration (Docker) and optional perf.
- Register `integration` mark in pytest.ini.
- Enrich docs: production guide, REST/n8n examples, bulk operations.
- Implement n8n nodes and REST gateway (currently placeholders).
- Improve logging/metrics (durations, retry counts) and expand migration assistant.

## Install / Uninstall (CLI only)
Quick install that makes `mcp` available in your PATH (uses a local venv under `~/.local/share/mcp_odoo_venv`):
```bash
./install.sh
export PATH="$HOME/.local/bin:$PATH"  # if not already
mcp --help
```

Remove everything (shim + venv):
```bash
./uninstall.sh
```
