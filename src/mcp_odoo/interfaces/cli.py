"""CLI pour MCP Odoo – implémentation Click directe pour éviter les soucis Typer/Click."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv, find_dotenv

from mcp_odoo.core.factory import MCPOdoo, detect_odoo_version
from mcp_odoo.utils.logging import configure_logging


# Chargement .env (sans override des variables déjà présentes)
def _load_env(env_file: str | None = None) -> None:
    if env_file:
        load_dotenv(env_file, override=False)
        return
    found = find_dotenv(usecwd=True)
    if found:
        load_dotenv(found, override=False)
        return
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env, override=False)


_load_env(os.getenv("MCP_ENV_FILE"))


def _ensure_conn_params(url: str | None, database: str | None, secret: str | None) -> None:
    missing = [name for name, val in (("url", url), ("database", database), ("api_key/password", secret)) if not val]
    if missing:
        msg = "\n".join(
            [
                f"Missing required parameter(s): {', '.join(missing)}",
                "Provide them via options or env vars:",
                "  export ODOO_URL=http://localhost:8069",
                "  export ODOO_DATABASE=mcp_test",
                "  export ODOO_API_KEY=token        # pour 19+",
                "  export ODOO_PASSWORD=admin       # pour 14-18",
                "  export ODOO_USER=admin",
                "Examples:",
                "  mcp-odoo read --model res.partner --ids 1,2 --fields '[\"name\"]'",
                "  mcp-odoo search --model res.partner --domain '[['\"is_company\"', '=', true]]'",
            ]
        )
        raise click.UsageError(msg)


def _coerce_verify(val: str | None) -> bool | str:
    if val is None:
        return True
    v = val.strip().lower()
    if v in {"0", "false", "no", "off"}:
        return False
    return val


def _coerce_version(val: str | None) -> float | None:
    if not val:
        return None
    try:
        return float(val.split("+")[0])
    except ValueError:
        return None


@click.group(help=r"""MCP Odoo CLI - Multi-Connector Platform for Odoo (14-19)

Unified CLI tool for connecting to Odoo instances via XML-RPC (14-18) or JSON-2 API (19+).
Automatically detects Odoo version and uses the appropriate API.""")
@click.option("--verbose", "-v", is_flag=True, help="Enable detailed logging for troubleshooting")
def cli(verbose: bool) -> None:
    """MCP Odoo CLI - Multi-Connector Platform for Odoo."""
    if verbose:
        configure_logging()


@cli.command(help=r"""Detect Odoo instance version via /web/webclient/version_info endpoint.

Useful to verify connectivity and determine which API (XML-RPC vs JSON-2) will be used.

Examples:
  mcp_odoo version --url https://mycompany.odoo.com
  mcp_odoo version --url http://localhost:8069""")
@click.option("--url", required=True, envvar="ODOO_URL", 
              help="Odoo instance URL (e.g. https://mycompany.odoo.com or http://localhost:8069)", type=str)
@click.option("--version", "odoo_version", envvar="ODOO_VERSION", 
              help="Force version detection (e.g. 17.0, 19.0) - bypasses auto-detection", type=str)
def version(url: str, odoo_version: Optional[str]) -> None:
    """Detect and display Odoo instance version."""
    v = _coerce_version(odoo_version) or detect_odoo_version(url)
    click.echo(f"Detected Odoo version: {v}")


def common_conn_options(fn):
    fn = click.option("--retry-backoff", default=0.3, show_default=True, envvar="MCP_RETRY_BACKOFF", type=float)(
        fn
    )
    fn = click.option(
        "--retry-attempts", default=3, show_default=True, envvar="MCP_RETRY_ATTEMPTS", type=int
    )(fn)
    fn = click.option(
        "--ssl-verify",
        envvar="MCP_SSL_VERIFY",
        default=None,
        help="SSL verification (1/0 or true/false).",
        type=str,
    )(fn)
    fn = click.option(
        "--version",
        "odoo_version",
        envvar="ODOO_VERSION",
        help="Force Odoo version (e.g. 17.0, 19.0) if autodetect unavailable",
        type=str,
    )(fn)
    fn = click.option("--password", envvar="ODOO_PASSWORD", help="Odoo password (14-18)", type=str)(fn)
    fn = click.option("--api-key", envvar="ODOO_API_KEY", help="API key (19+ ou fallback)", type=str)(fn)
    fn = click.option("--user", envvar="ODOO_USER", help="Odoo user (pour password auth)", type=str, required=False)(fn)
    fn = click.option("--database", required=True, envvar="ODOO_DATABASE", help="Database", type=str)(fn)
    fn = click.option("--url", required=True, envvar="ODOO_URL", help="Odoo URL", type=str)(fn)
    return fn


