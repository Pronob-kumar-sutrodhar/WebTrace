"""
Unit tests for the Flask Web Dashboard API endpoints.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
from webtrace.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestWebApp:
    """Test suite for Web Dashboard backend."""

    def test_index_page_renders(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"WebTrace" in response.data

    def test_api_crawl_dry_run(self, client):
        payload = {
            "seed": "https://example.com/",
            "max_depth": 2,
            "max_pages": 5,
            "dry_run": True,
        }
        response = client.post(
            "/api/crawl",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["stats"]["dry_run"] is True

    def test_api_crawl_invalid_url(self, client):
        payload = {"seed": "not-a-valid-url"}
        response = client.post(
            "/api/crawl",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
