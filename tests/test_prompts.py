from blendair import prompts

def test_parse_response(monkeypatch):
    # mock get_pref and requests.post
    class Pref: llm_endpoint = 'http://mock'
    monkeypatch.setattr(prompts, 'get_pref', lambda: Pref())

    class MockResp:
        def __init__(self):
            self._json = {"script": "print('ok')"}
        def raise_for_status(self):
            pass
        def json(self):
            return self._json
    monkeypatch.setattr(prompts.requests, 'post', lambda *a, **kw: MockResp())
    assert prompts.fetch_script('hi') == "print('ok')"