@cli.command(help=r"""Search for record IDs in Odoo using domain filters.

Returns a list of record IDs matching the specified domain criteria.
Use this to find records before reading their data.

Examples:
  # Find all companies
  mcp_odoo search --model res.partner --domain '[["is_company", "=", true]]'

  # Find partners with specific name
  mcp_odoo search --model res.partner --domain '[["name", "ilike", "Acme"]]'

  # Find all active users
  mcp_odoo search --model res.users --domain '[["active", "=", true]]'""")
@common_conn_options
@click.option("--model", required=True, 
              help="Odoo model name (e.g. res.partner, res.users, sale.order)", type=str)
@click.option("--domain", default="[]", show_default=True, 
              help='Search domain as JSON list (e.g. \'[["field", "operator", "value"]]\'))', type=str)
def search(url, database, user, api_key, password, retry_attempts, retry_backoff, ssl_verify, odoo_version, model, domain):
    secret = password or api_key
    _ensure_conn_params(url, database, secret)
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        password=password,
        user=user,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        verify=_coerce_verify(ssl_verify),
        version=_coerce_version(odoo_version),
    )
    domain_list = json.loads(domain)
    ids = mcp.search(model, domain_list)
    click.echo(ids)


@cli.command(help=r"""Read and retrieve data from Odoo records.

Fetches field values from existing records using their IDs.
Returns detailed record data in JSON format.

Examples:
  # Read all fields from partner ID 1
  mcp_odoo read --model res.partner --ids 1

  # Read specific fields from multiple partners
  mcp_odoo read --model res.partner --ids 1,2,3 --fields '["name", "email", "phone"]'

  # Read product information
  mcp_odoo read --model product.product --ids 5 --fields '["name", "list_price", "qty_available"]'""")
@common_conn_options
@click.option("--model", required=True, 
              help="Odoo model name (e.g. res.partner, product.product, sale.order)", type=str)
@click.option("--ids", required=True, 
              help="Comma-separated record IDs to read (e.g. 1,2,3)", type=str)
@click.option("--fields", 
              help='JSON list of field names to retrieve (e.g. \'["name", "email"]\') - omit for all fields', type=str)
def read(url, database, user, api_key, password, retry_attempts, retry_backoff, ssl_verify, odoo_version, model, ids, fields):
    secret = password or api_key
    _ensure_conn_params(url, database, secret)
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        password=password,
        user=user,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        verify=_coerce_verify(ssl_verify),
        version=_coerce_version(odoo_version),
    )
    ids_list = [int(x) for x in ids.split(",") if x]
    fields_list = json.loads(fields) if fields else None
    records = mcp.read(model, ids_list, fields_list)
    click.echo(json.dumps(records, indent=2, ensure_ascii=False))


@cli.command(help=r"""Create new records in Odoo.

Creates a new record with the specified field values.
Returns the ID of the newly created record.

Examples:
  # Create a new company
  mcp_odoo create --model res.partner --values '{"name": "ACME Corp", "is_company": true}'

  # Create a new contact
  mcp_odoo create --model res.partner --values '{"name": "John Doe", "email": "john@example.com"}'

  # Create a product
  mcp_odoo create --model product.product --values '{"name": "My Product", "list_price": 99.99}'""")
@common_conn_options
@click.option("--model", required=True, 
              help="Odoo model name (e.g. res.partner, product.product)", type=str)
@click.option("--values", required=True, 
              help='JSON dictionary of field values (e.g. \'{"name": "Value", "field": "data"}\')', type=str)
def create(url, database, user, api_key, password, retry_attempts, retry_backoff, ssl_verify, odoo_version, model, values):
    secret = password or api_key
    _ensure_conn_params(url, database, secret)
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        password=password,
        user=user,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        verify=_coerce_verify(ssl_verify),
        version=_coerce_version(odoo_version),
    )
    vals = json.loads(values)
    record_id = mcp.create(model, vals)
    click.echo(record_id)


