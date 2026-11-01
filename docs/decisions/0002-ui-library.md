# 0002. UI library: Mantine 9 with a custom Tessio theme

**Status:** Accepted. Amends [0001](0001-frontend-stack.md) (components are no longer framework-free).
**Date:** 2026-10-31

## Context

- We want ready-styled, good-looking components (button, text input, date picker, file upload…) so we don't style everything from scratch.
- We want as few libraries as possible.
- Styles must stay easy to debug: plain CSS / SCSS, no CSS-in-JS or Tailwind.
- The team knows Mantine well from years of use.

## Options considered

1. **Mantine 9**: complete, ready-styled, styles are plain CSS with readable class names, one package family for components, dates, forms, notifications, file upload, command search.
2. **IBM Carbon**: built in SCSS, complete, but a strong corporate look that is hard to change.
3. **Headless libraries (Base UI, React Aria)**: full design freedom, but every component must be styled by us.
4. **Tailwind or CSS-in-JS libraries (shadcn/ui, HeroUI, Ant Design, Chakra UI)**: against the SCSS / easy-debugging requirement.

## Decision

Use **Mantine 9** for all UI components, with a **custom Tessio theme** so the app doesn't look like a default Mantine app. Our own layout and page styles stay in **SCSS modules** that use Mantine's CSS variables.

### Packages (one family, one version)

| Package | For |
| --- | --- |
| `@mantine/core`, `@mantine/hooks` | Components and hooks |
| `@mantine/dates` (+ `dayjs`) | Date and time pickers |
| `@mantine/form` | Forms and validation |
| `@mantine/dropzone` | File upload (test case files, manual-run screenshots) |
| `@mantine/spotlight` | Command search (later) |

Plus:

- `@tabler/icons-react` for icons, the set Mantine's own docs and examples use.
- `sonner` for toasts (instead of `@mantine/notifications`), chosen for its look and stacking behavior. It follows Mantine's light/dark scheme through `DSToaster`. Features never import `sonner`: they call `useShowToast()` from `client/src/shared/hooks/use-show-toast.ts` (`showSuccessToast`, `showErrorToast`, `showInfoToast`, `showWarningToast`).

### Tessio theme

| Setting | Value |
| --- | --- |
| Primary color | `tessio` blue: `#EFF6FF` `#DBEAFE` `#BFDBFE` `#93C5FD` `#60A5FA` `#3B82F6` `#2563EB` `#1D4ED8` `#1E40AF` `#1E3A8A` |
| Primary shade | 6 (`#2563EB`) in both themes, so white text on filled buttons meets WCAG AA. The lighter `#60A5FA` is used only for links and the active nav item in dark mode (`--color-accent`). Danger buttons use `red.8`. |
| Font | Geist (sans and mono) |
| Font sizes | xs 12 · sm 14 · md 16 · lg 20 · xl 24 |
| Radius | xs 4 · sm 6 · md 10 (default) · lg 14 · xl 20 |
| Spacing | xs 8 · sm 12 · md 16 · lg 24 · xl 32 |
| Default component size | `sm` (data-dense screens) |
| Light / dark | Mantine color-scheme manager: follows the OS by default, switch in the UI, saved per user |

## Consequences

- Mantine's theme is the **single source** of colors, sizes and radius. `client/src/styles/_tokens.scss` is reduced to app-specific tokens (status colors, sidebar width) mapped onto Mantine variables.
- Light/dark is handled by Mantine's color-scheme manager instead of our own `data-theme` switch. Our SCSS tokens use native `light-dark()`, which follows Mantine's switch because Mantine sets `color-scheme` on the page. This needs the `browserslist` in `client/package.json` (Chrome/Edge 123, Firefox 120, Safari 17.5); with older targets Next.js rewrites `light-dark()` into a fallback that breaks.
- Mantine CSS is loaded as `styles.layer.css` (inside `@layer mantine`), so our unlayered styles always win regardless of import order.
- The current placeholder components (`client/src/components/ui/*`) are replaced by Mantine components.
- Mobbin references now guide the theme and component variants, not hand-built components.
- Mantine's basic `Table` covers MVP lists; a richer data table (sorting, pagination) is a later decision.
