import os
import openai
import logging
import json
import re
from config import (
    DEFAULT_LANGUAGE,
    OPENAI_MODEL,
    DEFAULT_SUMMARY_LENGTH,
    DEFAULT_KEYWORD_COUNT,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logger.info(
    f"Loaded config: OPENAI_MODEL={OPENAI_MODEL}, SUMMARY_LENGTH={DEFAULT_SUMMARY_LENGTH}, "
    f"KEYWORD_COUNT={DEFAULT_KEYWORD_COUNT}, SUMMARY_LANGUAGE={DEFAULT_LANGUAGE}"
)

def summarize_article(
    content: str,
    language: str = DEFAULT_LANGUAGE,
    summary_length: int = DEFAULT_SUMMARY_LENGTH,
    keyword_count: int = DEFAULT_KEYWORD_COUNT,
    model: str = OPENAI_MODEL,
) -> tuple[str | None, str | None]:
    """
    Summarize an article and extract keywords using OpenAI.
    Returns (summary, keywords) or (None, None) on error.
    """
    if not OPENAI_API_KEY or not content:
        return None, None

    # Try to use OpenAI JSON mode if available
    prompt = (
        f"Extract {keyword_count} keywords from the following article in {language}, "
        f"then write a summary in {summary_length} words in {language}. "
        "Respond in JSON with keys 'keywords' (comma-separated string) and 'summary'."
    )

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logger.info(f"Using model: {model}")
        logger.info(f"Prompt: {prompt}")

        # Try JSON mode if supported
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            max_tokens=summary_length * 2,
            response_format={"type": "json_object"},
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"Raw LLM output: {result}")

        try:
            data = json.loads(result)
            summary = data.get("summary")
            keywords = data.get("keywords")
            if summary and keywords:
                return summary.strip(), keywords.strip()
        except Exception as json_exc:
            logger.warning(f"Failed to parse JSON output: {json_exc}")

        # Fallback: regex-based parsing
        summary = None
        keywords = None
        # Accepts "Keywords: ..." and "Summary: ..." (case-insensitive, flexible whitespace)
        keywords_match = re.search(r"(?i)keywords\s*:\s*(.+)", result)
        summary_match = re.search(r"(?i)summary\s*:\s*(.+)", result, re.DOTALL)
        if keywords_match:
            keywords = keywords_match.group(1).strip()
        if summary_match:
            summary = summary_match.group(1).strip()
        if summary is None or keywords is None:
            logger.warning("Failed to robustly parse summary or keywords from LLM output.")
        return summary, keywords

    except Exception as e:
        logger.error(f"Exception during summarization: {e}", exc_info=True)
        return None, None