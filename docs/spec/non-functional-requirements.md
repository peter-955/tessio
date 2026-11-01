# Non-functional requirements

**Status:** Draft · **Updated:** 2026-11-01

WBS 1.4 · Index: [README](README.md)

How Tessio must behave beyond its features: security, privacy, performance, storage growth, availability, observability, accessibility, languages, browser support and limits. Each row has an id `NFR-<AREA>-nn`, the value the code uses today, and how it is verified: a test path, a check, or "not measured". Rows marked **[ASSUME]** are new targets that the pilot should confirm.

Test paths are relative to the repo root. Server tests run with `cd server && uv run pytest`; client tests with `cd client && npm test`.

## SEC: security

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-SEC-01 | No public sign-up; users join by invite only | invite link valid 7 days, one use | `server/tests/api/auth/test_sign_in_flow.py`, `server/tests/api/users/test_workspace_users.py` |
| NFR-SEC-02 | Passwords are long, not breached, and slow to crack | at least 12 characters; checked against Pwned Passwords (k-anonymity range API); Argon2id (m=65536, t=3, p=4) | `server/tests/unit/test_pwned_passwords_checker.py`, `server/tests/api/auth/test_change_password.py`, `server/tests/api/auth/test_password_reset.py` |
| NFR-SEC-03 | Two-factor is required for everyone | TOTP, a used time step is refused; 10 single-use recovery codes | `server/tests/api/auth/test_sign_in_flow.py`, `server/tests/api/auth/test_own_two_factor.py` |
| NFR-SEC-04 | Sign-in lockout | 5 failed passwords or codes → locked 15 minutes (`SIGN_IN_LOCKED`, 429); unknown emails take the same time | `server/tests/api/auth/test_sign_in_lockout.py` |
| NFR-SEC-05 | Server-side sessions | half session 10 min; idle timeout 7 days; cookie `tessio_session` HttpOnly, SameSite=Lax, Secure, 30 days; tokens stored as SHA-256 | `server/tests/api/auth/test_sign_in_flow.py`, `server/tests/api/auth/test_delete_expired_sessions.py` |
| NFR-SEC-06 | Sessions end on risky changes | password change signs out other sessions; reset, own two-factor reset, admin two-factor reset, deactivation and sign-out-all end every session | `server/tests/api/auth/test_sign_out_all.py`, `server/tests/api/users/test_deactivate_reactivate.py`, `server/tests/api/users/test_reset_two_factor.py` |
| NFR-SEC-07 | Reset links do not reveal accounts | forgot-password always answers 204; link valid 30 minutes, one use | `server/tests/api/auth/test_password_reset.py` |
| NFR-SEC-08 | CSRF protection | every `POST`, `PUT`, `PATCH`, `DELETE` under `/api/` needs an allowed `Origin`, or no `Origin` and `Sec-Fetch-Site` same-origin or none; else `ORIGIN_NOT_ALLOWED` (403) | `server/tests/api/app/test_origin_check.py` |
| NFR-SEC-09 | Secrets encrypted at rest | AES-256-GCM; format: version byte, key id, 12-byte nonce, ciphertext; header bound as associated data | `server/tests/unit/shared/crypto/test_aes_gcm_secret_cipher.py` |
| NFR-SEC-10 | Key rotation | `TESSIO_ENCRYPTION_KEY` + `TESSIO_ENCRYPTION_KEY_ID` encrypt; `TESSIO_PREVIOUS_ENCRYPTION_KEYS` still decrypt; re-encrypting old values is Later | `server/tests/unit/shared/crypto/test_aes_gcm_secret_cipher.py` |
| NFR-SEC-11 | Secret values never leak into results | every step result, error, summary and report masked with `••••` against all of the environment's secret values (Claude and manual runs) | `server/tests/unit/shared/masking/test_secret_masker.py`, `server/tests/api/runs/test_record_case_result.py`, `server/tests/api/runs/manual/test_record_manual_case_result.py` |
| NFR-SEC-12 | Secret access is audited | each reveal writes `secret.reveal`; each value handed to Claude writes `secret.resolve` with the run id | `server/tests/api/files/test_record_audit_event.py`, `server/tests/api/test_data/test_data_items.py`, `server/tests/api/story_context/test_resolve_data.py` |
| NFR-SEC-13 | Secrets only for those who need them | reveal: Admin and QC; `resolve_data`: own running run only, keys the run uses only | `server/tests/api/test_data/test_data_permissions.py`, `server/tests/api/story_context/test_resolve_data.py` |
| NFR-SEC-14 | Project isolation | a non-member gets `NOT_FOUND` (404) for every project route and MCP call | `server/tests/permissions/test_postgres_project_access_resolver.py`, `server/tests/permissions/test_role_capabilities.py`, the per-module permission tests |
| NFR-SEC-15 | One permission table, checked on every call | `role_capabilities.py`; every use case calls `require` or `require_workspace` | `server/tests/permissions/test_role_capabilities.py`; capability audit in the W7.T1 security review |
| NFR-SEC-16 | Archived projects are read-only | every capability outside `READ_CAPABILITIES` refused with `PROJECT_ARCHIVED`, REST and MCP | `server/tests/permissions/test_role_capabilities.py`, `server/tests/api/gaps/test_gap_tools.py`, `server/tests/api/story_context/test_get_story_context.py` |
| NFR-SEC-17 | API tokens are narrow | one project each; `tsio_` prefix, stored as SHA-256, shown once; 30 days by default, 90 at most, 10 active; owner's current role re-checked on every call; no workspace-admin bypass | `server/tests/api/api_tokens/test_api_tokens.py`, `server/tests/api/api_tokens/test_authenticate_api_token.py` |
| NFR-SEC-18 | Uploads are limited by the storage server | signed POST with `content-length-range` 1 to 20 MB (2 MB avatars) and the exact content type; completion re-reads the object and deletes it when size or type differ | `server/tests/unit/shared/storage/test_s3_object_storage.py`, `server/tests/api/files/test_uploads.py` |
| NFR-SEC-19 | Files are private | downloads only through 5-minute signed links after `file.download`, and only for uploaded screenshots, test files, evidence and reports; import files are read only by the person who uploaded them; screenshot upload links only for the run's starter | `server/tests/api/files/test_uploads.py`, `server/tests/api/runs/test_screenshot_upload.py` |
| NFR-SEC-20 | Rate limits on the public auth routes | per client IP, counted in Redis: sign-in 20 per 15 min; two-factor and two-factor confirm 20 per 15 min; invite accept and password reset 20 per 15 min; forgot password 10 per hour per IP and 3 emails per hour per address (extra requests still answer 204). Over the limit: `RATE_LIMITED` (429) with `Retry-After`. Signed-in routes and MCP calls have no request limit | `server/tests/api/auth/test_rate_limits.py`; re-checked in `server/app` on 2026-11-01 (added by the W7.T1 security review) |

