#!/usr/bin/env bash
# Standalone update script for mcp-odoo
# Usage: curl -sSL https://raw.githubusercontent.com/tsiorimg/mcp-odoo/main/scripts/update.sh | bash

set -euo pipefail

VENV_DIR="${HOME}/.local/share/mcp_odoo_venv"
BIN_DIR="${HOME}/.local/bin"

echo "🔄 mcp-odoo Update Script"
echo "=========================="

# Check if mcp-odoo is installed
if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ mcp-odoo not found. Installing fresh..."
    curl -sSL https://raw.githubusercontent.com/tsiorimg/mcp-odoo/main/scripts/install.sh | bash
    exit 0
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Get current version
CURRENT_VERSION=$(python -c 'import mcp_odoo; print(mcp_odoo.__version__)' 2>/dev/null || echo 'unknown')
echo "📍 Current version: $CURRENT_VERSION"

# Try update methods in order of preference
echo "🔄 Checking for updates..."

# Method 1: PyPI (when published)
if pip install mcp-odoo --upgrade --quiet 2>/dev/null; then
    NEW_VERSION=$(python -c 'import mcp_odoo; print(mcp_odoo.__version__)' 2>/dev/null || echo 'unknown')
    if [[ "$NEW_VERSION" != "$CURRENT_VERSION" ]]; then
        echo "✅ Updated from PyPI: $CURRENT_VERSION → $NEW_VERSION"
    else
        echo "ℹ️  Already up-to-date from PyPI"
    fi
# Method 2: GitHub (development)
elif pip install git+https://github.com/tsiorimg/mcp-odoo.git --upgrade --force-reinstall --quiet 2>/dev/null; then
    NEW_VERSION=$(python -c 'import mcp_odoo; print(mcp_odoo.__version__)' 2>/dev/null || echo 'dev')
    echo "✅ Updated from GitHub: $CURRENT_VERSION → $NEW_VERSION"
else
    echo "❌ Update failed. Please check:"
    echo "   • Internet connection"
    echo "   • Repository access"
    echo "   • Virtual environment integrity"
    exit 1
fi

echo ""
echo "🎉 Update completed!"
echo "🚀 Try: mcp-odoo --help"