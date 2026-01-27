import httpx
import respx

from mcp_odoo.connectors.json2 import JSON2Connector


@respx.mock
def test_json2_search_and_read():
    respx.get("http://odoo19.local/web/version").respond(json={"server_version": "19.0"})
    respx.post("http://odoo19.local/json/2/res.partner/search").respond(json=[1, 2])
    respx.post("http://odoo19.local/json/2/res.partner/read").respond(json=[{"id": 1, "name": "A"}])

    connector = JSON2Connector(url="http://odoo19.local", database="db", api_key="key")
    ids = connector.search("res.partner", [])
    assert ids == [1, 2]
    recs = connector.read("res.partner", [1], ["name"])
    assert recs[0]["name"] == "A"


@respx.mock
def test_json2_error_raises_apierror():
    respx.get("http://odoo19.local/web/version").respond(json={"version": "19.0"})
    respx.post("http://odoo19.local/json/2/res.partner/search").respond(status_code=400, json={"error": "bad"})

    connector = JSON2Connector(url="http://odoo19.local", database="db", api_key="key")
    try:
        connector.search("res.partner", [])
    except Exception as exc:  # ValidationError
        from mcp_odoo.core.exceptions import ValidationError

        assert isinstance(exc, ValidationError)
    else:
        assert False, "APIError not raised"


@respx.mock
def test_json2_retry_on_http_error():
    respx.get("http://odoo19.local/web/version").respond(json={"version": "19.0"})

    call_count = {"n": 0}

    def flaky(request):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise httpx.ConnectError("boom", request=request)
        return httpx.Response(200, json=[1])

    respx.post("http://odoo19.local/json/2/res.partner/search").mock(side_effect=flaky)

    connector = JSON2Connector(url="http://odoo19.local", database="db", api_key="key")
    ids = connector.search("res.partner", [])
    assert ids == [1]
    assert call_count["n"] == 2
