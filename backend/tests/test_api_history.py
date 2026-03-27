"""Tests for /api/history endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHistoryEndpoint:
    """Test suite for /api/history endpoint."""

    def test_history_basic_get(self):
        """Test basic history retrieval."""
        response = client.get("/api/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list), "history should return a list"

    def test_history_response_structure(self):
        """Validate history response structure."""
        response = client.get("/api/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Each history item should have required fields
        for item in data:
            assert "id" in item, "history item missing 'id'"
            assert "text" in item, "history item missing 'text'"
            assert "verdict" in item, "history item missing 'verdict'"
            assert "confidence" in item, "history item missing 'confidence'"
            assert "confidence_label" in item, "history item missing 'confidence_label'"
            assert "timestamp" in item, "history item missing 'timestamp'"

    def test_history_ordering(self):
        """Test that history returns latest first."""
        # Add a few claims
        claims = [
            "Claim 1",
            "Claim 2",
            "Claim 3",
        ]
        
        for claim in claims:
            client.post("/api/analyze", json={"text": claim})
        
        response = client.get("/api/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least our 3 claims
        assert len(data) >= 3, "history should contain recent claims"
        
        # Verify ordering is by timestamp descending (latest first)
        timestamps = [item.get("timestamp") for item in data]
        sorted_timestamps = sorted(
            [t for t in timestamps if t],
            reverse=True
        )
        
        # Check that returned items follow descending timestamp order
        for i in range(1, min(len(timestamps), len(sorted_timestamps))):
            # Timestamps should be in descending order
            assert timestamps[i-1] >= timestamps[i], \
                f"History not ordered by timestamp: {timestamps[i-1]} < {timestamps[i]}"

    def test_history_limit(self):
        """Test history limit parameter."""
        response = client.get("/api/history?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return at most 5 items
        assert len(data) <= 5, f"history exceeded limit: {len(data)}"

    def test_history_persistence(self):
        """Test that history persists after analysis."""
        # Analyze a unique claim
        unique_claim = f"Unique test claim {__import__('time').time()}"
        
        client.post("/api/analyze", json={"text": unique_claim})
        
        # Retrieve history
        response = client.get("/api/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Find our claim in history
        found = False
        for item in data:
            if item["text"] == unique_claim:
                found = True
                assert item["verdict"] in ["REAL", "RUMOR", "FAKE"]
                assert 0 <= item["confidence"] <= 100
                break
        
        assert found, "Analyzed claim not found in history"

    def test_history_verdict_consistency(self):
        """Test that verdict in history matches analysis response."""
        claim = "Python is widely used in data science"
        
        # Analyze claim
        analyze_response = client.post("/api/analyze", json={"text": claim})
        analyze_data = analyze_response.json()
        
        # Get history
        history_response = client.get("/api/history")
        history_data = history_response.json()
        
        # Find matching history item
        for item in history_data:
            if item["text"] == claim:
                # Verdict should match
                assert item["verdict"] == analyze_data["verdict"], \
                    "verdict mismatch between analysis and history"
                
                # Confidence should match closely
                assert abs(item["confidence"] - analyze_data["confidence"]) < 1, \
                    "confidence mismatch between analysis and history"
                break

    def test_history_empty_with_no_queries(self):
        """Test history when no queries have been made."""
        # Don't call analyze, just get history
        response = client.get("/api/history")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestHistoryErrorHandling:
    """Test error handling in /api/history endpoint."""

    def test_history_invalid_method(self):
        """Test using POST instead of GET."""
        response = client.post("/api/history", json={})
        assert response.status_code == 405  # Method not allowed

    def test_history_invalid_limit(self):
        """Test invalid limit parameter."""
        response = client.get("/api/history?limit=abc")
        # Should handle gracefully (either error or ignore)
        assert response.status_code in [200, 400, 422]


class TestIntegration:
    """Integration tests for analyze and history."""

    def test_analyze_then_history(self):
        """Test full workflow: analyze then retrieve history."""
        claim = "Test claim for integration test"
        
        # Step 1: Analyze
        analyze_response = client.post(
            "/api/analyze",
            json={"text": claim}
        )
        assert analyze_response.status_code == 200
        analyze_data = analyze_response.json()
        
        # Step 2: Get history
        history_response = client.get("/api/history")
        assert history_response.status_code == 200
        history_data = history_response.json()
        
        # Step 3: Verify claim is in history
        found = False
        for item in history_data:
            if item["text"] == claim:
                found = True
                assert item["verdict"] == analyze_data["verdict"]
                assert item["confidence"] == analyze_data["confidence"]
                break
        
        assert found, "Analyzed claim not in history after analysis"

    def test_multiple_analyses_all_in_history(self):
        """Test that multiple analyses all appear in history."""
        claims = [
            "Integration test claim 1",
            "Integration test claim 2",
            "Integration test claim 3",
        ]
        
        # Analyze all claims
        for claim in claims:
            response = client.post("/api/analyze", json={"text": claim})
            assert response.status_code == 200
        
        # Get history
        history_response = client.get("/api/history")
        assert history_response.status_code == 200
        history_data = history_response.json()
        
        # Verify all claims are in history
        history_texts = [item["text"] for item in history_data]
        for claim in claims:
            assert claim in history_texts, \
                f"Claim '{claim}' not found in history"
