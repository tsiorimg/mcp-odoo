# Phase 1 - Fondation de l'architecture

Cette phase couvre la structure du projet, la détection de version et la factory.

## Réalisé
- Arborescence modulaire `src/mcp_odoo/` conforme à AGENTS.md
- Interface `OdooConnector` définissant CRUD, introspection et appels de méthodes
- Détection automatique de version via `/web/version` (`detect_odoo_version`)
- `ConnectorFactory` qui choisit XML-RPC (<19) ou JSON-2 (>=19)
- Gestion de configuration `MCPConfig` (pydantic-settings)
- Logging structuré minimal (structlog)

## Tests
- `tests/unit/test_factory.py`: vérifie la détection de version et la sélection du connecteur

Commande:
```bash
. .venv/bin/activate
pytest tests/unit/test_factory.py -q
```

## Prochaines étapes
- Enrichir le mapping d'erreurs et le retry
- Couverture tests sur connecteurs et config
