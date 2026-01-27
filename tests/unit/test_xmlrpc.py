import types
import xmlrpc.client

from mcp_odoo.connectors.xmlrpc import XMLRPCConnector


class DummyProxy:
    def __init__(self):
        self.called = []
        self.fail_first = True

    def authenticate(self, db, user, key, context):
        return 1

    def version(self):
        return {"server_version": "17.0"}

    def execute_kw(self, db, uid, key, model, method, args, kwargs):
        self.called.append((model, method, args, kwargs))
        if self.fail_first:
            self.fail_first = False
            raise xmlrpc.client.Fault(faultCode=1, faultString="Temporary fault")
        if method == "search":
            return [1]
        if method == "read":
            return [{"id": 1, "name": "Test"}]
        if method == "create":
            return 42
        return True


def test_xmlrpc_crud(monkeypatch):
    dummy = DummyProxy()
    monkeypatch.setattr("xmlrpc.client.ServerProxy", lambda *a, **k: dummy)

    connector = XMLRPCConnector(url="http://odoo17.local", database="db", api_key="key")
    assert connector.version() == 17.0
    assert connector.search("res.partner", []) == [1]
    recs = connector.read("res.partner", [1], ["name"])
    assert recs[0]["name"] == "Test"
    assert connector.create("res.partner", {"name": "X"}) == 42
    assert connector.write("res.partner", [1], {"name": "Y"}) is True
    assert connector.unlink("res.partner", [1]) is True
    # ensure retry was triggered: first call failed, second succeeded
    assert len(dummy.called) >= 6  # CRUD + retry increments calls
