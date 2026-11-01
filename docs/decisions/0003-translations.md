# 0003. Translations: English, French, Vietnamese with react-i18next

**Status:** Accepted
**Date:** 2026-10-31

## Context

Tessio is used in English, French and Vietnamese, and the team's client conventions use `react-i18next`. Translations are set up from the start so no hard-coded text has to be moved later.

## Decision

- **Library:** `i18next` + `react-i18next`. Components call `useTranslation("<namespace>")`.
- **Languages:** `en` (default and fallback), `fr`, `vi`.
- **Files:** `client/src/lib/i18n/locales/<language>/<namespace>.json`, one namespace per module plus `common`, gathered by `locales/<language>/index.ts`.
- **Typed keys:** the English resources define the key types (`lib/i18n/i18next.d.ts`). A wrong key, or a French or Vietnamese file missing a key, fails `npm run typecheck`.
- **Language choice is stored in a cookie** (`tessio-language`). The server reads it and renders the page in that language, so there is no English flash and no hydration mismatch. Later the choice will also be saved in the user profile.
- **One i18n instance per request**, created in `AppProvider` and passed down with `I18nextProvider`. No global instance is shared between requests.
- **Dates and durations** go through `useFormatDate()` and `useFormatDuration()` in `client/src/shared/hooks/`. Dates are formatted in UTC without a localized time zone name, because Node and Chrome name it differently (French "TU" vs "UTC"), which breaks hydration.
- **Mantine date pickers** use the matching dayjs locale through `DatesProvider`.

## Consequences

- Pages render per request (`ƒ` in the build) instead of being prerendered, because the server reads the language cookie. This fits a signed-in app whose data will be per user anyway.
- Components that show text are client components. Server components only fetch data, handle "not found" and pass data to a client view.
- Mock data (suite names, descriptions, error messages) is content, not interface text, and stays untranslated.
- Page titles in the browser tab (`metadata`) are still English only.
