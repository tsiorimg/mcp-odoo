"""Migration helper XML-RPC → JSON-2 (placeholder)."""

from __future__ import annotations


def suggest_migration_steps() -> list[str]:
    return [
        "Enable JSON-2 API on Odoo 19+ instances",
        "Generate dedicated API keys (bot user)",
        "Update MCP configuration with the new keys",
        "Gradually replace XML-RPC endpoints with JSON-2",
    ]