## PRIV: privacy

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-PRIV-01 | Store little about people | name, email, workspace role, avatar, language, theme, sign-in state; no tracking or analytics | code review of `server/app/modules/users` |
| NFR-PRIV-02 | Deactivate, never delete | a deactivated user cannot sign in, tokens stop working; their name stays on runs, answers and failures | `server/tests/api/users/test_deactivate_reactivate.py` |
| NFR-PRIV-03 | Data stays on our server | Postgres, Redis and object storage run on the team's own VPS; Tessio sends data only to Jira (read), SMTP and Pwned Passwords (a 5-character hash prefix) | code review; [ADR 0007](../decisions/0007-hosting-vps-docker.md) |
| NFR-PRIV-04 | Screenshots may show personal data of the tested app | kept forever, visible to project members only | not measured; the pilot should use test accounts |
| NFR-PRIV-05 | Personal data export or erasure on request | not built | not measured |

## PERF: performance

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-PERF-01 | API read latency at pilot scale **[ASSUME]** | p95 under 300 ms | not measured |
| NFR-PERF-02 | API write latency at pilot scale **[ASSUME]** | p95 under 800 ms (Jira calls excluded) | not measured |
| NFR-PERF-03 | Live update delay **[ASSUME]** | a live event reaches open browsers within 2 s | not measured; event delivery covered by `server/tests/api/live_events/test_stream_live_events.py` |
| NFR-PERF-04 | Claude token cost per case **[ASSUME]** | the `record_case_result` reply is about 30 tokens (`{"case_result_id": "…"}`); images are sent as file paths, never as data | reply shape: `server/tests/api/runs/test_record_case_result_tool.py`; tokens per case: not measured (WBS 5.7 open, `claude/scripts/measure-tokens.sh`) |
| NFR-PERF-05 | Jira sync never blocks the API | runs as the `jira.sync_project` job on the `jira` queue; one job per project | `server/tests/api/stories/test_sync_request.py`, `server/tests/unit/shared/queue/test_job_deduplication.py` |
| NFR-PERF-06 | Jira calls are bounded | 20 s timeout (5 s connect); up to 3 retries on 429 or 503, `Retry-After` at most 60 s | `server/tests/api/jira/test_httpx_jira_client.py` |
| NFR-PERF-07 | Readiness check is fast | each dependency check times out after 2 s | `server/tests/api/health/test_health.py` |

