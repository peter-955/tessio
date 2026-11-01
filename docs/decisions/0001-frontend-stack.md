# 0001. Frontend stack: Next.js, TypeScript, SCSS

**Status:** Accepted. Amended by [0002](0002-ui-library.md) (Mantine as UI library).
**Date:** 2026-10-31

## Context

We want a client application early, to explore and imagine features before the backend is specified. UI components will be modeled on references from Mobbin.

## Decision

- **Next.js 16** (App Router, Turbopack) in `client/`
- **TypeScript** throughout
- **SCSS** via CSS Modules (`*.module.scss`), with no Tailwind
- Design tokens are CSS custom properties in `client/src/styles/_tokens.scss`, with light and dark values

## Consequences

- Components stay framework-free styling-wise, so Mobbin-inspired designs can be recreated directly in SCSS.
- Restyling (brand colors, spacing) happens in one tokens file.
- Next.js 16 has new conventions (async `params`, Cache Components, "instant" navigation validation). Check `client/node_modules/next/dist/docs/` before relying on older patterns.
- The backend stack is a separate, later decision.
