# Tessio brand

**Status:** Draft

## Logo

| File | Use |
| --- | --- |
| [tessio-mark.svg](tessio-mark.svg) | App icon, favicon, sidebar: blue tile with white mark |
| [tessio-mark-mono.svg](tessio-mark-mono.svg) | Single color; takes the surrounding text color (`currentColor`) |
| [tessio-logo.svg](tessio-logo.svg) | Mark + "Tessio" wordmark, for sign-in page and docs |

**Idea:** the ring is the "o" of Tessio and stands for the product under test. The check mark breaks out of the ring because the test passed.

**Notes:**
- The wordmark uses live text in Geist. Convert it to outlines before using it outside the app.
- Keep clear space around the mark of at least a quarter of its width.

## Color palette

Primary: **blue**, the color of trust.

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--color-accent` | `#2563EB` | `#60A5FA` | Primary buttons, links, active nav |
| `--color-accent-strong` | `#1D4ED8` | `#93C5FD` | Hover / pressed |
| `--color-accent-soft` | `#EFF6FF` | `#172554` | Selected rows, active nav background |
| `--color-bg` | `#F8FAFC` | `#0B1120` | Page background |
| `--color-surface` | `#FFFFFF` | `#111827` | Cards, tables, sidebar |
| `--color-border` | `#E2E8F0` | `#1F2937` | Borders, dividers |
| `--color-text` | `#0F172A` | `#E5E7EB` | Main text |
| `--color-text-muted` | `#64748B` | `#94A3B8` | Secondary text |

Logo gradient: `#3B82F6` → `#1D4ED8`.

Status colors (passed, failed, running, queued, skipped) are described in [platform-features-proposal.md](../../discussions/platform-features-proposal.md) §6. Since running is also blue, it uses a lighter tone than the brand accent so the two don't get confused.