## STOR: storage growth

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-STOR-01 | Every step of a Claude run keeps a screenshot | one full-scale JPEG per step, about 46 KB (1400 × 845, spike 1.7.2) | spike 1.7.2 |
| NFR-STOR-02 | Screenshots are kept forever | no automatic deletion | code review (`files.delete_orphans` skips screenshots) |
| NFR-STOR-03 | Move old screenshots to cheaper storage after 90 days | **not built** (blocker: production object storage undecided, [ADR 0007](../decisions/0007-hosting-vps-docker.md)) | not measured |
| NFR-STOR-04 | Orphan uploads are cleaned up | files still `pending` after 1 day are deleted daily at 03:00; pending screenshots are marked missing instead | `server/tests/queue/test_delete_orphan_files.py`, `server/tests/unit/shared/queue/test_job_schedules.py` |
| NFR-STOR-05 | Expired sessions are cleaned up | daily at 03:30 | `server/tests/api/auth/test_delete_expired_sessions.py`, `server/tests/unit/shared/queue/test_job_schedules.py` |
| NFR-STOR-06 | Failed background jobs are kept for inspection | 7 days; finished jobs are removed at once; 5 attempts with a 30 s backoff | code review of `server/app/shared/queue/bullmq_job_queue.py`; no test covers the retention |
| NFR-STOR-07 | Other file sizes | test files and manual evidence up to 20 MB each; data imports 1 MB; case imports 5 MB; avatars 2 MB | `server/tests/api/files/test_uploads.py` |

### Worked estimate for screenshots

Screenshots per sprint = stories × cases per story × steps per case × runs per case. Size = screenshots × 46 KB (1 MB = 1000 KB). Re-runs only repeat the failed cases, so "runs per case" counts the first run plus the share of cases re-run.

| Scenario | Stories | Cases per story | Steps per case | Runs per case | Screenshots per sprint | Per sprint | Per year (26 sprints) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pilot team | 10 | 6 | 8 | 2 | 960 | about 44 MB | about 1.1 GB |
| Larger team | 30 | 10 | 10 | 3 | 9 000 | about 414 MB | about 10.8 GB |

Manual-run evidence, test files and imports come on top; the database itself grows by a few MB per sprint. Without the 90-day rule (NFR-STOR-03), all of it stays on the VPS disk.

## AVAIL: availability

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-AVAIL-01 | Hosting | one VPS with Docker Compose: caddy, client, api, worker, postgres, redis, rustfs ([compose.prod.yml](../../compose.prod.yml)); no high availability | `docker compose config` on compose.prod.yml; never deployed (blocker for WBS 7.3) |
| NFR-AVAIL-02 | Containers restart on failure | `restart: unless-stopped`; logs rotated at 10 MB × 5 files | code review of compose.prod.yml |
| NFR-AVAIL-03 | Migrations before each deploy | `alembic upgrade head` as a one-off container ([deploy/deploy.sh](../../deploy/deploy.sh)) | not measured |
| NFR-AVAIL-04 | Backups and disaster recovery | Later (WBS 7.5); none today | not measured |
| NFR-AVAIL-05 | A run left open does not block a story for ever | runs idle 4 hours are aborted every 15 minutes | `server/tests/api/runs/manual/test_abort_stale_runs.py`, `server/tests/unit/shared/queue/test_job_schedules.py` |

