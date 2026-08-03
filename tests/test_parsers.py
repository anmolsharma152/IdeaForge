"""Test JSON parsing logic across graph nodes."""

import pytest

from ideaforge.graph.nodes.diverge import _parse_candidates
from ideaforge.graph.nodes.evaluate import _parse_scores
from ideaforge.graph.nodes.synthesize import _parse_refined


@pytest.mark.unit
def test_parse_candidates():
    # Valid JSON
    valid_json = '[{"title": "Idea 1", "body": "Body 1", "tags": ["t1"]}, {"title": "Idea 2", "body": "Body 2", "tags": ["t2"]}]'
    parsed = _parse_candidates(valid_json, expected=2)
    assert len(parsed) == 2
    assert parsed[0]["title"] == "Idea 1"
    
    # Wrapped in markdown
    md_json = f"```json\n{valid_json}\n```"
    parsed_md = _parse_candidates(md_json, expected=2)
    assert len(parsed_md) == 2
    
    # Invalid JSON should return empty list
    invalid_json = "This is just some text, not JSON"
    parsed_invalid = _parse_candidates(invalid_json, expected=2)
    assert len(parsed_invalid) == 0
    
    # Missing fields
    missing_fields = '[{"title": "Idea 1"}]'
    parsed_missing = _parse_candidates(missing_fields, expected=1)
    assert len(parsed_missing) == 0


@pytest.mark.unit
def test_parse_scores():
    # Valid JSON
    valid_json = '[{"coherence": 0.8, "usefulness": 0.9}]'
    parsed = _parse_scores(valid_json, expected=1)
    assert len(parsed) == 1
    assert parsed[0]["coherence"] == 0.8
    assert parsed[0]["usefulness"] == 0.9
    
    # Invalid JSON
    invalid_json = "Bad format"
    parsed_invalid = _parse_scores(invalid_json, expected=2)
    assert len(parsed_invalid) == 2
    # Should fallback to 0.5 scores
    assert parsed_invalid[0]["coherence"] == 0.5


@pytest.mark.unit
def test_parse_refined():
    # Valid JSON
    valid_json = '{"title": "Refined", "body": "Refined body", "tags": ["t1"]}'
    parsed = _parse_refined(valid_json)
    assert parsed["title"] == "Refined"
    assert parsed["body"] == "Refined body"
    assert parsed["tags"] == ["t1"]
    
    # Wrapped in markdown
    md_json = f"```\n{valid_json}\n```"
    parsed_md = _parse_refined(md_json)
    assert parsed_md["title"] == "Refined"
    
    # Invalid JSON
    invalid = _parse_refined("Not JSON")
    assert invalid["title"] == "Synthesis failed"
