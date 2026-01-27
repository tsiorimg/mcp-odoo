import types

import pytest
import respx
import httpx

from mcp_odoo.core.factory import ConnectorFactory, detect_odoo_version


@respx.mock
def test_detect_odoo_version_reads_web_version():
    respx.get("http://odoo.example.com/web/version").respond(
        json={"server_version": "19.0"}
    )
    version = detect_odoo_version("http://odoo.example.com")
    assert version == 19.0


def test_factory_selects_json2(monkeypatch):
    calls = {}

    def fake_json_init(self, *args, **kwargs):
        calls["json2"] = True

    def fake_xml_init(self, *args, **kwargs):
        calls["xmlrpc"] = True

    monkeypatch.setattr("mcp_odoo.connectors.json2.JSON2Connector.__init__", fake_json_init)
    monkeypatch.setattr("mcp_odoo.connectors.xmlrpc.XMLRPCConnector.__init__", fake_xml_init)

    connector = ConnectorFactory.create(
        url="http://example.com",
        database="db",
        api_key="key",
        version=19.0,
    )
    assert "json2" in calls
    assert not calls.get("xmlrpc")
    assert connector.__class__.__name__ == "JSON2Connector"

    connector = ConnectorFactory.create(
        url="http://example.com",
        database="db",
        api_key="key",
        version=17.0,
    )
    assert "xmlrpc" in calls
    assert connector.__class__.__name__ == "XMLRPCConnector"


def test_detect_odoo_version_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("boom", request=httpx.Request("GET", args[0]))

    monkeypatch.setattr(httpx, "get", fake_get)
    with pytest.raises(Exception):
        detect_odoo_version("http://nonexistent.local", timeout=0.01)
