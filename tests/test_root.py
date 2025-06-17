import types
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide stub openai to satisfy llm_summarizer import if needed
sys.modules.setdefault("openai", types.ModuleType("openai"))
# FastAPI's TestClient requires httpx; provide a minimal stub if missing
if 'httpx' not in sys.modules:
    sys.modules['httpx'] = types.ModuleType('httpx')

# Provide stub sqlalchemy to import the app without database dependencies
if 'sqlalchemy' not in sys.modules:
    sa = types.ModuleType('sqlalchemy')
    sa.orm = types.ModuleType('sqlalchemy.orm')
    def create_engine(*args, **kwargs):
        class Engine: ...
        return Engine()
    sa.create_engine = create_engine
    sa.orm.Session = type('Session', (), {})
    def sessionmaker(*args, **kwargs):
        def maker(*a, **k):
            return None
        return maker
    sa.orm.sessionmaker = sessionmaker
    # Provide minimal Column and other constructs used by models
    sa.Column = lambda *a, **k: None
    placeholder = type('Placeholder', (), {})
    sa.Integer = sa.String = sa.Text = sa.DateTime = placeholder
    sa.Enum = lambda *a, **k: None
    sa.ForeignKey = lambda *a, **k: None
    sa.Table = lambda *a, **k: None
    class Base:
        metadata = type('Meta', (), {})()
    sa.orm.declarative_base = lambda: Base
    sa.orm.relationship = lambda *a, **k: None
    sys.modules['sqlalchemy'] = sa
    sys.modules['sqlalchemy.orm'] = sa.orm

import app


def test_read_root_function():
    assert app.read_root() == {"message": "RSS-GPT API is running."}