@cli.command(help=r"""Update existing Odoo records.

Modifies field values of existing records using their IDs.
Returns True if the update was successful.

Examples:
  # Update partner email
  mcp_odoo write --model res.partner --ids 1 --values '{"email": "new@example.com"}'

  # Update multiple partners
  mcp_odoo write --model res.partner --ids 1,2,3 --values '{"phone": "+1234567890"}'

  # Update product price
  mcp_odoo write --model product.product --ids 5 --values '{"list_price": 149.99}'""")
@common_conn_options
@click.option("--model", required=True, 
              help="Odoo model name (e.g. res.partner, product.product)", type=str)
@click.option("--ids", required=True, 
              help="Comma-separated record IDs to update (e.g. 1,2,3)", type=str)
@click.option("--values", required=True, 
              help='JSON dictionary of field values to update (e.g. \'{"field": "new_value"}\')', type=str)
def write(url, database, user, api_key, password, retry_attempts, retry_backoff, ssl_verify, odoo_version, model, ids, values):
    secret = password or api_key
    _ensure_conn_params(url, database, secret)
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        password=password,
        user=user,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        verify=_coerce_verify(ssl_verify),
        version=_coerce_version(odoo_version),
    )
    ids_list = [int(x) for x in ids.split(",") if x]
    vals = json.loads(values)
    ok = mcp.write(model, ids_list, vals)
    click.echo(ok)


@cli.command(help=r"""Delete records from Odoo.

Permanently removes records from the database using their IDs.
⚠️  WARNING: This action cannot be undone!
Returns True if the deletion was successful.

Examples:
  # Delete a single partner (be careful!)
  mcp_odoo unlink --model res.partner --ids 999

  # Delete multiple test records
  mcp_odoo unlink --model product.product --ids 100,101,102

  # Delete a draft sale order
  mcp_odoo unlink --model sale.order --ids 45""")
@common_conn_options
@click.option("--model", required=True, 
              help="Odoo model name (e.g. res.partner, sale.order)", type=str)
@click.option("--ids", required=True, 
              help="Comma-separated record IDs to delete (e.g. 1,2,3) - ⚠️ PERMANENT DELETION", type=str)
def unlink(url, database, user, api_key, password, retry_attempts, retry_backoff, ssl_verify, odoo_version, model, ids):
    secret = password or api_key
    _ensure_conn_params(url, database, secret)
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        password=password,
        user=user,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        verify=_coerce_verify(ssl_verify),
        version=_coerce_version(odoo_version),
    )
    ids_list = [int(x) for x in ids.split(",") if x]
    ok = mcp.unlink(model, ids_list)
    click.echo(ok)


@cli.command(help=r"""Call custom methods on Odoo models.

Executes public methods available on Odoo models with custom arguments.
Useful for advanced operations, workflows, and custom business logic.

Examples:
  # Call action_confirm on sale order
  mcp_odoo call --model sale.order --method action_confirm --args '[123]'

  # Get default values for a model
  mcp_odoo call --model res.partner --method default_get --args '[["name", "email"]]'

  # Call method with keyword arguments
  mcp_odoo call --model account.move --method post --kwargs '{"soft": false}'""")
@common_conn_options
@click.option("--model", required=True, 
              help="Odoo model name (e.g. sale.order, account.move)", type=str)
@click.option("--method", required=True, 
              help="Method name to call on the model (e.g. action_confirm, default_get)", type=str)
@click.option("--args", default="[]", show_default=True, 
              help='Positional arguments as JSON list (e.g. \'[123, "value"]\')', type=str)
@click.option("--kwargs", default="{}", show_default=True, 
              help='Keyword arguments as JSON dict (e.g. \'{"param": "value", "flag": true}\')', type=str)
def call(url, database, user, api_key, password, retry_attempts, retry_backoff, ssl_verify, odoo_version, model, method, args, kwargs):
    secret = password or api_key
    _ensure_conn_params(url, database, secret)
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        password=password,
        user=user,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        verify=_coerce_verify(ssl_verify),
        version=_coerce_version(odoo_version),
    )
    args_list = json.loads(args or "[]")
    kwargs_dict = json.loads(kwargs or "{}")
    result = mcp.call_method(model, method, *args_list, **kwargs_dict)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


def app():
    cli()


if __name__ == "__main__":
    app()
