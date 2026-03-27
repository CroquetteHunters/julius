---
name: Engagement 559 - SLIDES Presentation Maker 3.1
description: DefectDojo engagement 559 for Slidesgo Presentation Maker. 15 SAST findings pending production validation and upload.
type: project
---

## Engagement 559 — SLIDES Presentation Maker 3.1

**DefectDojo**: https://defectdojo.internal/engagement/559
**API Token**: REDACTED_DEFECTDOJO_TOKEN
**Product ID**: 4
**Repo**: freepik-company/slidesgo
**Production URL**: https://slidesgo.com/ai/presentation-maker
**JIRA**: SEC-3134
**Contact**: Érika Hevilla

**Status (2026-03-26)**:
- 15 local SAST findings written to `outputs/defectdojo-slides-pmaker-3.1/findings/finding-001..015/report.md`
- 0 findings uploaded to DefectDojo (no tests created yet)
- No evidence/screenshots captured yet
- App deployed to production — ready for dynamic validation

**Why:** Code review findings need production validation before upload. Only PoC-confirmed findings should go to DD.

**How to apply:** When user says "continua":
1. Connect via Burp Suite MCP for authenticated testing
2. Validate each of the 15 findings against https://slidesgo.com/ai/presentation-maker
3. Capture evidence (HTTP requests/responses, screenshots) for confirmed findings
4. Discard/reclassify unconfirmable findings
5. Upload only validated findings to DD engagement 559 with active=false, verified=false

**Findings summary:**

| # | Title | Sev | CVSS | CWE | Key file |
|---|-------|-----|------|-----|----------|
| 001 | SSRF via unvalidated URL in webhook image handler | High | 7.5 | 918 | SlideImageRedisManager.php |
| 002 | TOCTOU race condition bypasses generation limits | Medium | 5.3 | 367 | GenerateAiPresentation.php |
| 003 | QA request cookie spoofing bypasses all rate limits | Medium | 4.2 | 807 | helpers.php |
| 004 | Generation not recorded on LLM/GCS failure | Medium | 4.3 | 799 | GenerateAiPresentation.php |
| 005 | Webhook signature verification skipped when secret empty | Medium | 4.8 | 345 | AiImageWebhookController.php |
| 006 | Webhook query param cross-presentation attribution | Low | 3.7 | 639 | AiImageWebhookController.php |
| 007 | GCS path traversal via unsanitized Redis values | Medium | 4.4 | 22 | SlideImageRedisManager.php |
| 008 | Concurrency lock before validation enables self-DoS | Medium | 4.3 | 400 | GenerateContentController.php |
| 009 | Stored XSS in slide snapshot fields | Medium | 5.4 | 79 | CreateReportController.php |
| 010 | Missing CSRF on state-mutating API endpoints | Medium | 4.3 | 352 | api.php |
| 011 | Non-atomic Redis pipeline state corruption | Low | 2.2 | 362 | SlideImageRedisManager.php |
| 012 | Auth failures masked as 400 (IDOR timing oracle) | Medium | 4.3 | 209 | GenerateSlideImagesController.php |
| 013 | Mass assignment open on generation log model | Low | 2.2 | 915 | AiPresentationGenerationLog.php |
| 014 | v-html DOM XSS pattern | Medium | 4.4 | 79 | ReportIssuePopover.vue |
| 015 | Verbose console.error exposes internal state | Medium | 4.0 | 532 | useSlideImages.js |

**Priority for dynamic validation:**
- HIGH: F001 (SSRF), F009 (Stored XSS), F005 (Webhook bypass), F002 (race condition)
- MEDIUM: F003, F008, F010, F012, F014, F015
- LOW/hard to validate externally: F004, F006, F007, F011, F013 (internal/Redis-dependent)
