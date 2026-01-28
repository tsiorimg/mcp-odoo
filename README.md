# MCP Odoo - Multi-Connector Platform

**A future-proof Python library for Odoo integration** featuring a hybrid architecture that seamlessly handles both XML-RPC (Odoo 14-18) and JSON-2 API (Odoo 19+).

## 🚨 Why This Project Matters

Odoo 19 introduced the new **JSON-2 API** while **deprecating XML-RPC**, with complete removal planned for **Odoo 20 (Fall 2026)**. This creates a critical transition period where organizations need to support multiple Odoo versions with different APIs.

**MCP Odoo solves this challenge** with intelligent auto-detection and unified interface across all supported versions.

## 🎯 Project Context

### The Problem
- **XML-RPC API** (Odoo 14-18): Traditional endpoint `/xmlrpc/2/object`
- **JSON-2 API** (Odoo 19+): Modern REST-like endpoint `/json/2/<model>/<method>`
- **Transition Challenge**: Organizations running mixed Odoo versions need dual-API support
- **Deadline Pressure**: XML-RPC removal in 2026 forces migration planning now

### The Solution: Hybrid Architecture
```python
# Single interface, automatic API selection
mcp = MCPOdoo(url="https://mycompany.odoo.com")
# → Auto-detects Odoo version → Uses appropriate API
partners = mcp.search("res.partner", [("is_company", "=", True)])
```

### Key Features
- 🔄 **Auto-detection**: Seamless version detection via `/web/version`
- 🔧 **Unified Interface**: Same code works across Odoo 14-19
- 🔐 **Modern Auth**: API Keys with rotation support
- 🐳 **Docker Testing**: Multi-version integration tests
- 📊 **Performance**: Benchmarks XML-RPC vs JSON-2
- 🚀 **Future-proof**: Ready for Odoo 20 transition

## 🏗️ Architecture Overview

```
MCPOdoo (Factory)
├── Version Detection (/web/version)
├── XMLRPCConnector (Odoo 14-18)
│   ├── xmlrpc.client
│   └── Login/password auth (API key optional if enabled)
└── JSON2Connector (Odoo 19+)
    ├── HTTP/JSON requests  
    └── Bearer token auth
```

## 🔧 Supported Operations

### Core CRUD
- `search()` - Query records with domains
- `read()` - Fetch record data  
- `write()` - Update records
- `create()` - Create new records
- `unlink()` - Delete records

### Advanced Features
- `fields_get()` - Model introspection
- `execute()` - Call public methods
- `search_read()` - Combined operations
- `ir.model` exploration - Dynamic model discovery

## 🎯 Use Cases

### Integration Scenarios
- **Multi-tenant SaaS** with customers on different Odoo versions
- **Enterprise migrations** from older to newer Odoo versions
- **Third-party applications** needing broad Odoo compatibility
- **Automation tools** (n8n, Zapier) with universal connectors
- **Data synchronization** between mixed Odoo environments

### Target Developers
- **Python developers** building Odoo integrations
- **DevOps teams** managing multi-version environments  
- **Solution architects** planning Odoo transitions
- **Automation specialists** using n8n/CLI workflows

## 📚 Quick Start

### Installation & Setup
```bash
# Development setup
git clone https://github.com/tsiorimg/mcp-odoo.git
cd mcp-odoo
poetry install --with dev,test

# OR Quick CLI installation
./scripts/install.sh
export PATH="$HOME/.local/bin:$PATH"
```

### Python Usage
```python
from mcp_odoo import MCPOdoo

# Auto-detection in action
mcp = MCPOdoo(
    url="https://mycompany.odoo.com",
    database="prod", 
    api_key="your_api_key"
)

# Unified interface across all versions
partners = mcp.search("res.partner", [("is_company", "=", True)])
partner_data = mcp.read("res.partner", partners[:5], ["name", "email"])
print(f"Found {len(partners)} companies")
```

### CLI Usage
Configure environment first:
```bash
# .env file
ODOO_URL=http://localhost:8069
ODOO_DATABASE=mcp_test
ODOO_API_KEY=your_api_key
```

