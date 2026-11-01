# Open questions

Add questions as they come up. When one is answered, note the answer and link the ADR or spec it produced.

| # | Question | Why it matters | Answer / link |
| --- | --- | --- | --- |
| 1 | Does Tessio execute tests itself, or ingest results from existing CI? | Drives the whole server design (workers and browsers vs. a report-ingest API). | **Neither.** Claude runs tests from the developer's extension; testers run manual cases. Tessio orchestrates through MCP. See [testing-workflow-proposal.md](testing-workflow-proposal.md). |
| 2 | Which frameworks must v1 support: Playwright only, or Cypress/Selenium too? | Determines report parsers and runner images. | **Not applicable.** Tests are step-by-step cases run by Claude or by hand, not framework code. |
| 3 | Single team, or multi-tenant SaaS? | Auth, data isolation, billing. | **One company** (single tenant), multiple projects, one role per person per project. See [platform-features-proposal.md](platform-features-proposal.md). |
| 4 | Do we need live run progress in v1? | Real-time transport (SSE / WebSockets). | **Yes**, one update per test case, over server-sent events. See [server-proposal.md](server-proposal.md) §10 and [ADR 0004](../decisions/0004-backend-stack.md). |
| 5 | Where are screenshots stored, and for how long? | Storage cost, object storage choice. | Every step of a Claude run gets a screenshot, **kept forever**. RustFS in Docker for MVP ([ADR 0005](../decisions/0005-local-object-storage.md), MinIO images can no longer be pulled), RustFS on the VPS in production ([ADR 0009](../decisions/0009-production-storage-and-proxy.md)). |
| 6 | Who is the primary user for v1: QA engineers, developers or leads? | Which screens get the most design attention. | |
| 7 | How are AC written in Jira: description text, a custom field, or sub-tasks? | How the Jira sync reads AC. | **A list in the story description.** |
| 8 | Are gap-question answers posted back to the Jira story as comments? | Whether the Jira sync also writes. | **No.** Sync stays read-only. |
