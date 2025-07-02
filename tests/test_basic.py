import importlib

def test_import():
    assert importlib.import_module('blendair')


def test_fetch_script_mock(monkeypatch):
    from blendair import prompts
    monkeypatch.setattr(prompts, 'get_pref', lambda: type('P', (), {'llm_endpoint': 'mock'})())
    monkeypatch.setattr(prompts.requests, 'post', lambda *a, **kw: type('R', (), {'json': lambda self: {'script': 'print(123)'}, 'raise_for_status': lambda self: None})())
    assert prompts.fetch_script('hello') == 'print(123)'
