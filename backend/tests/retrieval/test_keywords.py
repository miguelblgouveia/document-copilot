from __future__ import annotations

import json

from unittest.mock import MagicMock, patch

from app.retrieval.keywords import FtsKeywordExtraction, extract_fts_keywords
from app.retrieval.types import SearchFilters

LONG_NVDA_QUERY = (
    "How did NVIDIA describe demand drivers and customer concentration "
    "for its Data Center business?"
)

LONG_NEUTRAL_QUERY = (
    "What did management say about operating margins and cost structure "
    "across recent fiscal years?"
)


def _mock_parse_response(terms: list[str]) -> MagicMock:
    message = MagicMock()
    message.parsed = FtsKeywordExtraction(terms=terms)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response



@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_returns_llm_terms(mock_post):
    mock_post.return_value.json.return_value = {
        "message": {
            "content": '{"terms": ["data center", "demand", "customer concentration"]}'
        }
    }
    mock_post.return_value.raise_for_status.return_value = None

    result = extract_fts_keywords(LONG_NVDA_QUERY, filters=SearchFilters(ticker="NVDA"))

    words = result.split()
    assert len(words) <= 5

    assert "demand" in result.casefold()
    assert "center" in result.casefold()
    assert "nvidia" not in result.casefold()
    
    call_kwargs = mock_post.call_args.kwargs
    payload = call_kwargs["json"]
    user_message = payload["messages"][1]["content"]

    assert "Ticker filter: NVDA" in user_message
    assert LONG_NVDA_QUERY in user_message



@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_fast_path_skips_llm(mock_post):
    short_query = "Azure AI cloud capacity"

    result = extract_fts_keywords(short_query)

    assert result == short_query
    mock_post.assert_not_called()


def _mock_ollama_response(mock_post, terms):
    mock_post.return_value.json.return_value = {
        "message": {
            "content": json.dumps({"terms": terms})
        }
    }
    mock_post.return_value.raise_for_status.return_value = None

@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_clamps_to_max_terms(mock_post: MagicMock) -> None:
    _mock_ollama_response(mock_post, ["one", "two", "three", "four", "five", "six"])

    result = extract_fts_keywords(LONG_NEUTRAL_QUERY)

    assert result == "one two three four five"




@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_dedupes_terms(mock_post: MagicMock) -> None:
    _mock_ollama_response(mock_post, ["Azure", "azure", "AI", "cloud"])

    result = extract_fts_keywords(LONG_NEUTRAL_QUERY)

    assert result == "Azure AI cloud"



@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_falls_back_when_llm_raises(mock_post: MagicMock) -> None:
    mock_post.side_effect = RuntimeError("api down")

    result = extract_fts_keywords(LONG_NVDA_QUERY)

    assert "NVIDIA" in result
    assert "demand" in result.casefold()
    assert len(result.split()) <= 5
    assert "how" not in result.casefold().split()



@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_falls_back_when_too_few_terms(mock_post: MagicMock) -> None:
    _mock_ollama_response(mock_post, ["Azure"])

    result = extract_fts_keywords(LONG_NVDA_QUERY)

    assert len(result.split()) >= 3


@patch("app.retrieval.keywords.requests.post")
def test_extract_fts_keywords_falls_back_when_parse_is_none(mock_post: MagicMock) -> None:
    mock_post.return_value.json.return_value = {
        "message": {"content": "invalid json"}
    }
    mock_post.return_value.raise_for_status.return_value = None

    result = extract_fts_keywords(LONG_NVDA_QUERY)

    assert result
    assert "how" not in result.casefold().split()
