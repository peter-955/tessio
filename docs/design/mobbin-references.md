# Mobbin references

**Status:** In discussion

A log of the Mobbin screens and components we adopt, so we remember where each design came from.

## How to add a reference

1. Add a row below with the Mobbin link and what we're taking from it.
2. Build the component in `client/src/components/ui/` using tokens from `client/src/styles/_tokens.scss`, with no hard-coded colors.
3. Set the status to `Built` and link the component file.

## References

| Component / screen | Mobbin link | What we take from it | Tessio component | Status |
| --- | --- | --- | --- | --- |
| *example: Sidebar navigation* | *link* | *grouping, active state* | `components/layout/Sidebar.tsx` | Placeholder |

## Current placeholder components

These exist only so the prototype works. Replace or restyle them as Mobbin references come in:

- `layout/Sidebar`, `layout/AppShell`
- `ui/Button`, `ui/Card`, `ui/PageHeader`, `ui/StatusBadge`, `ui/Table.module.scss`
- `runs/RunsTable`, `runs/RunsExplorer` (status filter chips)
