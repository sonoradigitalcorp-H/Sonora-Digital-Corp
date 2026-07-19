# openclaw-browser — OpenClaw Browser Plugin

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-OCB-001

---

## 1. Business Objective

Execute headless browser automation via the OpenClaw gateway for scraping, testing, and screenshot capture.

## 2. Inputs (Gherkin)

```gherkin
Given OpenClaw gateway is running
When a URL needs to be visited for scraping
Or a page needs screenshot capture
Or a form needs automated interaction
```

## 3. Outputs (Gherkin)

```gherkin
Then browser navigates to target URL
And page content is extracted as structured data
And screenshots are saved to storage
And form interactions are completed
```

## 4. Events

```
Events:
- openclaw:browser:navigated: page loaded successfully
- openclaw:browser:scraped: content extracted
- openclaw:browser:screenshot: capture saved
```

## 5. Dependencies

```
Dependencies:
- OpenClaw gateway: port 18789
- Headless browser: Chromium via Puppeteer/Playwright
- Storage: screenshot and data output directory
```

## 6. Tools

```
Tools:
- openclaw_execute(browser_*): navigate, scrape, screenshot, interact
```

## 7. Policies

```
Policies:
- Rate limits: max 1 request per second per domain
- Robots.txt: must be respected for scraping jobs
- Session data: browser sessions must be isolated per request
- Screenshots: auto-delete after 24 hours unless flagged
```

## 8. Success Metrics

```gherkin
Success Metrics:
- page_load_time: Given URL When loaded Then seconds
  Target: < 5 s
- scrape_completion: Given scrape requests When data returned Then percentage
  Target: > 95%
```

## 9. Failure Conditions

```
Failure Conditions:
- Page timeout: browser takes > 30s to load (increase timeout or skip)
- CAPTCHA: site blocks automation (fall back to alternative source)
- Resource exhaustion: too many concurrent browser sessions (limit pool)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If timeout → retry with extended timeout, skip if persistent
2. If CAPTCHA → log blocked domain, use API alternative if available
3. If resource exhaustion → reduce concurrent sessions, kill idle browsers
4. Log all attempts to state/logs/skills/openclaw-browser.log
```

## 11. Business Value

```
Business Value: Headless browser automation integrated into any workflow without managing browser infrastructure.
```

## 12. Parent OS

```
Parent OS: Dev
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: TBD
- Events: openclaw:browser:navigated, openclaw:browser:scraped, openclaw:browser:screenshot
- Logs: state/logs/skills/openclaw-browser.log
```
