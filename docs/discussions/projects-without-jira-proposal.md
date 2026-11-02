# Projects without Jira: stories and AC written in Tessio

**Status:** Accepted
**Date:** 2026-11-01
**WBS:** [3.3.5](../wbs/wbs.md#33-projects) (project without Jira), [3.5.7](../wbs/wbs.md#35-sprints--user-stories-synced-from-jira) (stories written in Tessio)
**Related:** [projects spec](../spec/projects.md), [sprints and stories spec](../spec/sprints-and-stories.md)

## Decisions at a glance

| Area | Decision (Peter, 2026-11-01; details are Claude's common-case defaults) |
| --- | --- |
| Project | A workspace admin can create a project **without Jira**, even when no Jira connection is set. |
| Stories | In a project without Jira, stories and their AC are written in Tessio. |
| Story keys | `<PROJECT KEY>-<n>`, like `SHOP-12`, so every screen, MCP tool and skill keeps working unchanged. |
| Who writes stories | Admin, PM, BA and QC. |
| Sprints | None in a project without Jira. Stories are listed without a sprint. |
| Mixing | A project is either linked to Jira or not. Linking a project without Jira to Jira later is out of scope. |

## 1. Why

Creating a project needs a Jira connection, and every story comes from a Jira sync. Without Jira access nobody can try Tessio at all, and a team that doesn't use Jira can't use it either.

## 2. Changes

**Projects**
- `projects.jira_project_key` and `jira_board_id` become nullable. A project without them is a project without Jira, shown as "Stories written in Tessio".
- The create form gets a choice: "Link a Jira project" or "Write stories in Tessio". Without a Jira connection, only the second is offered, instead of today's refusal.
- In a project without Jira, "Sync from Jira" is hidden and refused (`JIRA_NOT_CONFIGURED`), and the sprints page says "This project has no sprints".

**Stories**
- `stories.source`: `jira` or `tessio`. As built, the `jira_*` columns stay required and get placeholders for `tessio` stories (see WBS planning assumption 3.5.7), so no reader had to change.
- A `story_key_counters` row per project gives the next number. Keys never repeat, even after a delete.
- New capability `story.edit` (Admin, PM, BA, QC), only in projects without Jira:
  - `POST /api/projects/{project_key}/stories`: title (1 to 255 characters), description (plain text, up to 20 000 characters) and AC (a list of 0 to 50 texts, each up to 2000 characters).
  - `PATCH …/stories/{story_key}`: the same fields.
  - `DELETE …/stories/{story_key}`: only when the story has no test cases, runs or gaps (`CONFLICT` otherwise).
- AC keep today's rules. Codes come from the position (`AC1`, `AC2`…). A removed AC is kept for history. When an AC's text changes or it's removed, the linked cases get the **Needs review** flag through the same use case the Jira sync uses.

**Screens**
- The story list gets "New story" for `story.edit`. The story detail gets "Edit" and "Delete".
- The editor: title, description, and an AC list where each row can be added, edited, moved and removed.
- The story header shows "Written in Tessio" instead of the Jira status and link.

**Everything else** works unchanged on these stories: test cases, readiness review, runs, traceability, failures, sign-off and the Claude skills.

## 3. Not in this proposal

- Sprints in projects without Jira.
- Linking such a project to Jira later, or moving stories between the two kinds.
- Rich text in the description.

## 4. Open points

- Bulk creation of stories from a file is not needed for now (Peter, 2026-11-01).
