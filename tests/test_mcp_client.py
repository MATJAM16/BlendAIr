from blendair.mcp_client import BlenderMCPClient


def test_get_context(monkeypatch):
    client = BlenderMCPClient()
    monkeypatch.setattr(client, 'base_url', 'http://mock')

    class MockResp:
        def raise_for_status(self):
            pass
        def json(self):
            return {"hello": "world"}
    import requests
    monkeypatch.setattr(requests, 'get', lambda url: MockResp())
    ctx = client.get_context('demo')
    assert ctx == {"hello": "world"}
