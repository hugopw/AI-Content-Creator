"""
Keyword Universe Generator

Generates a comprehensive "keyword universe" representing how an ideal customer profile (ICP)
thinks about and searches for topics related to a website's content.

Uses Claude API to analyze ICP characteristics and website content, producing 50-100 natural
search phrases that the ICP would actually use, avoiding industry jargon in favor of
user-centric language.

Usage:
    python -m src.keyword_universe_generator --icp data/icp_profiles/ai_night_school.json --website-url https://example.com

Requirements:
    - ANTHROPIC_API_KEY environment variable must be set
    - ICP profile JSON file must exist
    - Either website URL or website content must be provided
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from time import sleep

from anthropic import Anthropic, APIError, RateLimitError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KeywordUniverseGenerator:
    """Generates keyword universes using Claude API based on ICP profiles and website content."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the keyword universe generator.

        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it as an environment variable or pass it to the constructor."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Sonnet 4 as specified in CLAUDE.md
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def load_prompt_template(self) -> str:
        """
        Load the keyword universe generation prompt from file.

        Returns:
            The prompt template as a string.

        Raises:
            FileNotFoundError: If prompt file doesn't exist.
        """
        prompt_path = Path(__file__).parent / 'prompts' / 'keyword_universe.txt'

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_icp_profile(self, icp_path: str) -> Dict[str, Any]:
        """
        Load ICP profile from JSON file.

        Args:
            icp_path: Path to the ICP profile JSON file.

        Returns:
            Dictionary containing ICP profile data.

        Raises:
            FileNotFoundError: If ICP file doesn't exist.
            json.JSONDecodeError: If ICP file is not valid JSON.
        """
        icp_file = Path(icp_path)

        if not icp_file.exists():
            raise FileNotFoundError(f"ICP profile not found at {icp_path}")

        with open(icp_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def fetch_website_content(self, website_url: str) -> str:
        """
        Fetch website content for analysis.

        Args:
            website_url: URL of the website to analyze.

        Returns:
            Website content as string (for now, just returns the URL).

        Note:
            For Phase 1, we'll keep this simple and just pass the URL to Claude.
            Claude can fetch and analyze the content directly.
            Future enhancement: Use requests/BeautifulSoup for pre-processing.
        """
        # For Phase 1, we'll let Claude fetch the content via its web tools
        # This keeps our code simple as per the "own as little code as possible" principle
        logger.info(f"Will analyze website at: {website_url}")
        return website_url

    def generate_keywords(
        self,
        icp_profile: Dict[str, Any],
        website_content: str,
        website_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate keyword universe using Claude API.

        Args:
            icp_profile: Dictionary containing ICP characteristics.
            website_content: Website content or URL to analyze.
            website_url: Optional website URL for metadata.

        Returns:
            Dictionary containing generated keywords with metadata.

        Raises:
            APIError: If Claude API call fails after retries.
        """
        prompt_template = self.load_prompt_template()

        # Construct the user message with ICP profile and website info
        user_message = f"""
ICP PROFILE:
{json.dumps(icp_profile, indent=2)}

WEBSITE TO ANALYZE:
{website_content}

Please analyze this ICP profile and website content, then generate a comprehensive keyword universe of 50-100 search phrases following the guidelines in the system prompt.

Return ONLY the JSON object, no additional commentary.
"""

        # Call Claude API with retries
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling Claude API (attempt {attempt + 1}/{self.max_retries})...")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=prompt_template,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )

                # Extract the response text
                response_text = response.content[0].text

                # Parse JSON from response
                try:
                    keywords_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Claude response: {e}")
                    logger.debug(f"Response text: {response_text}")
                    raise

                # Add metadata
                result = {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "icp_name": icp_profile.get("name", "unknown"),
                    "source_website": website_url or website_content,
                    "keywords": keywords_data.get("keywords", []),
                    "total_keywords": keywords_data.get("total_keywords", len(keywords_data.get("keywords", []))),
                    "categories": keywords_data.get("categories", [])
                }

                logger.info(f"Successfully generated {result['total_keywords']} keywords across {len(result['categories'])} categories")
                return result

            except RateLimitError as e:
                logger.warning(f"Rate limit hit: {e}")
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (attempt + 1)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                else:
                    logger.error("Max retries reached for rate limit")
                    raise

            except APIError as e:
                logger.error(f"API error: {e}")
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                else:
                    logger.error("Max retries reached")
                    raise

    def save_keywords(self, keywords: Dict[str, Any], output_path: str) -> None:
        """
        Save keyword universe to JSON file.

        Args:
            keywords: Dictionary containing keywords and metadata.
            output_path: Path where JSON file should be saved.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(keywords, f, indent=2, ensure_ascii=False)

        logger.info(f"Keyword universe saved to {output_path}")


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate keyword universe from ICP profile and website content'
    )
    parser.add_argument(
        '--icp',
        required=True,
        help='Path to ICP profile JSON file'
    )
    parser.add_argument(
        '--website-url',
        help='URL of website to analyze'
    )
    parser.add_argument(
        '--website-content',
        help='Direct website content (alternative to URL)'
    )
    parser.add_argument(
        '--output',
        help='Output path for keyword universe JSON (default: data/keyword_universes/{icp_name}_keywords.json)'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.website_url and not args.website_content:
        parser.error("Either --website-url or --website-content must be provided")

    try:
        # Initialize generator
        generator = KeywordUniverseGenerator()

        # Load ICP profile
        logger.info(f"Loading ICP profile from {args.icp}")
        icp_profile = generator.load_icp_profile(args.icp)

        # Get website content
        if args.website_url:
            website_content = generator.fetch_website_content(args.website_url)
            website_url = args.website_url
        else:
            website_content = args.website_content
            website_url = None

        # Generate keywords
        logger.info("Generating keyword universe...")
        keywords = generator.generate_keywords(icp_profile, website_content, website_url)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            icp_name = icp_profile.get('name', 'unknown')
            output_path = f"data/keyword_universes/{icp_name}_keywords.json"

        # Save results
        generator.save_keywords(keywords, output_path)

        # Print summary
        print(f"\n✓ Keyword universe generated successfully!")
        print(f"  • Total keywords: {keywords['total_keywords']}")
        print(f"  • Categories: {', '.join(keywords['categories'])}")
        print(f"  • Saved to: {output_path}")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate keyword universe: {e}", exc_info=True)
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
