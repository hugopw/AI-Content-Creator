# Content Sentinel - Planning & Architecture Decisions

**Last Updated**: November 2024
**Project Status**: Phase 1 - Keyword Universe & Feed Discovery
**Strategic Goal**: Increase organic search traffic from AI search engines and traditional search

---

## Table of Contents
1. [Project Origin & Philosophy](#project-origin--philosophy)
2. [Strategic Objectives & Success Metrics](#strategic-objectives--success-metrics)
3. [Acceptance Criteria Hierarchy](#acceptance-criteria-hierarchy)
4. [Phase Breakdown](#phase-breakdown)
5. [Architecture Decisions](#architecture-decisions)
6. [What We're NOT Building](#what-were-not-building)
7. [Open Questions & Future Considerations](#open-questions--future-considerations)

---

## Project Origin & Philosophy

### The Core Problem
Traditional content marketing is reactive - you publish and hope people find you. We want to **intercept our ICP where they're already looking** by:
1. Understanding what they're actually searching for (not industry jargon)
2. Finding the articles they're reading
3. Creating response content that gets discovered alongside those articles

### The Hypothesis
If we can identify what our ICP is reading, and create quality response content that references those articles, we'll:
- Rank for the same search terms
- Get cited by AI search engines alongside the original sources
- Build topical authority through consistent, relevant content
- Generate inbound links when the original articles get shared

### Founding Principles
1. **Own as little code as possible** - favour existing tools and services
2. **Simple is better** - flat files over databases, scripts over services
3. **Startup scale** - build for 5-20 articles/week, not thousands
4. **Fast iteration** - get to production quickly, prove value, then iterate
5. **Outcome-focused testing** - test that we achieve business goals, not just technical correctness

### First Use Case
**AI Night School** (www.ainightschool.org) - Hugo's AI training business for executives.

The new version of the site is being released at:
https://ainightschoolorg-git-chore-add-content-daniel-zarembas-projects.vercel.app/

**Future use cases**:
- Wife's hypnotherapy practice (teen anxiety niche targeting mothers)
- Product consultancy offering (teach this system to clients)

---

## Strategic Objectives & Success Metrics

### North Star Metric
**Increase organic search traffic from AI search engines and traditional search month-on-month**

Measured via analytics showing traffic from:
- Google (traditional search)
- Perplexity (AI search)
- ChatGPT (AI search)
- Claude (AI search)
- Gemini (AI search)

### Secondary Metrics
- Number of relevant articles discovered per week
- Article generation-to-publish rate
- Time saved vs manual content creation
- Internal link graph density (as proxy for content interconnection)
- Pages indexed by search engines
- Backlinks acquired from published articles

### Success Definition
After 3 months of operation:
- 50+ new articles published
- Measurable uplift in organic traffic from target sources
- System requires < 2 hours/week of human intervention
- Content quality is "good enough" (drives traffic, doesn't harm brand)
- At least 5 articles ranking on page 1 for target keywords

---

## Acceptance Criteria Hierarchy

### Level 1: Strategic OKR
**Increase organic search traffic from AI search engines and traditional search by X% month-on-month**

### Level 2: Outcome-Based Acceptance Criteria

**AC1: System discovers relevant content daily**
- Given a keyword universe for an ICP
- When articles matching those keywords are published
- Then the system identifies them within 24 hours
- And filters out irrelevant matches

**AC2: System generates on-brand response content**
- Given a relevant source article
- When the article generator runs
- Then it produces markdown content matching defined ToV/worldview
- And references the source article appropriately

**AC3: Content reaches production with minimal friction**
- Given a generated article
- When it enters review queue
- Then human can approve/reject with single action
- And approved content publishes to static site automatically

**AC4: Published content is discoverable**
- Given published articles on the static site
- When search engines/LLMs crawl the site
- Then content is properly indexed with relevant metadata
- And internal linking supports discovery

### Level 3: Technical Acceptance Criteria

#### Keyword Universe Generation
- **AC3.1**: Given an ICP description and topic, LLM generates 50-100 phrases representing how ICP thinks about the problem
- **AC3.2**: Keywords include semantic variations, related concerns, and tangential topics ICP would search for
- **AC3.3**: Keyword universe stored in simple format (JSON/CSV) for RSS feed configuration

#### Content Discovery
- **AC3.4**: System monitors RSS feeds from defined sources
- **AC3.5**: New articles matching keyword universe flagged within 24 hours
- **AC3.6**: LLM relevance filter scores articles 0-10 for ICP relevance
- **AC3.7**: Only articles scoring 7+ proceed to article generation
- **AC3.8**: System logs rejected articles with reasoning for review/tuning

#### Article Generation
- **AC3.9**: Given approved source article, system generates markdown file with frontmatter (title, date, source URL, keywords)
- **AC3.10**: Article references source naturally, doesn't copy extensively
- **AC3.11**: Article written in defined ToV (stored as system prompt)
- **AC3.12**: Article includes relevant internal links to existing content where appropriate
- **AC3.13**: Generated articles stored in `/content/blog/pending/` folder

#### Review Process
- **AC3.14**: System presents pending articles in simple review interface (GitHub PR initially)
- **AC3.15**: Single-click approve moves markdown from `/pending/` to `/approved/`
- **AC3.16**: Single-click reject archives to `/rejected/` with optional reason
- **AC3.17**: No action after 48 hours = auto-reject (prevents queue buildup)

#### Publishing
- **AC3.18**: Approved articles trigger Vercel build via webhook/API
- **AC3.19**: React site reads markdown files and renders with stylesheet
- **AC3.20**: Published articles include proper meta tags for SEO (title, description, OG tags)
- **AC3.21**: Sitemap auto-updates with new content

#### Monitoring
- **AC3.22**: Weekly report shows: articles discovered, relevance scores, articles generated, approval rate, publish rate
- **AC3.23**: Monthly analytics integration showing organic traffic by source

---

## Phase Breakdown

### Phase 0: Manual Validation (Week 1) - RECOMMENDED FIRST STEP
**Goal**: Validate the entire concept before writing any code.

**Activities**:
1. Have Claude generate keyword universe for AI Night School + ICP
2. Set up Google Alerts or Feedly for those keywords manually
3. Spend one week seeing what articles come through
4. Manually write 2-3 response articles using Claude
5. Publish them to existing site

**Exit criteria**:
- Relevant articles actually exist in the feeds
- Response articles feel valuable (not just SEO spam)
- We actually want to continue with automation

**Why this matters**: If the concept doesn't work manually, automation won't save it.

**Decision**: We're skipping Phase 0 and going straight to Phase 1 because Hugo is confident in the concept.

### Phase 1: Minimum Automated Loop (Weeks 1-3) - CURRENT PHASE

**Scope**:
- Keyword universe generation tool
- RSS feed discovery tool
- Basic feed monitoring
- Article generation via Claude API
- GitHub PR as review interface
- Vercel auto-deploy on merge

**Tech Stack**:
- Python scripts (target < 500 lines total)
- Claude API (Sonnet 4)
- GitHub (storage + CI/CD)
- GitHub Actions (scheduling)
- Existing React/Vercel site

**Phase 1 Sub-phases**:

**Phase 1a: Keyword Universe & Feed Discovery (Current)**
1. `keyword_universe_generator.py` - takes ICP + website, outputs keywords
2. `feed_discovery.py` - takes keywords, outputs RSS feed list
3. System prompts for each LLM task
4. Basic tests for each component

**Phase 1b: Feed Monitoring & Relevance Filtering**
1. `feed_monitor.py` - checks feeds, filters by relevance
2. `relevance_filter.py` - scores articles for ICP fit
3. Queue management (JSON file with pending articles)

**Phase 1c: Article Generation & Publishing**
1. `article_generator.py` - generates markdown response articles
2. GitHub Actions workflow for daily runs
3. Integration with Vercel for auto-deploy

**Success criteria for Phase 1**:
- System runs automatically once per day
- Produces 1-3 article drafts per week
- Human reviews in GitHub PR
- Approved articles publish automatically
- Total human time < 30 mins/week

### Phase 2: Polish (Month 2) - ONLY IF PHASE 1 PROVES VALUABLE

**Potential additions**:
- Better review interface (custom Next.js page, Airtable, or Notion)
- Keyword universe refresh (monthly re-generation based on trending topics)
- Analytics integration (track which articles drive traffic)
- Internal linking suggestions (based on existing content semantic similarity)
- Email digest of weekly activity
- A/B testing different article styles
- Quality scoring for generated articles
- Archive/search for historical content

**Decision point**: Only build what we're actually missing after running Phase 1 for a month.

### Phase 3: Product-ification (Month 3+) - IF BUILDING FOR CLIENTS

**Changes needed**:
- Multi-tenant support (different ICPs, websites, ToV)
- Better config management (not hardcoded)
- Client dashboard
- White-label options
- Documentation for handoff
- Onboarding flow
- Billing integration

**Not building this yet** - prove value for our own use first.

---

## Architecture Decisions

### Decision 1: GitHub as CMS
**Decision**: Use GitHub repo for content storage, version control, and review process.

**Rationale**:
- Free for private repos
- Built-in version control
- PR system is already a review workflow
- Vercel integrates natively
- Zero custom code needed for CMS

**Alternative considered**: Contentful, Sanity, custom CMS - all require more setup and maintenance.

**Trade-off**: Less user-friendly for non-technical users, but we're technical and it's just for us initially.

### Decision 2: Static Site (React + Vercel)
**Decision**: Keep existing static React site, add markdown rendering if needed.

**Rationale**:
- Already built
- Free hosting on Vercel
- Fast page loads (good for SEO)
- No server to maintain
- Auto-deploys on git push

**Alternative considered**: WordPress, Ghost, custom backend - all overkill for our scale.

**Trade-off**: Need to rebuild entire site for each new article, but at our scale (< 20 articles/week) this is negligible.

**Note**: Need to verify if existing React site supports markdown rendering. If not, we'll need to add a library like `react-markdown` or convert markdown to HTML at build time.

### Decision 3: Flat File Storage (JSON)
**Decision**: Store keyword universes, feed lists, and article queues as JSON files in the repo.

**Rationale**:
- No database to maintain
- Human-readable and git-diffable
- Easy to backup (it's in git)
- Sufficient for startup scale

**Alternative considered**: PostgreSQL, MongoDB, Airtable - all require external services and connection management.

**Trade-off**: Doesn't scale to millions of records, but we're nowhere near that. Will reconsider if we hit 10,000+ articles.

### Decision 4: Scheduled Scripts vs Always-On Service
**Decision**: Daily batch job via GitHub Actions, not a constantly-running service.

**Rationale**:
- Simpler (no server management)
- Cheaper (runs for ~5 mins/day, not 24/7)
- Good enough (daily discovery is sufficient)
- GitHub Actions free tier covers our usage

**Alternative considered**: AWS Lambda, Cloud Run, always-on API - all require more infrastructure.

**Trade-off**: Not real-time, but we don't need real-time for content discovery.

### Decision 5: Claude API for All LLM Tasks
**Decision**: Use Claude (Sonnet 4) for keyword generation, relevance filtering, and article writing.

**Rationale**:
- High-quality outputs
- Good instruction-following
- Extended context window (useful for article generation)
- We know it well
- Supports structured outputs natively

**Alternative considered**: GPT-4, Gemini, open-source models - all viable, but Claude is our preference.

**Trade-off**: API costs, but at our scale (~100 API calls/day) it's negligible (< £50/month).

### Decision 6: RSS Over Web Scraping
**Decision**: Monitor RSS feeds rather than scraping websites directly.

**Rationale**:
- RSS is designed for this (legal, expected use)
- Simpler parsing (standardised format)
- More reliable (no breaking when sites redesign)
- Lower rate-limit risk

**Alternative considered**: Web scraping with Playwright/Selenium - much more fragile and legally grey.

**Trade-off**: Limited to sites that offer RSS feeds, but that's most of our target publications.

**Note**: For publications that don't have RSS, we can manually add their content via web_fetch or similar tools later.

### Decision 7: Manual Review via GitHub PR (Phase 1)
**Decision**: Use GitHub PR approval as the review process initially.

**Rationale**:
- Zero code to build
- Version control built-in
- Diff view shows exactly what's being published
- Familiar workflow for technical users

**Alternative considered**: Custom review UI, Notion/Airtable integration - all require building something.

**Trade-off**: Not user-friendly for non-technical clients, but fine for us. Can add custom UI later if needed.

### Decision 8: Keyword Universe as Static Asset (Phase 1)
**Decision**: Generate keyword universe once, store as JSON, manually refresh when needed.

**Rationale**:
- Keywords don't change rapidly
- Manual refresh allows for quality control
- Saves API costs
- Simpler logic

**Alternative considered**: Auto-refresh monthly, dynamic keyword generation - adds complexity we don't need yet.

**Trade-off**: Might miss emerging topics, but we can manually refresh when we notice gaps.

---

## What We're NOT Building

It's important to document what we explicitly decided NOT to build, to avoid scope creep.

### Not Building (Yet or Ever)

1. **Real-time monitoring** - Daily batch is sufficient
2. **Database** - Flat files are fine at this scale
3. **Custom CMS** - GitHub is our CMS
4. **Social media posting** - Focus on owned content first
5. **Comment systems** - Not part of MVP
6. **Advanced analytics dashboard** - Use Google Analytics
7. **Multi-language support** - English only initially
8. **AI model fine-tuning** - Prompting is sufficient
9. **Image generation** - Text content only
10. **Video/podcast content** - Written content only
11. **Email newsletter integration** - Manual for now
12. **A/B testing framework** - Too early
13. **User accounts/auth** - Single user (Hugo)
14. **API for external access** - Internal tool only
15. **Mobile app** - Web interface sufficient
16. **Blockchain/web3 anything** - Obviously not
17. **Real-time collaboration** - Single author
18. **Payment processing** - Not a paid product yet
19. **Multi-tenant architecture** - Single instance for now
20. **Enterprise SSO** - Not applicable

### Features We Might Add Later (Phase 2+)

Only if Phase 1 proves valuable:
- Better review UI
- Analytics integration
- Internal linking suggestions
- Keyword universe refresh automation
- Email digests
- Quality scoring for generated articles
- Archive/search for historical content
- Topic clustering
- Competitive intelligence
- Link graph analysis

### Features for Product-ification (Phase 3+)

Only if turning this into a client offering:
- Multi-tenant support
- Client dashboard
- White-labelling
- Billing integration
- Onboarding flow
- Client documentation
- User accounts
- Team permissions
- Usage analytics

---

## Open Questions & Future Considerations

### Current Uncertainties

**Q1: How many articles will we actually want to publish per week?**
- **Current assumption**: 5-10 per week
- **Decision point**: After 1 month of operation, review quality vs quantity
- **Risk**: Too many articles = thin content, hurt SEO

**Q2: What's the right relevance threshold?**
- **Current assumption**: Score of 7/10 from Claude relevance filter
- **Decision point**: After 2 weeks, review false positives/negatives
- **Risk**: Too strict = miss good opportunities, too loose = irrelevant content

**Q3: Does the React site support markdown rendering?**
- **Current assumption**: It might, need to verify
- **Decision point**: Check existing site setup before building article generator
- **Risk**: Might need to add markdown rendering library or convert to HTML pre-build

**Q4: How often should keyword universe refresh?**
- **Current assumption**: Manual refresh when needed
- **Decision point**: After 3 months, evaluate if keywords feel stale
- **Risk**: Static keywords miss emerging topics

**Q5: What's the approval rate we should expect?**
- **Current assumption**: 80% of generated articles get approved
- **Decision point**: After 1 month, review actual rate
- **Risk**: Low approval rate = wasted API costs and generation time

**Q6: How do we handle articles behind paywalls?**
- **Current assumption**: RSS feeds give us enough context to write response
- **Decision point**: If we can't generate quality responses from RSS alone, reconsider
- **Risk**: Might need subscription access to key publications

**Q7: What's Hugo's tone of voice definition?**
- **Current assumption**: Will be defined during article generator build
- **Decision point**: Need to capture ToV examples before building generator
- **Risk**: Generated articles don't sound like Hugo

### Future Exploration

**Idea 1: Topic clustering**
Could we automatically cluster generated articles by topic and suggest series/pillar content?

**Idea 2: Competitive intelligence**
Could we track which keywords competitors are ranking for and generate content accordingly?

**Idea 3: Link graph analysis**
Could we use internal linking patterns to identify content gaps?

**Idea 4: Seasonal trends**
Could we predict seasonal keyword spikes and pre-generate content?

**Idea 5: LLM citation tracking**
Could we detect when our content is cited by ChatGPT/Claude/Perplexity?

**Idea 6: Content refresh cycle**
Could we identify older articles that need updating and auto-queue them for refresh?

**Idea 7: Expert interviews**
Could we identify key voices in each topic area and suggest outreach for quotes/interviews?

### Technology Evolution

**When might we need a database?**
- 1,000+ articles published
- Complex querying requirements
- Multiple concurrent users
- Real-time analytics needs

**When might we need a backend service?**
- Real-time monitoring required
- Webhook integrations multiply
- Complex orchestration logic
- Need for job queues

**When might we need a custom UI?**
- Non-technical users need to review
- Clients need to access the system
- Complex editing workflows
- Advanced analytics visualisation

---

## Appendix: AI Night School ICP (Current)
```json
{
  "name": "ai_night_school",
  "audience": "Business leaders and executives",
  "characteristics": {
    "mindset": "Overwhelmed by AI hype but know they need to act",
    "time": "Time-poor (can't do lengthy courses)",
    "needs": "Practical implementation guidance, not theory",
    "focus": "ROI and business value"
  },
  "demographics": {
    "age_range": "35-55",
    "job_titles": [
      "CEO",
      "CTO",
      "COO",
      "VP Product",
      "Head of Operations",
      "Managing Director",
      "General Manager"
    ],
    "company_size": "50-5000 employees",
    "industries": [
      "Professional services",
      "Technology",
      "Financial services",
      "Healthcare",
      "Manufacturing"
    ]
  },
  "pain_points": [
    "Where do I start with AI?",
    "How do I get my team on board?",
    "What's the actual ROI?",
    "How do I avoid wasting money on AI vendors?",
    "What should I do first?",
    "How do I know if an AI use case is worth pursuing?",
    "What are the risks I should be aware of?"
  ],
  "reading_habits": [
    "Harvard Business Review",
    "TechCrunch",
    "Business Insider",
    "MIT Technology Review",
    "The Economist (tech section)",
    "LinkedIn (thought leaders)",
    "Industry-specific publications",
    "Morning Brew",
    "The Information"
  ],
  "search_behaviour": [
    "How to implement AI in [industry]",
    "AI ROI calculator",
    "AI adoption strategy",
    "Best AI tools for [function]",
    "AI implementation checklist",
    "AI risks for business",
    "How to train team on AI"
  ]
}
```

---

## Appendix: Content Quality Standards

### What Makes a Good Response Article?

1. **Adds Value**: Doesn't just summarise the source, adds perspective, examples, or actionable steps
2. **On-Brand**: Matches Hugo's ToV (pragmatic, practical, anti-hype)
3. **SEO-Friendly**: Includes target keywords naturally, good structure with headers
4. **Linkable**: Other publications would want to link to it
5. **Actionable**: Reader can do something with the information
6. **Accurate**: Doesn't misrepresent the source article or make false claims

### Red Flags (Auto-Reject)

- Plagiarises source content
- Makes factual errors
- Contains generic AI-sounding phrases ("in today's rapidly evolving landscape...")
- Doesn't reference source article
- Keyword stuffing
- No clear value-add over source

---

## Change Log

**16 November 2024**: Initial planning document created
**Next review**: After Phase 1a completion (estimated end of November 2024)

---

*This is a living document. Update as we learn and iterate.*
