"""Typer-based CLI for MCP Odoo."""

from __future__ import annotations

import json
from typing import Optional

import typer

from mcp_odoo.core.factory import MCPOdoo, detect_odoo_version
from mcp_odoo.utils.logging import configure_logging

app = typer.Typer(help="CLI MCP Odoo (XML-RPC & JSON-2)")


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable logging")):
    if verbose:
        configure_logging()


@app.command()
def version(url: str = typer.Option(..., help="Odoo URL")):
    v = detect_odoo_version(url)
    typer.echo(f"Detected Odoo version: {v}")


@app.command()
def search(
    url: str = typer.Option(..., help="Odoo URL"),
    database: str = typer.Option(..., help="Database"),
    api_key: str = typer.Option(..., help="API key"),
    model: str = typer.Option(..., help="Odoo model (e.g. res.partner)"),
    domain: Optional[str] = typer.Option("[]", help="JSON domain, e.g. [[\"is_company\", '=', True]]"),
    retry_attempts: int = typer.Option(3, help="Retry attempts on network errors"),
    retry_backoff: float = typer.Option(0.3, help="Initial backoff in seconds"),
):
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
    )
    domain_list = json.loads(domain)
    ids = mcp.search(model, domain_list)
    typer.echo(ids)


@app.command()
def read(
    url: str = typer.Option(..., help="Odoo URL"),
    database: str = typer.Option(..., help="Database"),
    api_key: str = typer.Option(..., help="API key"),
    model: str = typer.Option(..., help="Odoo model"),
    ids: str = typer.Option(..., help="Comma-separated IDs"),
    fields: Optional[str] = typer.Option(None, help="JSON list of fields"),
    retry_attempts: int = typer.Option(3, help="Retry attempts on network errors"),
    retry_backoff: float = typer.Option(0.3, help="Initial backoff in seconds"),
):
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
    )
    ids_list = [int(x) for x in ids.split(",") if x]
    fields_list = json.loads(fields) if fields else None
    records = mcp.read(model, ids_list, fields_list)
    typer.echo(json.dumps(records, indent=2, ensure_ascii=False))


@app.command()
def create(
    url: str = typer.Option(..., help="Odoo URL"),
    database: str = typer.Option(..., help="Database"),
    api_key: str = typer.Option(..., help="API key"),
    model: str = typer.Option(..., help="Odoo model"),
    values: str = typer.Option(..., help='JSON dict of values, e.g. "{\\"name\\\":\\"Test\\"}"'),
    retry_attempts: int = typer.Option(3, help="Retry attempts on network errors"),
    retry_backoff: float = typer.Option(0.3, help="Initial backoff in seconds"),
):
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
    )
    vals = json.loads(values)
    record_id = mcp.create(model, vals)
    typer.echo(record_id)


@app.command()
def write(
    url: str = typer.Option(..., help="Odoo URL"),
    database: str = typer.Option(..., help="Database"),
    api_key: str = typer.Option(..., help="API key"),
    model: str = typer.Option(..., help="Odoo model"),
    ids: str = typer.Option(..., help="Comma-separated IDs"),
    values: str = typer.Option(..., help='JSON dict of values, e.g. "{\\"name\\\":\\"New\\"}"'),
    retry_attempts: int = typer.Option(3, help="Retry attempts on network errors"),
    retry_backoff: float = typer.Option(0.3, help="Initial backoff in seconds"),
):
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
    )
    ids_list = [int(x) for x in ids.split(",") if x]
    vals = json.loads(values)
    ok = mcp.write(model, ids_list, vals)
    typer.echo(ok)


@app.command()
def unlink(
    url: str = typer.Option(..., help="Odoo URL"),
    database: str = typer.Option(..., help="Database"),
    api_key: str = typer.Option(..., help="API key"),
    model: str = typer.Option(..., help="Odoo model"),
    ids: str = typer.Option(..., help="Comma-separated IDs"),
    retry_attempts: int = typer.Option(3, help="Retry attempts on network errors"),
    retry_backoff: float = typer.Option(0.3, help="Initial backoff in seconds"),
):
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
    )
    ids_list = [int(x) for x in ids.split(",") if x]
    ok = mcp.unlink(model, ids_list)
    typer.echo(ok)


@app.command()
def call(
    url: str = typer.Option(..., help="Odoo URL"),
    database: str = typer.Option(..., help="Database"),
    api_key: str = typer.Option(..., help="API key"),
    model: str = typer.Option(..., help="Odoo model"),
    method: str = typer.Option(..., help="Method name"),
    args: Optional[str] = typer.Option("[]", help="Positional args JSON, e.g. [1,2]"),
    kwargs: Optional[str] = typer.Option("{}", help="Keyword args JSON, e.g. {\"context\":{}}"),
    retry_attempts: int = typer.Option(3, help="Retry attempts on network errors"),
    retry_backoff: float = typer.Option(0.3, help="Initial backoff in seconds"),
):
    mcp = MCPOdoo(
        url=url,
        database=database,
        api_key=api_key,
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
    )
    args_list = json.loads(args or "[]")
    kwargs_dict = json.loads(kwargs or "{}")
    result = mcp.call_method(model, method, *args_list, **kwargs_dict)
    typer.echo(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
