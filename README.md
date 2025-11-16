# Content Sentinel

An AI-powered content discovery and generation system that intercepts your ideal customer profile (ICP) where they're already looking.

**Current Status**: Phase 1a - Keyword Universe & Feed Discovery

## Overview

Content Sentinel helps you:
1. Generate a "keyword universe" from your ICP and website content
2. Discover RSS feeds where your ICP reads content
3. Monitor feeds for relevant articles (coming in Phase 1b)
4. Generate response articles in your tone of voice (coming in Phase 1c)
5. Publish to your static site automatically (coming in Phase 1c)

See [PLANNING.md](PLANNING.md) for full project details and [CLAUDE.md](CLAUDE.md) for technical specifications.

## Quick Start

### 1. Setup Environment

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and add your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Generate Keyword Universe

```bash
# Using AI Night School as example
python -m src.keyword_universe_generator \
  --icp data/icp_profiles/ai_night_school.json \
  --website-url https://ainightschoolorg-git-chore-add-content-daniel-zarembas-projects.vercel.app/
```

This will:
- Analyze the ICP profile and website content
- Generate 50-100 natural search phrases your ICP would use
- Save results to `data/keyword_universes/ai_night_school_keywords.json`

### 3. Review Output

```bash
# View generated keywords
cat data/keyword_universes/ai_night_school_keywords.json
```

## Project Structure

```
content-sentinel/
├── README.md                    # This file
├── CLAUDE.md                    # System guide for Claude Code
├── PLANNING.md                  # Decision history & architecture
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── src/
│   ├── keyword_universe_generator.py    # Phase 1a: Keyword generation
│   └── prompts/
│       └── keyword_universe.txt         # LLM prompt for keywords
├── data/
│   ├── icp_profiles/
│   │   └── ai_night_school.json        # AI Night School ICP
│   └── keyword_universes/
│       └── *.example.json              # Example output format
└── tests/
    └── test_keyword_universe_generator.py

```

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## Phase 1a: Keyword Universe Generation ✅

**Status**: Complete

Generate keyword universes from ICP profiles and website content.

**Acceptance Criteria**:
- ✅ Given ICP description and website, generates 50-100 keyword phrases
- ✅ Keywords represent how ICP thinks (not industry jargon)
- ✅ Output saved as JSON with metadata
- ✅ Keywords are human-readable and natural

**Usage**:
```bash
python -m src.keyword_universe_generator \
  --icp data/icp_profiles/ai_night_school.json \
  --website-url https://example.com \
  --output data/keyword_universes/custom_output.json
```

## Next Steps

**Phase 1b**: Feed Discovery
- Build tool to discover RSS feeds based on keyword universe
- Find publications where ICP reads content
- Validate feeds are active and relevant

**Phase 1c**: Article Generation & Publishing
- Monitor RSS feeds for new articles
- Generate response content using Claude
- Auto-publish to static site via GitHub

See [PLANNING.md](PLANNING.md) for detailed roadmap.

## Development Principles

Following the "own as little code as possible" philosophy:
- ✅ Use existing tools (Claude API, feedparser, GitHub Actions)
- ✅ Simple flat file storage (no database)
- ✅ Scheduled scripts (no always-on services)
- ✅ GitHub as CMS
- ✅ Focus on startup scale (5-20 articles/week)

## Contributing

This is currently a personal project for AI Night School. See CLAUDE.md for development guidelines if you're working with Claude Code.

## License

TBD