## OBS: observability

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-OBS-01 | Structured logs | JSON lines on stdout; level from `LOG_LEVEL` (default `INFO`) | `server/tests/unit/shared/logging/test_configure_logging.py`, `server/tests/unit/shared/logging/test_json_log_formatter.py` |
| NFR-OBS-02 | Error tracking | Sentry when `SENTRY_DSN` is set, tagged with `SENTRY_ENVIRONMENT` | `server/tests/unit/shared/logging/test_configure_logging.py` |
| NFR-OBS-03 | Liveness | `GET /api/health` answers `{"status": "ok"}` | `server/tests/api/health/test_health.py` |
| NFR-OBS-04 | Readiness | `GET /api/health/ready` checks Postgres and Redis (2 s each); 503 when one fails | `server/tests/api/health/test_health.py` |
| NFR-OBS-05 | Job dashboard is private | Bull Board only on `127.0.0.1:3205` behind a login, in the `ops` profile; not routed by Caddy | code review of compose.prod.yml and [deploy/Caddyfile](../../deploy/Caddyfile) |
| NFR-OBS-06 | Uptime monitoring | service not chosen | not measured |

## A11Y: accessibility

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-A11Y-01 | Conformance target | WCAG 2.2 AA | vitest-axe checks in the client tests (85 test files); full review in WBS 6.4 (W7.T2) |
| NFR-A11Y-02 | Readable text | 14 px floor for body text | W7.T2 review; the `--text-xs` (12 px) token is still used in a few stylesheets on 2026-11-01 |
| NFR-A11Y-03 | Colour contrast | AA contrast for text and controls in light and dark themes | `client/src/shared/styles/tokens/color-tokens.test.ts` |
| NFR-A11Y-04 | Status is never shown by colour alone | every status badge has a text label; AC and result cells carry a label or icon | W7.T2 review |
| NFR-A11Y-05 | Keyboard use | every action reachable by keyboard; "Skip to main content" link; visible focus | W7.T2 review |

## I18N: languages

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-I18N-01 | Three UI languages | English, French, Vietnamese (`en`, `fr`, `vi`), one namespace per module in `client/src/lib/i18n/locales/<language>/` ([ADR 0003](../decisions/0003-translations.md)) | `npm run typecheck` (key types come from the English files) |
| NFR-I18N-02 | The choice is saved per user | `language` on the user, saved with `PATCH /api/me`, applied after sign-in on every device | `server/tests/api/auth/test_me_profile.py` |
| NFR-I18N-03 | Jira content is not translated | AC markers are read in English, French and Vietnamese | `server/tests/unit/stories/test_acceptance_criteria_parser.py` |

## COMPAT: browsers and devices

| ID | Requirement | Value | How verified |
| --- | --- | --- | --- |
| NFR-COMPAT-01 | Browsers **[ASSUME]** | the latest two versions of Chrome, Edge, Firefox and Safari | not measured |
| NFR-COMPAT-02 | Small screens | no horizontal page scroll at 375 px; sidebar becomes a drawer below `md` | not measured in a browser (carry-over W2–W6) |
| NFR-COMPAT-03 | Claude side | Claude Code with the Tessio plugin and Claude in Chrome on the developer's machine; `python3` for the hook; `sips` (macOS) or `cwebp` for non-JPEG screenshots | `python3 -m unittest discover claude/hooks/tests` |

## LIMITS: maximums and page sizes

