import os
import openai

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
DEFAULT_SUMMARY_LENGTH = int(os.environ.get("SUMMARY_LENGTH", 200))
DEFAULT_KEYWORD_COUNT = int(os.environ.get("KEYWORD_COUNT", 5))
DEFAULT_LANGUAGE = os.environ.get("SUMMARY_LANGUAGE", "en")

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

    prompt = (
        f"Extract {keyword_count} keywords from the following article in {language}, "
        f"then write a summary in {summary_length} words in {language}. "
        "Output format:\n"
        "Keywords: keyword1, keyword2, ...\n"
        "Summary: <summary text>"
    )

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            max_tokens=summary_length * 2,
        )
        result = response.choices[0].message.content.strip()
        # Parse output
        keywords = None
        summary = None
        for line in result.splitlines():
            if line.lower().startswith("keywords:"):
                keywords = line.split(":", 1)[1].strip()
            elif line.lower().startswith("summary:"):
                summary = line.split(":", 1)[1].strip()
        return summary, keywords
    except Exception as e:
        # Optionally log error here
        return None, None