# Tessio client

Next.js 16 · TypeScript · SCSS modules · Mantine 9 ([ADR 0002](../docs/decisions/0002-ui-library.md)) · TanStack Query on a typed `openapi-fetch` client.

## Run

Start the server first (see the [root README](../README.md#run-locally)), then:

```bash
npm install
npm run dev        # http://localhost:3201
```

`next.config.ts` rewrites `/api/:path*` and `/mcp` to the server at `TESSIO_SERVER_URL` (default `http://localhost:3202`), so the browser sees one origin and the session cookie stays same-site.

## Checks

```bash
npm run typecheck
npm run lint
npm run format:check   # npm run format to fix
npm test               # Vitest (jsdom, Testing Library, vitest-axe)
npm run build
```

After a server API change, run `uv run python -m app.commands.export_openapi` in `server/` (it writes `src/lib/api/openapi.json`), then `npm run generate:api` here to regenerate `src/lib/api/openapi.type.ts`. CI fails if either file is out of date.

Commit messages are checked by commitlint (Conventional Commits, header ≤ 72 characters) through a husky `commit-msg` hook at the workspace root.

## Layout

```
src/
├── app/                    routes only: (app) and (auth) route groups, metadata + one page component
├── proxy.ts                Next.js 16 proxy (the renamed middleware): redirects to sign-in without a session cookie
├── modules/<feature>/      pages (<name>.tsx → <Name>Page), components/, hooks/{queries,mutations}, utils/, typing/
├── components/
│   ├── design-system/      DS* components: the only place that imports @mantine/*
│   └── <name>/             app-wide components: app-shell, project-context, runs-table, session-guard, status-badge
├── lib/<library>/          library setup: api (apiClient, openapi.json, generated types), dayjs, i18n (locales),
│                           mantine (theme and palette), react-query (query client), uploads (signed uploads)
├── shared/                 hooks (useAppQuery, useAppMutation, useLiveEvents…), providers, styles (tokens, mixins),
│                           typing, utils
└── test/                   Vitest setup, test providers and test utils
```

## Rules

- **UI comes from `@/components/design-system`.** Features never import `@mantine/*`; a missing component becomes a new `DS*` wrapper with narrow props (`type`, `size`, `isDisabled`, `isLoading`…).
- **Data fetching:** one hook per request in `modules/<feature>/hooks/queries` (`use-get-…`) or `hooks/mutations`, built on `useAppQuery` / `useAppMutation` (`@/shared/hooks/use-app-query`, `@/shared/hooks/use-app-mutation`) and `apiClient` (`@/lib/api/api-client`). Each query hook exports its key constant (for example `GET_RUNS_KEY`) and a typed query-key tuple. Live events invalidate queries through `LIVE_EVENT_QUERY_KEYS` in `shared/typing/constants/live-event-query-keys.constant.ts`: add your key to the event types that change its data.
- **Text** shown to users lives in `src/lib/i18n/locales/{en,fr,vi}/*.json` and is read with `useTranslation("<namespace>")`. Add every key to all three languages; typecheck fails otherwise. Dates and durations go through `useFormatDate()` / `useFormatDuration()` ([ADR 0003](../docs/decisions/0003-translations.md)).
- **Toasts** go through `useShowToast()` from `@/shared/hooks/use-show-toast`; never import `sonner` in a feature.
- **One file, one role**, named by its suffix: `.tsx` (one component), `.module.scss`, `use-*.ts`, `*.util.ts`, `*.constant.ts`, `*.type.ts`, `*.enum.ts`, `*.test.ts(x)`. No `index.ts` barrels outside the design system.
- **Styles** are `*.module.scss` using semantic tokens (`var(--color-text-muted)`, `var(--space-4)`) from `shared/styles/tokens/`. Breakpoints only through `@use "shared/styles/mixins" as *;`.
- **Colors** are defined once in the Mantine palette (`lib/mantine/mantine-colors.constant.ts`); semantic tokens map to it with `light-dark()`.
- **Code style** (enforced by ESLint): arrow functions only, braces on every `if`, no `any`, inline `type` imports, one component per file, no digit separators, no comments.
