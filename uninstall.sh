#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local"
VENV_DIR="${PREFIX}/share/mcp_odoo_venv"
BIN_DIR="${PREFIX}/bin"

rm -f "${BIN_DIR}/mcp"
rm -rf "${VENV_DIR}"

echo "Removed mcp CLI shim and virtualenv."
