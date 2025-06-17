import types
import sys
from pathlib import Path

# Ensure project root on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub openai module to avoid import errors and network calls
openai_stub = types.ModuleType('openai')
class DummyClient:
    def __init__(self, api_key=None):
        pass
openai_stub.OpenAI = DummyClient
sys.modules['openai'] = openai_stub

import os
from llm_summarizer import summarize_article


def test_summarize_article_returns_none_without_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    summary, keywords = summarize_article('example content')
    assert summary is None and keywords is None
