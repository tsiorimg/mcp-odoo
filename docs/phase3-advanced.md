# Phase 3 - Gestion avancée (erreurs, retries, cache)

## Réalisé
- Mapping d'erreurs JSON-2 → exceptions (`ValidationError`, `NotFoundError`, `RateLimitError`, `ServerError`, `AuthenticationError`).
- Retries avec backoff exponentiel léger (3 tentatives) pour XML-RPC et JSON-2 (`utils/retry.py`).
- Cache `fields_get` (LRU, 128 entrées) dans les deux connecteurs pour accélérer l'introspection.

## Tests
- `tests/unit/test_json2.py`: vérifie erreurs 400 → `ValidationError` et retry après erreur réseau.
- `tests/unit/test_xmlrpc.py`: vérifie retry après `Fault` XML-RPC et CRUD complet.

Commande:
```bash
. .venv/bin/activate
pytest tests/unit -q
```

## À faire ensuite
- Backoff parametrable via config
- Journaux structurés enrichis (durées, retries)
- Tests d'intégration Docker multi-versions
- Benchmarks perfs (search/read, bulk)
