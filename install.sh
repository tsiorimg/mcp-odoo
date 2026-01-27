#!/usr/bin/env bash
set -euo pipefail

# Lightweight installer for the mcp CLI (wrapper around mcp-odoo)
# Installs into ~/.local/share/mcp_odoo_venv and adds a shim ~/.local/bin/mcp

PREFIX="${HOME}/.local"
VENV_DIR="${PREFIX}/share/mcp_odoo_venv"
BIN_DIR="${PREFIX}/bin"

mkdir -p "${VENV_DIR}" "${BIN_DIR}"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install .

cat > "${BIN_DIR}/mcp" <<'EOF'
#!/usr/bin/env bash
VENV_DIR="${HOME}/.local/share/mcp_odoo_venv"
source "${VENV_DIR}/bin/activate"
exec mcp-odoo "$@"
EOF
chmod +x "${BIN_DIR}/mcp"

echo "Installed mcp CLI to ${BIN_DIR}/mcp"
echo "Ensure ${BIN_DIR} is in your PATH (e.g., export PATH=\"${BIN_DIR}:\$PATH\")"
