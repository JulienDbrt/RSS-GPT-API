import os

DEFAULT_LANGUAGE = os.environ.get("SUMMARY_LANGUAGE", "fr")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
DEFAULT_SUMMARY_LENGTH = int(os.environ.get("SUMMARY_LENGTH", 250))
DEFAULT_KEYWORD_COUNT = int(os.environ.get("KEYWORD_COUNT", 6))