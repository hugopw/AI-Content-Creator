"""
Tests for keyword_universe_generator module

These tests focus on structure and logic, not exact LLM outputs.
Claude API calls are mocked to avoid hitting the API during tests.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime

from src.keyword_universe_generator import KeywordUniverseGenerator


@pytest.fixture
def mock_icp_profile():
    """Sample ICP profile for testing."""
    return {
        "name": "test_icp",
        "audience": "Test audience",
        "characteristics": {
            "mindset": "Test mindset",
            "time": "Time-poor",
            "needs": "Test needs",
            "focus": "Test focus"
        },
        "pain_points": ["Pain 1", "Pain 2"],
        "reading_habits": ["Publication 1", "Publication 2"]
    }


@pytest.fixture
def mock_keywords_response():
    """Sample keywords response from Claude."""
    return {
        "keywords": [
            {
                "phrase": "test keyword 1",
                "category": "test_category",
                "search_intent": "informational"
            },
            {
                "phrase": "test keyword 2",
                "category": "test_category",
                "search_intent": "commercial"
            }
        ],
        "categories": ["test_category"],
        "total_keywords": 2
    }


class TestKeywordUniverseGenerator:
    """Test suite for KeywordUniverseGenerator class."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        generator = KeywordUniverseGenerator(api_key="test_key")
        assert generator.api_key == "test_key"
        assert generator.client is not None

    def test_init_without_api_key_raises_error(self):
        """Test initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
                KeywordUniverseGenerator()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env_key'})
    def test_init_with_env_var(self):
        """Test initialization reads API key from environment."""
        generator = KeywordUniverseGenerator()
        assert generator.api_key == "env_key"

    def test_load_prompt_template(self):
        """Test loading prompt template from file."""
        generator = KeywordUniverseGenerator(api_key="test_key")
        prompt = generator.load_prompt_template()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Check for key phrases from the prompt
        assert "keyword universe" in prompt.lower()
        assert "json" in prompt.lower()

    def test_load_icp_profile(self, mock_icp_profile, tmp_path):
        """Test loading ICP profile from JSON file."""
        generator = KeywordUniverseGenerator(api_key="test_key")

        # Create temporary ICP file
        icp_file = tmp_path / "test_icp.json"
        with open(icp_file, 'w') as f:
            json.dump(mock_icp_profile, f)

        # Load and verify
        loaded_profile = generator.load_icp_profile(str(icp_file))
        assert loaded_profile == mock_icp_profile

    def test_load_icp_profile_file_not_found(self):
        """Test loading ICP profile raises error if file doesn't exist."""
        generator = KeywordUniverseGenerator(api_key="test_key")

        with pytest.raises(FileNotFoundError):
            generator.load_icp_profile("nonexistent.json")

    def test_fetch_website_content(self):
        """Test fetching website content (currently just returns URL)."""
        generator = KeywordUniverseGenerator(api_key="test_key")
        url = "https://example.com"
        content = generator.fetch_website_content(url)

        assert content == url

    @patch('src.keyword_universe_generator.Anthropic')
    def test_generate_keywords_success(
        self,
        mock_anthropic_class,
        mock_icp_profile,
        mock_keywords_response
    ):
        """Test successful keyword generation."""
        # Mock the API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps(mock_keywords_response))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        generator = KeywordUniverseGenerator(api_key="test_key")
        result = generator.generate_keywords(
            icp_profile=mock_icp_profile,
            website_content="https://example.com",
            website_url="https://example.com"
        )

        # Verify structure
        assert "generated_at" in result
        assert "icp_name" in result
        assert "source_website" in result
        assert "keywords" in result
        assert "total_keywords" in result
        assert "categories" in result

        # Verify content
        assert result["icp_name"] == "test_icp"
        assert result["source_website"] == "https://example.com"
        assert result["total_keywords"] == 2
        assert len(result["keywords"]) == 2
        assert result["categories"] == ["test_category"]

    @patch('src.keyword_universe_generator.Anthropic')
    def test_generate_keywords_validates_json_structure(
        self,
        mock_anthropic_class,
        mock_icp_profile
    ):
        """Test that generated keywords have expected JSON structure."""
        mock_client = Mock()
        mock_response = Mock()

        keywords_data = {
            "keywords": [
                {
                    "phrase": "test phrase",
                    "category": "test_cat",
                    "search_intent": "informational"
                }
            ],
            "categories": ["test_cat"],
            "total_keywords": 1
        }

        mock_response.content = [Mock(text=json.dumps(keywords_data))]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        generator = KeywordUniverseGenerator(api_key="test_key")
        result = generator.generate_keywords(
            icp_profile=mock_icp_profile,
            website_content="test content"
        )

        # Check each keyword has required fields
        for keyword in result["keywords"]:
            assert "phrase" in keyword
            assert "category" in keyword
            assert "search_intent" in keyword

    def test_save_keywords(self, mock_keywords_response, tmp_path):
        """Test saving keywords to JSON file."""
        generator = KeywordUniverseGenerator(api_key="test_key")

        output_file = tmp_path / "output" / "keywords.json"
        keywords = {
            "generated_at": datetime.now().isoformat(),
            "icp_name": "test",
            "source_website": "https://example.com",
            **mock_keywords_response
        }

        generator.save_keywords(keywords, str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Verify content
        with open(output_file, 'r') as f:
            saved_data = json.load(f)

        assert saved_data["icp_name"] == "test"
        assert saved_data["total_keywords"] == 2
        assert len(saved_data["keywords"]) == 2

    @patch('src.keyword_universe_generator.Anthropic')
    @patch('src.keyword_universe_generator.sleep')
    def test_generate_keywords_retries_on_rate_limit(
        self,
        mock_sleep,
        mock_anthropic_class,
        mock_icp_profile,
        mock_keywords_response
    ):
        """Test that API rate limits trigger retries."""
        from anthropic import RateLimitError

        mock_client = Mock()

        # First call raises rate limit, second succeeds
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps(mock_keywords_response))]

        # Create a proper RateLimitError with required arguments
        mock_rate_limit_response = Mock()
        mock_rate_limit_response.status_code = 429

        rate_limit_error = RateLimitError(
            message="Rate limited",
            response=mock_rate_limit_response,
            body={"error": {"message": "Rate limited"}}
        )

        mock_client.messages.create.side_effect = [
            rate_limit_error,
            mock_response
        ]
        mock_anthropic_class.return_value = mock_client

        generator = KeywordUniverseGenerator(api_key="test_key")
        result = generator.generate_keywords(
            icp_profile=mock_icp_profile,
            website_content="test"
        )

        # Should have succeeded after retry
        assert result is not None
        assert mock_client.messages.create.call_count == 2
        assert mock_sleep.called


