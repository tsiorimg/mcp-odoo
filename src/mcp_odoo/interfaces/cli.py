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


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable logging")
def cli(verbose: bool) -> None:
    if verbose:
        configure_logging()


@cli.command()
@click.option("--url", required=True, envvar="ODOO_URL", help="Odoo URL", type=str)
@click.option("--version", "odoo_version", envvar="ODOO_VERSION", help="Force version (e.g. 17.0, 19.0)", type=str)
def version(url: str, odoo_version: Optional[str]) -> None:
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


@cli.command()
@common_conn_options
@click.option("--model", required=True, help="Odoo model (e.g. res.partner)", type=str)
@click.option("--domain", default="[]", show_default=True, help="JSON domain", type=str)
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


@cli.command()
@common_conn_options
@click.option("--model", required=True, help="Odoo model", type=str)
@click.option("--ids", required=True, help="Comma-separated IDs", type=str)
@click.option("--fields", help="JSON list of fields", type=str)
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


@cli.command()
@common_conn_options
@click.option("--model", required=True, help="Odoo model", type=str)
@click.option("--values", required=True, help='JSON dict of values', type=str)
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


@cli.command()
@common_conn_options
@click.option("--model", required=True, help="Odoo model", type=str)
@click.option("--ids", required=True, help="Comma-separated IDs", type=str)
@click.option("--values", required=True, help='JSON dict of values', type=str)
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


@cli.command()
@common_conn_options
@click.option("--model", required=True, help="Odoo model", type=str)
@click.option("--ids", required=True, help="Comma-separated IDs", type=str)
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


@cli.command()
@common_conn_options
@click.option("--model", required=True, help="Odoo model", type=str)
@click.option("--method", required=True, help="Method name", type=str)
@click.option("--args", default="[]", show_default=True, help="Positional args JSON", type=str)
@click.option("--kwargs", default="{}", show_default=True, help="Keyword args JSON", type=str)
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
