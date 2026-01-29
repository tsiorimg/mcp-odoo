#!/usr/bin/env bash
set -euo pipefail

# Lightweight installer for the mcp CLI (wrapper around mcp-odoo)
# Installs into ~/.local/share/mcp_odoo_venv and adds a shim ~/.local/bin/mcp

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: install.sh [--version <git_ref>]

Examples:
  ./scripts/install.sh                # install from current checkout (when run inside repo)
  curl -fsSL https://raw.githubusercontent.com/tsiorimg/mcp-odoo/main/scripts/install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/tsiorimg/mcp-odoo/main/scripts/install.sh | bash -s -- --version v1.2.3
USAGE
}

REF="main"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version|--ref)
      REF="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

PREFIX="${HOME}/.local"
VENV_DIR="${PREFIX}/share/mcp_odoo_venv"
BIN_DIR="${PREFIX}/bin"
REPO_URL="https://github.com/tsiorimg/mcp-odoo.git"

mkdir -p "${VENV_DIR}" "${BIN_DIR}"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip

if [[ -f "pyproject.toml" && -d "src/mcp_odoo" ]]; then
  echo "📦 Installing mcp-odoo from local checkout"
  pip install .
else
  echo "🌐 Installing mcp-odoo from GitHub (${REF})"
  pip install "git+${REPO_URL}@${REF}"
fi

cat > "${BIN_DIR}/mcp_odoo" <<'EOF'
#!/usr/bin/env bash
VENV_DIR="${HOME}/.local/share/mcp_odoo_venv"
source "${VENV_DIR}/bin/activate"
exec mcp-odoo "$@"
EOF
chmod +x "${BIN_DIR}/mcp_odoo"

echo "Installed mcp_odoo CLI to ${BIN_DIR}/mcp_odoo"
echo "Ensure ${BIN_DIR} is in your PATH (e.g., export PATH=\"${BIN_DIR}:\$PATH\")"