Then use CLI commands:
```bash
mcp-odoo search --model res.partner --domain '[["is_company", "=", true]]'
mcp-odoo create --model res.partner --values '{"name":"New Partner"}'
mcp-odoo call --model sale.order --method action_confirm --ids 1
```

## 🧪 Testing & Development

### Multi-Version Testing
```bash
# Launch test environment with Odoo 14, 17, 19
docker-compose -f docker/docker-compose.test.yml up -d

# Run integration tests across all versions
pytest tests/integration/ -v

# Performance benchmarks
pytest tests/performance/ --benchmark-only
```

### Development Status
- ✅ **Core Architecture**: Hybrid connector system implemented
- ✅ **Multi-version Testing**: Docker Compose with Odoo 14/17/19
- ✅ **Integration Tests**: CRUD operations validated across versions
- 🔄 **Performance Benchmarks**: XML-RPC vs JSON-2 comparisons
- 📋 **CLI Interface**: Full command-line toolkit

### Remaining Work
- **CI/CD Pipeline**: GitHub Actions for automated testing
- **Enhanced Documentation**: Production deployment guides  
- **N8N Integration**: Custom nodes for workflow automation
- **REST Gateway**: HTTP API wrapper for web applications
- **Migration Tools**: XML-RPC to JSON-2 transition utilities

## ⚙️ Advanced Configuration

### Environment Variables
```bash
# Required
ODOO_URL=http://localhost:8069
ODOO_DATABASE=mcp_test  
ODOO_USER=admin
# Choose authentication depending on Odoo version
# - Odoo 14-18: set ODOO_PASSWORD (legacy login/password)
# - Odoo 19+: set ODOO_API_KEY (Bearer token)
ODOO_PASSWORD=your_password
ODOO_API_KEY=your_api_key_here

# Optional
ODOO_VERSION=17.0              # Auto-detected if omitted
MCP_RETRY_ATTEMPTS=3           # Connection retry logic
MCP_RETRY_BACKOFF=0.3          # Backoff delay in seconds
```

### Updates & Version Management
```bash
# Update installation
./scripts/update.sh

# Install specific version
./scripts/install.sh --version=v1.2.3

# Check current version
mcp-odoo --version

# Uninstall
./scripts/uninstall.sh
```

## 📊 API Compatibility Matrix

| Feature | XML-RPC (14-18) | JSON-2 (19+) | MCP Odoo |
|---------|-----------------|---------------|----------|
| **Authentication** | uid + password/key | Bearer token | ✅ Unified |
| **CRUD Operations** | execute_kw | REST endpoints | ✅ Unified |  
| **Transactions** | Multi-call support | Single per request | ✅ Handled |
| **Error Handling** | XML-RPC faults | HTTP status codes | ✅ Normalized |
| **Performance** | Good | Better | ✅ Optimized |

## 🤝 Contributing

### Development Workflow
```bash
# 1. Fork and clone repository
git clone https://github.com/yourusername/mcp-odoo.git

# 2. Install development dependencies  
poetry install --with dev,test

# 3. Run tests locally
pytest tests/unit/ -v                    # Unit tests (fast)
docker-compose -f docker/docker-compose.test.yml up -d
pytest tests/integration/ -v             # Integration tests (with Odoo)

# 4. Submit pull request with tests
```

### Supported Python Versions
- Python 3.9+
- Tested on: 3.9, 3.10, 3.11, 3.12

### Supported Odoo Versions  
- **Odoo 14.0-18.x**: XML-RPC API
- **Odoo 19.0+**: JSON-2 API
- **Auto-detection**: Seamless version switching

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support & Community

- **Issues**: [GitHub Issues](https://github.com/tsiorimg/mcp-odoo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tsiorimg/mcp-odoo/discussions)  
- **Documentation**: [Wiki](https://github.com/tsiorimg/mcp-odoo/wiki)

---

**🎯 Mission**: Provide the definitive Python library for Odoo integration that survives the API transition and guides the community through the migration to modern JSON-2 endpoints.
