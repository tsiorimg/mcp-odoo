# Plan: MCP Odoo Python – Multi-Connector Platform

Créer un MCP (Multi-Connector Platform) pour Odoo en Python, capable de se connecter aux versions Odoo 14 à 19 via l'API XML-RPC (14-18) et la nouvelle API JSON-2 (19+). Le projet supportera la lecture, l'écriture de données et l'appel de méthodes publiques Odoo. **Architecture hybride** pour gérer la transition API avec dépréciation XML-RPC prévue en Odoo 20 (2026). Inclut documentation complète, tests unitaires, et interfaces n8n/CLI.

## Steps

### Phase 1: Architecture Hybride
1. **Architecture du MCP**: Structure modulaire avec adaptateurs XML-RPC et JSON-2
2. **Détection automatique**: Auto-détection version Odoo et sélection API appropriée
3. **Module de connexion XML-RPC**: Pour Odoo 14-18 avec gestion API Keys
4. **Module de connexion JSON-2**: Pour Odoo 19+ avec authentification Bearer
5. **Interface unifiée**: Abstraction des différences entre APIs

### Phase 2: Core Functionality
6. **Gestionnaire de configuration**: Support multi-instances, rotation API keys
7. **Module d'introspection**: Intégration `ir.model`/`ir.model.fields` (toutes versions)
8. **Module de lecture**: Implémentation unifiée `search`, `read`, `search_read`, `fields_get`
9. **Module d'écriture**: Implémentation unifiée `create`, `write`, `unlink`
10. **Module d'exécution**: Appel méthodes publiques avec gestion transactionnelle

### Phase 3: Gestion Avancée
11. **Cache intelligent**: Métadonnées avec invalidation par version
12. **Gestion d'erreurs**: Mapping erreurs XML-RPC ↔ JSON-2
13. **Migration assistant**: Outils transition XML-RPC → JSON-2
14. **Performance**: Optimisations spécifiques par API

### Phase 4: Interfaces
15. **Interface CLI**: Commandes unifiées multi-versions
16. **Interface n8n**: Nodes avec auto-détection API
17. **API REST**: Gateway unifié avec proxying intelligent

### Phase 5: Qualité et Future-proofing
18. **Tests unitaires**: Couverture XML-RPC + JSON-2 avec mocks
19. **Tests d'intégration**: Validation multi-versions réelles
20. **Documentation**: Guide migration, comparaison APIs
21. **Exemples**: Scripts démonstratifs pour chaque version
22. **Roadmap v20**: Préparation suppression XML-RPC

## Spécifications Techniques

### Versions Odoo et APIs
- **Odoo 14.0-18.x**: XML-RPC (`/xmlrpc/2/common`, `/xmlrpc/2/object`)
- **Odoo 19.0+**: JSON-2 API (`/json/2/<model>/<method>`)
- **Transition critique**: XML-RPC déprécié, suppression Odoo 20 (automne 2026)
- **Auto-détection**: Version via `/web/version` → sélection API automatique

### Authentification Hybride

#### XML-RPC (14-18)
- **Méthode**: `common.authenticate(db, login, api_key, {})`
- **Headers**: Standard HTTP sans autorisation spéciale
- **API Keys**: Remplacement password par clé (14+)

#### JSON-2 (19+)
- **Méthode**: Header `Authorization: bearer <api_key>`
- **Headers requis**: `Host`, `Content-Type`, `X-Odoo-Database`
- **API Keys**: Obligatoires, durée max 3 mois, rotation requise
- **Bot users**: Recommandés pour intégrations (pas de password)

### Stack Technique Python
- **XML-RPC**: `xmlrpc.client` (stdlib)
- **JSON-2**: `requests` ou `httpx` pour HTTP moderne
- **Configuration**: `pydantic-settings` pour validation
- **CLI**: `typer` avec auto-complétion
- **Tests**: `pytest` + `respx` (httpx) + `requests-mock`
- **Documentation**: `mkdocs-material` avec exemples live

### Environnements Odoo

#### Configuration Multi-Environnements
```yaml
# .env.development
ODOO_URL=http://localhost:8069
ODOO_DATABASE=mcp_test
ODOO_USER=admin
ODOO_API_KEY=dev_api_key_here
ODOO_VERSION=17.0  # Auto-détecté si non spécifié

# .env.testing
ODOO_URL=http://localhost:8070  # Instance Docker test
ODOO_DATABASE=test_db
ODOO_USER=test_user
ODOO_API_KEY=test_api_key

# .env.production
ODOO_URL=https://mycompany.odoo.com
ODOO_DATABASE=prod_db
ODOO_USER=integration_bot
ODOO_API_KEY=${SECURE_API_KEY}  # Injecté via CI/CD
```

