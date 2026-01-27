# Phase 2 - Connecteurs Core

Cette phase implémente les connecteurs XML-RPC (14-18) et JSON-2 (19+) avec une API unifiée.

## Réalisé
- `XMLRPCConnector` (XML-RPC stdlib) avec CRUD, search_read, fields_get, call_method
- `JSON2Connector` (httpx) avec endpoints `/json/2/<model>/<method>`
- Validation des IDs et construction d'en-têtes (`connectors/utils.py`)
- Mapping d'erreurs initial (APIError)

## Tests
- `tests/unit/test_xmlrpc.py`: mocks ServerProxy pour vérifier CRUD
- `tests/unit/test_json2.py`: mocks HTTP via respx pour search/read et erreurs

Commande:
```bash
. .venv/bin/activate
pytest tests/unit -q
```

## Points restants
- Retries et backoff
- Mapping d'erreurs plus complet (codes → exceptions dédiées)
- Tests de performance et intégration Docker
