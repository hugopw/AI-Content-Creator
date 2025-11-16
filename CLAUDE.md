# Content Sentinel System

## Project Philosophy

This is a content discovery and generation system built on the principle of **owning as little code as possible**. We favour:

1. Using existing tools and services over building from scratch
2. Simple, flat file storage over databases
3. GitHub as CMS over custom admin interfaces
4. Scheduled scripts over always-on services
5. LLM APIs over rule-based logic

**Scale assumption**: Low volume initially (5-20 articles/week). Don't optimise for scale we don't have.

## Project Overview

A system that:
1. Generates a "keyword universe" from an ICP and website content
2. Discovers RSS feeds where that ICP likely reads content
3. Monitors those feeds for relevant articles
4. Generates response articles in our tone of voice
5. Queues them for lightweight human review
6. Auto-publishes approved content to a static React site on Vercel

## Strategic Objective

**Increase organic search traffic from AI search engines (Perplexity, ChatGPT, Claude, Gemini) and traditional search (Google) month-on-month.**

Success = measurable uplift in organic traffic from these sources.

## Current Build Phase: Phase 1 - Keyword Universe & Feed Discovery

### Immediate Goal
Build the tool that:
- Takes AI Night School website content as input
- Takes an ideal customer profile as input
- Generates keyword universe (50-100 phrases representing how ICP thinks about topics)
- Searches for publications/sources where ICP likely reads content
- Outputs a list of RSS feed URLs to monitor

### Tech Stack Constraints

**What we're using:**
- Python 3.11+ for scripts
- Claude API (Sonnet 4) for all LLM tasks
- GitHub for storage/version control
- GitHub Actions for scheduling (when we get there)
- `feedparser` for RSS handling
- Existing React/Vercel site for publishing

**What we're NOT building:**
- No databases (use JSON/CSV files)
- No web frameworks (scripts only at this stage)
- No custom APIs
- No real-time systems (daily batch jobs are fine)

### File Structure
```
content-sentinel/
├── README.md
├── claude.md (this file)
├── PLANNING.md
├── .env.example
├── .gitignore
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── keyword_universe_generator.py
│   ├── feed_discovery.py
│   ├── feed_monitor.py (future)
│   ├── article_generator.py (future)
│   └── prompts/
│       ├── keyword_universe.txt
│       ├── feed_discovery.txt
│       ├── relevance_filter.txt (future)
│       └── article_generation.txt (future)
├── data/
│   ├── icp_profiles/
│   │   └── ai_night_school.json
│   ├── keyword_universes/
│   │   └── ai_night_school_keywords.json
│   └── feed_lists/
│       └── ai_night_school_feeds.json
├── content/
│   ├── pending/
│   ├── approved/
│   └── rejected/
└── tests/
    ├── __init__.py
    ├── test_keyword_universe_generator.py
    └── test_feed_discovery.py
```

### Acceptance Criteria for Current Phase

#### AC1: Keyword Universe Generation
```
GIVEN: An ICP description and website URL/content
WHEN: keyword_universe_generator.py runs
THEN:
  - System generates 50-100 keyword phrases
  - Keywords represent how ICP thinks about problems (not industry jargon)
  - Keywords include semantic variations and related concerns
  - Output saved as JSON with metadata (date generated, ICP name, source)
  - Keywords are human-readable and make intuitive sense
```

**Test**: Run with AI Night School ICP, manually review 10 random keywords, 8/10 should feel relevant and natural.

#### AC2: Feed Discovery
```
GIVEN: A keyword universe
WHEN: feed_discovery.py runs
THEN:
  - System identifies 10-20 potential RSS feed sources
  - Sources are publications/sites where ICP likely reads content
  - Each source includes: URL, RSS feed URL, brief description, relevance score
  - Output saved as JSON
  - Feeds are valid and currently active
```

**Test**: Run with AI Night School keywords, manually check 5 feeds, all should load and contain recent content.

#### AC3: Integration
```
GIVEN: ICP profile JSON file
WHEN: Running end-to-end workflow
THEN:
  - Keyword universe generates successfully
  - Feed discovery uses that universe
  - Both outputs are saved to correct locations
  - Process logs key stats (keywords generated, feeds found)
  - Process completes in < 5 minutes
```

