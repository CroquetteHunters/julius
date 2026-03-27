---
name: Business logic verification before reporting
description: Always verify that a finding is not "by design" before reporting - check company service, docs, competitors
type: feedback
---

Before reporting data exposure, information leak, or access control findings in bug bounty, ALWAYS verify the behavior is not intended ("by design").

**Why:** In the hitta.se bounty (2026-03), we assumed sensitive data exposure was a vulnerability when it was actually the core service feature (people-search engine). This wastes time and damages researcher reputation.

**How to apply:** During the Pre-Submission Gate, run these checks:
1. Understand what the company actually does (is data exposure their product?)
2. Check ToS, Privacy Policy, FAQ, API docs for justification
3. Compare with competitors in the same industry
4. Apply the "would a customer complain?" heuristic
5. If in doubt, ask the user before reporting