#### Docker Compose pour Tests
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  odoo-14:
    image: odoo:14.0
    ports: ["8069:8069"]
    environment:
      - HOST=db-14
      - USER=odoo
      - PASSWORD=odoo
    depends_on: ["db-14"]
    
  odoo-17:
    image: odoo:17.0  
    ports: ["8070:8069"]
    environment:
      - HOST=db-17
      - USER=odoo
      - PASSWORD=odoo
    depends_on: ["db-17"]
    
  odoo-19:
    image: odoo:19.0
    ports: ["8071:8069"] 
    environment:
      - HOST=db-19
      - USER=odoo
      - PASSWORD=odoo
    depends_on: ["db-19"]
    
  db-14:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes: ["odoo-14-data:/var/lib/postgresql/data"]
    
  db-17:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres  
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes: ["odoo-17-data:/var/lib/postgresql/data"]
    
  db-19:
    image: postgres:16
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo 
      - POSTGRES_PASSWORD=odoo
    volumes: ["odoo-19-data:/var/lib/postgresql/data"]

volumes:
  odoo-14-data:
  odoo-17-data: 
  odoo-19-data:
```

### Architecture des Connecteurs

```python
# Interface unifiée
class OdooConnector(ABC):
    @abstractmethod
    def search(self, model: str, domain: list) -> list[int]
    
    @abstractmethod 
    def read(self, model: str, ids: list[int], fields: list[str]) -> list[dict]

# Implémentations spécialisées
class XMLRPCConnector(OdooConnector): pass
class JSON2Connector(OdooConnector): pass

# Factory avec auto-détection
class ConnectorFactory:
    @staticmethod
    def create(url: str) -> OdooConnector:
        version = detect_version(url)
        return XML2Connector(url) if version >= 19 else XMLRPCConnector(url)
```

### Gestion des Différences API

| Aspect | XML-RPC | JSON-2 |
|--------|---------|--------|
| **Endpoint** | `/xmlrpc/2/object` | `/json/2/<model>/<method>` |
| **Auth** | `uid + password/key` | `Bearer <api_key>` |
| **Params** | `execute_kw(db, uid, pwd, model, method, args, kwargs)` | `POST {"ids": [], "context": {}, "fields": []}` |
| **Transactions** | Multi-calls possibles | Une transaction par requête |
| **Erreurs** | Exceptions XML-RPC | Status HTTP + JSON error |

### Migration et Compatibilité
- **Détection automatique**: Version serveur → API appropriée
- **Fallback intelligent**: JSON-2 non disponible → XML-RPC
- **Assistant migration**: Scripts conversion config XML-RPC → JSON-2
- **Logging différentiel**: Alertes dépréciation XML-RPC
- **Documentation transition**: Guide migration step-by-step

## Stratégie de Test

### Tests Unitaires (Mocks)
```python
# Tests rapides sans Odoo réel
@pytest.fixture
def mock_odoo_xmlrpc():
    with patch('xmlrpc.client.ServerProxy') as mock:
        mock.return_value.version.return_value = {'server_version': '17.0'}
        yield mock
        
@pytest.fixture  
def mock_odoo_json2():
    with respx.mock as mock:
        mock.get('/web/version').respond(json={'version': '19.0'})
        mock.post('/json/2/res.partner/search').respond(json=[1, 2, 3])
        yield mock
```

### Tests d'Intégration (Docker)
```python
# tests/integration/conftest.py
@pytest.fixture(scope="session")
def odoo_environments():
    """Lance les instances Odoo via Docker Compose"""
    subprocess.run(["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"])
    
    # Attente démarrage + initialisation DB
    wait_for_odoo("http://localhost:8069")  # Odoo 14
    wait_for_odoo("http://localhost:8070")  # Odoo 17  
    wait_for_odoo("http://localhost:8071")  # Odoo 19
    
    # Setup initial data
    setup_test_data_v14()
    setup_test_data_v17() 
    setup_test_data_v19()
    
    yield {
        "odoo_14": "http://localhost:8069",
        "odoo_17": "http://localhost:8070", 
        "odoo_19": "http://localhost:8071"
    }
    
    subprocess.run(["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"])

