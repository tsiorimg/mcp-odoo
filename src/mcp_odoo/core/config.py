"""MCP configuration via pydantic-settings."""

from __future__ import annotations

from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPConfig(BaseSettings):
    """Main MCP Odoo configuration, loaded from environment or .env files."""

    model_config = SettingsConfigDict(env_file=(".env", ".env.development", ".env.testing"))

    odoo_url: str
    odoo_database: str
    odoo_user: str = "admin"
    odoo_api_key: SecretStr
    odoo_version: Optional[str] = None  # Auto-detected if None
    timeout: float = 10.0
    retry_attempts: int = 3
    retry_backoff: float = 0.3

    def version_float(self) -> Optional[float]:
        if self.odoo_version is None:
            return None
        try:
            return float(self.odoo_version.split(".")[0] + "." + self.odoo_version.split(".")[1])
        except (IndexError, ValueError):
            return None
