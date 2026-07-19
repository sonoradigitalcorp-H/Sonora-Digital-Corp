# skills/social — Social Media Trend Research and Analysis

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-SOC-001

---

## 1. Business Objective

Research social media trends in minutes using Firecrawl scrapers and LLM analysis — identifying viral opportunities, content gaps, and platform-specific strategies across TikTok, Instagram, YouTube, and X.

## 2. Inputs (Gherkin)

```gherkin
Given a target market or niche is defined (genre, location, demographic)
And a research query specifies platforms and time horizon
When the social research pipeline is triggered (manual or scheduled at 10:00)
```

## 3. Outputs (Gherkin)

```gherkin
Then trends are scraped from configured social platforms
And each trend is analyzed for relevance, virality potential, and competition
And a structured research report is generated with actionable recommendations
And the report is saved to Engram for future reference
```

## 4. Events

```
Events:
- social:research:completed: a research cycle finished
- social:trend:identified: a trending topic or pattern was detected
- social:opportunity:flagged: a high-potential content gap was found
```

## 5. Dependencies

```
Dependencies:
- Firecrawl API: service — web scraping and crawling
- Browser runtime: service — JavaScript-rendered page extraction
- LLM provider: service — trend analysis and summarization
- Engram: service — trend history and research storage
- RAG index: data — historical context for trend comparison
```

## 6. Tools

```
Tools:
- firecrawl_crawl: crawl social platforms for trending content
- firecrawl_scrape: extract structured data from individual pages
- llm_chat: analyze trends, identify patterns, generate recommendations
```

## 7. Policies

```
Policies:
- Respect robots.txt and rate limits for all scraped platforms
- Cache results for 1 hour to avoid redundant scraping
- Never store user PII from scraped content
- Trend analysis must include confidence score
- All research must be timestamped and source-attributed
- Research must complete within 10 minutes
```

## 8. Success Metrics

```gherkin
Success Metrics:
- research_time: Given query triggered When report generated Then minutes
  Target: < 5 min
- trend_accuracy: Given identified trends When validated against actual data Then accuracy
  Target: > 80%
- platform_coverage: Given configured platforms When scraped Then success rate per platform
  Target: > 90%
```

## 9. Failure Conditions

```
Failure Conditions:
- Platform blocks: social site returns captcha or block page (detect via response content)
- Rate limit hit: API returns 429 (detect via HTTP status)
- Empty results: no trends found for query (detect via result set size)
- LLM hallucination: analysis includes fabricated data (detect via source verification)
- Stale cache: returning outdated trends (detect via cache age check)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If platform blocks → rotate user-agent, add delay, retry once
2. If rate limited → wait 60s, reduce concurrency, retry
3. If empty results → broaden query, try alternative platforms
4. If LLM hallucination suspected → regenerate with stricter grounding prompt
5. If cache stale → force refresh, extend cache window
6. Log all research to state/logs/skills/social.log
```

## 11. Business Value

```
Business Value: Social trend research in minutes. Identifies viral opportunities.
```

## 12. Parent OS

```
Parent OS: Sales
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-SOC-001
- Events: social:research:completed, social:trend:identified, social:opportunity:flagged
- Logs: state/logs/skills/social.log
```
