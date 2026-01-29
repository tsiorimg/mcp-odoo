#!/usr/bin/env bash
set -euo pipefail

PREFIX="${HOME}/.local"
VENV_DIR="${PREFIX}/share/mcp_odoo_venv"
BIN_DIR="${PREFIX}/bin"

rm -f "${BIN_DIR}/mcp_odoo"
rm -rf "${VENV_DIR}"

echo "Removed mcp_odoo CLI shim and virtualenv."