### Code Quality Requirements

**Every Python file must have:**
1. Docstring at module level explaining purpose
2. Type hints on all functions
3. Error handling for API calls (with retries for rate limits)
4. Logging using Python's `logging` module (not just print statements)
5. At least one test file covering happy path

**Testing approach:**
- Use `pytest`
- Mock Claude API calls in tests (don't hit API in CI)
- Test data transformations and edge cases
- Don't test LLM outputs for exact matches (test structure/format only)

**Documentation:**
- README must explain how to run each script
- Each JSON output should have a corresponding `.example.json` showing structure
- Prompts should be in separate text files (not hardcoded in Python)
- Include comments explaining non-obvious logic

### Environment Setup

Required environment variables:
```
ANTHROPIC_API_KEY=your_key_here
```

Dependencies (requirements.txt):
```
anthropic>=0.40.0
feedparser>=6.0.0
pytest>=8.0.0
pytest-mock>=3.12.0
```

### Development Principles

1. **Fail fast**: If API calls fail, don't continue. Log the error and exit.
2. **Idempotent**: Running scripts multiple times shouldn't cause problems.
3. **Observable**: Log what's happening at each stage.
4. **Cacheable**: Don't regenerate keyword universe unless explicitly asked.
5. **Cheap**: Minimise token usage where possible (but don't sacrifice quality).

### What Claude Code Should Ask Before Building

- "Do we need this feature now, or is it future scope?"
- "Can we use an existing library instead of writing this?"
- "Is this the simplest approach that could work?"
- "Have we added unnecessary abstraction?"

### Current Inputs

**AI Night School Website**:
- Production: https://www.ainightschool.org
- **New version (use this)**: https://ainightschoolorg-git-chore-add-content-daniel-zarembas-projects.vercel.app/

**AI Night School ICP**:
```
AI Night School serves business leaders and executives who are:
- Overwhelmed by AI hype but know they need to act
- Time-poor (can't do lengthy courses)
- Want practical implementation guidance, not theory
- Interested in ROI and business value
- Reading: HBR, TechCrunch, Business Insider, MIT Tech Review, The Economist
- Age: 35-55
- Job titles: CEO, CTO, COO, VP Product, Head of Operations
- Pain points: "Where do I start?", "How do I get my team on board?", "What's the actual ROI?"
```

### Expected Outputs

#### Keyword Universe JSON Format
```json
{
  "generated_at": "2024-11-16T10:30:00Z",
  "icp_name": "ai_night_school",
  "source_website": "https://ainightschoolorg-git-chore-add-content-daniel-zarembas-projects.vercel.app/",
  "keywords": [
    {
      "phrase": "how to start with ai in my business",
      "category": "getting_started",
      "search_intent": "informational"
    },
    {
      "phrase": "ai roi calculator",
      "category": "business_value",
      "search_intent": "commercial"
    }
  ],
  "total_keywords": 75,
  "categories": ["getting_started", "business_value", "team_adoption", "practical_implementation"]
}
```

#### Feed List JSON Format
```json
{
  "generated_at": "2024-11-16T10:35:00Z",
  "source_keywords": "ai_night_school_keywords.json",
  "keywords": [
    {
      "publication": "Harvard Business Review",
      "feed_url": "https://hbr.org/feed",
      "website_url": "https://hbr.org",
      "description": "Business strategy and management insights",
      "relevance_score": 9,
      "categories": ["business", "strategy", "leadership"]
    }
  ],
  "total_feeds": 15
}
```

### Next Phases (Not Building Yet)

See PLANNING.md for full details.

- **Phase 2**: RSS feed monitoring + relevance filtering
- **Phase 3**: Article generation + review queue
- **Phase 4**: Auto-publishing to React site
- **Phase 5**: Analytics integration

---

## Notes for Claude Code

- **Challenge me** if I'm overengineering
- **Ask** if you're not sure whether we need a feature now
- **Prefer** boring, well-tested libraries over clever custom code
- **Document** why you made architectural choices in comments
- **Test** the code you write (at least happy paths)
- Keep it **simple** - we can always add complexity later if needed

This is a startup-scale project. Fast iteration > perfect code.

When in doubt, check PLANNING.md for context and rationale behind decisions.
