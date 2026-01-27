# Phase 5 - Qualité & future-proofing

## Réalisé
- Tests unitaires couvrant factory, connecteurs, retries, erreurs.
- Squelettes tests intégration (avec skip si instances non dispo) et benchmarks perf.
- Docker compose multi-versions disponible.

## Backlog
- Activer CI GitHub Actions (workflow à ajouter) pour exécuter unit + intégration/perf conditionnels.
- Couverture 90%: ajouter tests sur config, logging, cache, migration utils.
- Mesures de perf comparatives XML-RPC vs JSON-2 à renseigner.
- Roadmap Odoo 20: surveiller suppression XML-RPC, prévoir fallback JSON-2 only.
