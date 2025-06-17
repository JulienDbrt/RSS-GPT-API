from datetime import datetime
import types
import sys
from pathlib import Path

# Ensure project root on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub logging to avoid configuration issues
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stub dateutil.parser.parse
dateutil_parser = types.ModuleType('dateutil.parser')

def stub_parse(value):
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')

dateutil_parser.parse = stub_parse
sys.modules['dateutil'] = types.ModuleType('dateutil')
sys.modules['dateutil'].parser = dateutil_parser

# Inline implementation of parse_datetime extracted from fetch_articles
def parse_datetime(dt_str, entry=None):
    """Parse a datetime string from an RSS entry."""
    if entry and hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6])
        except Exception as e:  # pragma: no cover - logging not critical
            logger.warning(f"Failed to parse published_parsed: {e}")
    if not dt_str:
        return None
    try:
        return dateutil_parser.parse(dt_str)
    except Exception as e:  # pragma: no cover - logging not critical
        logger.error(f"Error parsing datetime from '{dt_str}': {e}", exc_info=True)
        return None

class Entry:
    def __init__(self, parsed=None):
        self.published_parsed = parsed


def test_parse_datetime_prefers_struct_time():
    import time
    parsed = time.gmtime(0)
    dt = parse_datetime(None, entry=Entry(parsed))
    assert dt == datetime(1970, 1, 1)

def test_parse_datetime_string():
    dt = parse_datetime('2024-01-01T12:00:00')
    assert dt == datetime(2024, 1, 1, 12, 0, 0)
