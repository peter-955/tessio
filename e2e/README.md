# Tessio end-to-end tests

A Playwright (Chromium) suite that drives the real app the way a team uses it: invite, two-factor sign-in, project, Jira sync, test case, gap, manual run, failure and sign-off. It also checks the phone layout at 375 px and the focused-input border in the light and dark themes.

The suite runs against its own Docker stack (`compose.e2e.yml`, project `tessio-e2e`), built from `../server` and `../client`, with a fake Jira. Your dev stack, its data and its rate limits are not touched.

## Run it

Requires Node 24 and Docker.

```bash
cd e2e
npm install
npx playwright install chromium
npm run stack:up          # builds and starts the stack, waits until every service is healthy
npm test                  # seeds the e2e database, then runs tests/01 … tests/11 in order
npm run report            # opens the HTML report (playwright-report/index.html)
npm run stack:down        # stops the stack and deletes its volumes
```

`npm run test:headed` shows the browser. `npm run fake-jira` starts the fake Jira on its own (port 3000, or `PORT`).

## How it works

- **Order matters.** The flow is one story told across numbered spec files: each file builds on the data the previous ones created. Playwright runs them alphabetically with one worker, no retries, and stops at the first failure.
- **Seed.** `support/global-setup.ts` runs `python -m app.commands.seed_e2e` inside the `api` container. The command refuses any database whose name does not end in `_e2e`, empties every table, creates the workspace owner with a confirmed authenticator key, and clears the rate-limit counters in Redis. The owner's credentials are passed as arguments from `support/constants/e2e-users.constant.ts`.
- **Users.** Each role (owner, QC, dev) signs in once; its browser state is saved under `.state/` and reused by the `ownerPage`, `qcPage` and `devPage` fixtures. The QC and dev keys come from the two-factor setup response, and invite links are read from Mailpit.
- **Fake Jira.** `fake-jira/server.ts` serves the Jira Cloud endpoints the server calls (myself, project search, boards, sprints, issue search) with the fixed data in `fake-jira/jira-fixtures.ts`: project SHOP, board "SHOP board", active sprint 11 with SHOP-1 (3 acceptance criteria), SHOP-2 and the sub-task SHOP-3.
- **Selectors.** Elements are found by role and accessible name, using the English texts from `client/src/lib/i18n/locales/en/*.json`.

## Ports

| Service            | Host port |
| ------------------ | --------- |
| Client             | 3211      |
| API                | 3212      |
| Mailpit UI and API | 3217      |
| RustFS (S3)        | 3218      |
| Fake Jira          | 3219      |

## Environment variables

| Variable                 | Default                 | Use                                                                                                                     |
| ------------------------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `E2E_BASE_URL`           | `http://localhost:3211` | The client the browser opens                                                                                            |
| `E2E_MAILPIT_URL`        | `http://localhost:3217` | Where invite emails are read                                                                                            |
| `E2E_FAKE_JIRA_SITE_URL` | `http://fake-jira:3000` | The Jira site URL entered in workspace settings, as the API container sees it                                           |
| `E2E_SEED_MODE`          | `compose`               | `compose` seeds through `docker compose exec api`; `local` runs `uv run python -m app.commands.seed_e2e` in `../server` |
| `E2E_DATABASE_URL`       | none                    | Required in `local` mode: an asyncpg URL to a database whose name ends in `_e2e`                                        |
| `E2E_REUSE_STATE`        | unset                   | `1` skips the reset and the seed and keeps `.state/`, to re-run one spec on top of an earlier full run                  |

## Local mode (dev stack)

To run the suite against a dev server instead of the e2e stack, point the variables at it and give the seed its own `_e2e` database:

```bash
createdb -h localhost -p 3203 -U tessio tessio_e2e
DATABASE_URL=postgresql+asyncpg://tessio:tessio@localhost:3203/tessio_e2e uv run alembic upgrade head   # in ../server
E2E_SEED_MODE=local \
E2E_DATABASE_URL=postgresql+asyncpg://tessio:tessio@localhost:3203/tessio_e2e \
E2E_BASE_URL=http://localhost:3201 \
E2E_MAILPIT_URL=http://localhost:3207 \
E2E_FAKE_JIRA_SITE_URL=http://localhost:3000 \
npm test
```

The dev API and worker must use that same `tessio_e2e` database, and `npm run fake-jira` must be running.

## Re-run one spec

After a full run, keep the data and re-run a single file:

```bash
E2E_REUSE_STATE=1 npx playwright test tests/10-mobile-layout.spec.ts
```

## CI

`.github/workflows/e2e.yml` runs the suite on every pull request and on pushes to `main`. On failure it uploads the HTML report, the traces and screenshots, and the stack logs (`stack.log`) for 7 days.

## What it does not cover

- File uploads (evidence, test files, avatars): the bucket CORS stays a manual check.
- A real Jira site: the payloads follow the Jira Cloud docs, but a check against a real site is still open (WBS 1.7.4).
- Claude runs through MCP: the server tests cover them.
