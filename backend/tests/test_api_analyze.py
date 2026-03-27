"""Tests for /api/analyze endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAnalyzeEndpoint:
    """Test suite for /api/analyze endpoint."""

    def test_analyze_basic_claim(self):
        """Test analyzing a basic claim."""
        response = client.post(
            "/api/analyze",
            json={"text": "Water boils at 100 degrees Celsius"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "verdict" in data, "Response missing 'verdict' field"
        assert "confidence" in data, "Response missing 'confidence' field"
        assert "scores" in data, "Response missing 'scores' field"
        assert "key_signals" in data, "Response missing 'key_signals' field"
        assert "reasoning" in data, "Response missing 'reasoning' field"
        assert "sources" in data, "Response missing 'sources' field"

    def test_analyze_response_structure(self):
        """Validate complete response structure."""
        response = client.post(
            "/api/analyze",
            json={"text": "AI is transforming technology"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate verdict is one of expected values
        assert data["verdict"] in ["REAL", "RUMOR", "FAKE"], \
            f"Invalid verdict: {data['verdict']}"
        
        # Validate confidence is between 0 and 100
        assert 0 <= data["confidence"] <= 100, \
            f"Invalid confidence: {data['confidence']}"
        
        # Validate scores structure
        scores = data.get("scores", {})
        assert isinstance(scores, dict), "scores should be a dict"
        for key in ["real", "rumor", "fake"]:
            assert key in scores, f"scores missing '{key}'"
            assert 0 <= scores[key] <= 100, f"scores[{key}] out of range"
        
        # Scores should sum to 100
        total = sum(scores.values())
        assert abs(total - 100) < 1, f"scores don't sum to 100: {total}"
        
        # Validate confidence_label
        assert "confidence_label" in data
        assert data["confidence_label"] in ["LOW", "MEDIUM", "HIGH"]
        
        # Validate key_signals
        signals = data.get("key_signals", [])
        assert isinstance(signals, list), "key_signals should be a list"
        
        # Validate reasoning
        assert isinstance(data.get("reasoning", ""), str), \
            "reasoning should be a string"
        
        # Validate highlighted_text
        highlights = data.get("highlighted_text", [])
        assert isinstance(highlights, list), "highlighted_text should be a list"
        
        # Validate sources
        sources = data.get("sources", [])
        assert isinstance(sources, list), "sources should be a list"
        for source in sources:
            assert "title" in source, "source missing 'title'"
            assert "url" in source, "source missing 'url'"
            assert "credibility_score" in source, "source missing 'credibility_score'"

    def test_analyze_empty_text(self):
        """Test handling of empty text."""
        response = client.post(
            "/api/analyze",
            json={"text": ""}
        )
        
        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_analyze_very_long_text(self):
        """Test handling of very long text."""
        long_text = "This is a test claim. " * 500  # Very long text
        
        response = client.post(
            "/api/analyze",
            json={"text": long_text}
        )
        
        # Should handle long text gracefully
        assert response.status_code in [200, 400, 413]

    def test_analyze_special_characters(self):
        """Test handling of special characters."""
        claims = [
            "This claim has émojis 🎉 and special chars!",
            "Numbers: 12345, Math: 2+2=4, Symbols: @#$%",
            "Unicode: café, naïve, résumé",
        ]
        
        for claim in claims:
            response = client.post(
                "/api/analyze",
                json={"text": claim}
            )
            assert response.status_code == 200

    def test_analyze_invalid_json(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/analyze",
            json={"invalid_field": "no text field"}
        )
        
        # Should reject invalid requests
        assert response.status_code in [400, 422]

    def test_analyze_multiple_claims_consistency(self):
        """Test that same claim gives consistent results."""
        claim = "Python is a programming language"
        
        # Analyze same claim twice
        response1 = client.post("/api/analyze", json={"text": claim})
        response2 = client.post("/api/analyze", json={"text": claim})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Verdict and confidence should be consistent (or very close)
        assert data1["verdict"] == data2["verdict"]
        assert abs(data1["confidence"] - data2["confidence"]) < 5


class TestAnalyzeErrorHandling:
    """Test error handling in /api/analyze endpoint."""

    def test_malformed_request_missing_text(self):
        """Test request without text field."""
        response = client.post("/api/analyze", json={})
        assert response.status_code in [400, 422]

    def test_wrong_method(self):
        """Test using GET instead of POST."""
        response = client.get("/api/analyze")
        assert response.status_code == 405  # Method not allowed