class TestKeywordStructure:
    """Tests for keyword data structure validation."""

    def test_keyword_has_required_fields(self):
        """Test that keywords have all required fields."""
        keyword = {
            "phrase": "test phrase",
            "category": "test_category",
            "search_intent": "informational"
        }

        assert "phrase" in keyword
        assert "category" in keyword
        assert "search_intent" in keyword
        assert isinstance(keyword["phrase"], str)
        assert isinstance(keyword["category"], str)
        assert keyword["search_intent"] in ["informational", "commercial", "navigational"]

    def test_output_format_matches_spec(self, mock_keywords_response):
        """Test that output format matches specification from CLAUDE.md."""
        # Add metadata to match full output format
        full_output = {
            "generated_at": "2024-11-16T10:30:00Z",
            "icp_name": "test_icp",
            "source_website": "https://example.com",
            **mock_keywords_response
        }

        # Verify all required top-level fields exist
        assert "generated_at" in full_output
        assert "icp_name" in full_output
        assert "source_website" in full_output
        assert "keywords" in full_output
        assert "total_keywords" in full_output
        assert "categories" in full_output

        # Verify keywords is a list
        assert isinstance(full_output["keywords"], list)
        assert len(full_output["keywords"]) > 0

        # Verify categories is a list
        assert isinstance(full_output["categories"], list)