def setup_test_data_v14():
    """Crée des données de test dans Odoo 14"""
    # Création partenaires, produits, commandes via XML-RPC
    pass
```

### Tests End-to-End Multi-Versions
```python
# tests/integration/test_cross_version.py
class TestCrossVersionCompatibility:
    
    def test_partner_crud_all_versions(self, odoo_environments):
        """Test CRUD partenaires sur toutes versions"""
        for version, url in odoo_environments.items():
            mcp = MCPOdoo(url=url)
            
            # Create
            partner_id = mcp.create('res.partner', {'name': f'Test Partner {version}'})
            assert isinstance(partner_id, int)
            
            # Read 
            partner = mcp.read('res.partner', [partner_id], ['name'])[0]
            assert partner['name'] == f'Test Partner {version}'
            
            # Update
            mcp.write('res.partner', [partner_id], {'email': 'test@example.com'})
            updated = mcp.read('res.partner', [partner_id], ['email'])[0]
            assert updated['email'] == 'test@example.com'
            
            # Delete
            mcp.unlink('res.partner', [partner_id])
            assert mcp.search('res.partner', [('id', '=', partner_id)]) == []
    
    def test_api_detection(self, odoo_environments):
        """Vérifie auto-détection API"""
        # Odoo 14/17 doit utiliser XML-RPC
        mcp_14 = MCPOdoo(url=odoo_environments["odoo_14"])
        assert isinstance(mcp_14.connector, XMLRPCConnector)
        
        # Odoo 19 doit utiliser JSON-2
        mcp_19 = MCPOdoo(url=odoo_environments["odoo_19"])  
        assert isinstance(mcp_19.connector, JSON2Connector)
        
    def test_metadata_consistency(self, odoo_environments):
        """Vérifie cohérence métadonnées entre versions"""
        for version, url in odoo_environments.items():
            mcp = MCPOdoo(url=url)
            
            # Fields res.partner doivent être cohérents
            fields = mcp.fields_get('res.partner')
            assert 'name' in fields
            assert 'email' in fields
            assert fields['name']['type'] == 'char'
```

### Tests de Performance
```python
# tests/performance/test_benchmarks.py
class TestPerformance:
    
    @pytest.mark.benchmark(group="search")
    def test_search_performance_xmlrpc(self, benchmark, odoo_17):
        mcp = MCPOdoo(url=odoo_17)
        result = benchmark(mcp.search, 'res.partner', [('is_company', '=', True)])
        assert len(result) > 0
        
    @pytest.mark.benchmark(group="search")
    def test_search_performance_json2(self, benchmark, odoo_19):
        mcp = MCPOdoo(url=odoo_19) 
        result = benchmark(mcp.search, 'res.partner', [('is_company', '=', True)])
        assert len(result) > 0
        
    def test_bulk_operations(self, odoo_environments):
        """Test opérations bulk sur datasets importants"""
        for version, url in odoo_environments.items():
            mcp = MCPOdoo(url=url)
            
            # Création 1000 partenaires
            start = time.time()
            partner_ids = []
            for i in range(1000):
                partner_id = mcp.create('res.partner', {'name': f'Bulk Partner {i}'})
                partner_ids.append(partner_id)
            
            creation_time = time.time() - start
            logger.info(f"{version}: Création 1000 partners en {creation_time:.2f}s")
            
            # Lecture bulk
            start = time.time() 
            partners = mcp.read('res.partner', partner_ids, ['name'])
            read_time = time.time() - start
            logger.info(f"{version}: Lecture 1000 partners en {read_time:.2f}s")
            
            assert len(partners) == 1000
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test MCP Odoo
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
        
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        pip install -e .[test]
        
    - name: Unit tests (mocks)
      run: pytest tests/unit/ -v
      
    - name: Start Odoo test environments  
      run: docker-compose -f docker-compose.test.yml up -d
      
    - name: Wait for Odoo instances
      run: |
        ./scripts/wait-for-odoo.sh localhost:8069
        ./scripts/wait-for-odoo.sh localhost:8070 
        ./scripts/wait-for-odoo.sh localhost:8071
        
    - name: Integration tests
      run: pytest tests/integration/ -v --tb=short
      
    - name: Performance tests
      run: pytest tests/performance/ -v --benchmark-only
      
    - name: Cleanup
      run: docker-compose -f docker-compose.test.yml down -v
```