| ID | Item | Limit | Where in code |
| --- | --- | --- | --- |
| NFR-LIMITS-01 | File upload | 20 MB (avatar 2 MB) | `MAX_FILE_BYTES`, `MAX_AVATAR_BYTES` |
| NFR-LIMITS-02 | Upload link / screenshot upload link / download link | 15 min / 1 h / 5 min | `UPLOAD_LIFETIME`, `SCREENSHOT_UPLOAD_LIFETIME`, `DOWNLOAD_LINK_LIFETIME` |
| NFR-LIMITS-03 | Steps per test case | 100 | `MAX_STEPS` |
| NFR-LIMITS-04 | Step results per recorded case | 200 | `MAX_STEPS_PER_CASE` |
| NFR-LIMITS-05 | Test case title / long texts | 200 / 5000 characters | `MAX_TITLE_LENGTH`, `MAX_TEXT_LENGTH` |
| NFR-LIMITS-06 | AC links per case | 50 | `MAX_CRITERION_LINKS` |
| NFR-LIMITS-07 | Case import | 5 MB, 500 cases, 5000 rows | `MAX_CASE_IMPORT_BYTES`, `MAX_IMPORTED_CASES`, `MAX_IMPORT_ROWS` |
| NFR-LIMITS-08 | Test data value / data import | 10 000 characters / 1 MB, 1000 items | `MAX_DATA_ITEM_VALUE_LENGTH`, `MAX_IMPORT_BYTES`, `MAX_IMPORT_ITEMS` |
| NFR-LIMITS-09 | Run summary | 4000 characters | `MAX_SUMMARY_LENGTH` |
| NFR-LIMITS-10 | Run list | 50 by default, 200 at most | `DEFAULT_RUN_LIST_LIMIT`, `MAX_RUN_LIST_LIMIT` |
| NFR-LIMITS-11 | Gaps per `raise_gaps` call / gap inbox | 50 / 200 | `MAX_GAPS_PER_CALL`, `MAX_INBOX_SIZE` |
| NFR-LIMITS-12 | Gap question / answer | 2000 / 4000 characters | `MAX_QUESTION_LENGTH`, `MAX_ANSWER_LENGTH` |
| NFR-LIMITS-13 | Failure list / result history | 500 / 50 | `MAX_FAILURE_LIST_SIZE`, `MAX_RESULT_HISTORY_SIZE` |
| NFR-LIMITS-14 | My work items per section | 20 | `MAX_MY_WORK_ITEMS` |
| NFR-LIMITS-15 | Notifications page | 20 by default, 100 at most | `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` |
| NFR-LIMITS-16 | `resolve_data` keys per call | 50 | `MAX_RESOLVE_KEYS` |
| NFR-LIMITS-17 | Member candidates per search | 20 | `MAX_MEMBER_CANDIDATES` |
| NFR-LIMITS-18 | Active API tokens per user / lifetime | 10 / 1 to 90 days (default 30) | `MAXIMUM_ACTIVE_API_TOKENS`, `MAXIMUM_API_TOKEN_LIFETIME_DAYS` |
| NFR-LIMITS-19 | Allowed file types per project | 1 to 50 | `UpdateProjectRequest` |
| NFR-LIMITS-20 | Project key | `^[A-Z][A-Z0-9]{1,9}$` | `PROJECT_KEY_PATTERN` |
| NFR-LIMITS-21 | Stale run / stale sync | 4 hours / 15 minutes | `STALE_RUN_INACTIVITY`, `SYNC_STALE_AFTER` |
| NFR-LIMITS-22 | Closed sprints synced back | 30 days | `CLOSED_SPRINT_SYNC_WINDOW` |
| NFR-LIMITS-23 | Default allowed file types | png, jpeg, webp, gif, pdf, txt, csv, json, docx, xlsx | `DEFAULT_ALLOWED_FILE_TYPES` |

## Open points

- Rate limits: NFR-SEC-20 records the limits the security review (WBS 6.5, W7.T1) added while this doc was written. Signed-in routes and MCP calls are not limited; the pilot should confirm that is enough.
- Every **[ASSUME]** row needs a measurement during the pilot (WBS 8.4).
- The 90-day storage rule, backups, uptime monitoring and the production SMTP provider are blockers or Later items tracked in [wbs.md](../wbs/wbs.md).
