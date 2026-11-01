# Project admin guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for the project *Admin*. You decide who is in the project and with which role, and you set the project defaults. You can also do everything a QC and a Dev can do: see the [QC guide](qc.md) and the [Dev guide](dev.md). Workspace admins act as Admin in every project.

## Rules

| Rule | Detail |
| --- | --- |
| One role per person | Each member has exactly one project role: Admin, PM, BA, QC, Dev or Viewer. |
| At least one Admin | The last Admin cannot be removed or given another role. |
| Who can be added | Active users and invited users who have not accepted yet. Deactivated users cannot be added. |
| Archived projects | Members and settings are read-only, like everything else. |

The rights of each role are in the [permission matrix](README.md#permission-matrix).

## Manage members

Open **Members** in the sidebar (`/projects/{KEY}/members`).

### Add a member

1. Select **Add member**.
2. Search by name or email. Only users without access to the project are listed; invited users show "(invited)".
3. Pick the **Role** and select **Add**.

If the person is not in the workspace yet, ask a workspace admin to invite them first.

### Change a role

1. Open the role list on the person's row.
2. Pick the new role. It is saved at once and applies to their Claude tokens too.

### Remove a member

1. Select the remove button on the row and confirm with **Remove**.
2. They lose access to the project. Their history stays. If you remove yourself, you lose access too.

> Screenshot to add: project-members.png: the members table with statuses, role lists and Add member.

## Project settings

Open **Settings** in the sidebar (`/projects/{KEY}/settings`). Select **Save** in each card after a change.

| Card | What to set |
| --- | --- |
| **General** | Name, description and the Jira board. The key cannot be changed. |
| **Defaults** | **Default environment**: used when a run does not pick one. Create environments first under **Test data**, **Environments** tab. |
| **Allowed file types** | The MIME types members may upload as test files and evidence. Screenshots from runs are always allowed. Use **Reset to defaults** to go back. |
| **Archive project** | Shown to workspace admins only. Makes the project read-only for everyone. |

### File types that features need

| Feature | Types to keep allowed |
| --- | --- |
| Test case import (.xlsx, .csv) | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `text/csv` |
| Test data import (.env, JSON, YAML) | `text/plain` or `application/json` |
| Screenshots from Claude runs | Always allowed, nothing to set |

The defaults cover images, PDF, text, CSV, JSON, Word and Excel files. Keep at least one type.

> Screenshot to add: project-settings.png: the settings page with General, Defaults and Allowed file types.

## First setup of a project

1. Add the members with their roles: at least one PM or BA, one QC and one Dev.
2. Ask a PM or BA to select **Sync from Jira** on **Stories**.
3. Ask QC or Dev to add the environments on `/projects/{KEY}/test-data?tab=environments`.
4. Pick the **Default environment** in the settings.
5. Check **Allowed file types** if your team imports spreadsheets or data files.
6. Ask each Dev to connect Claude, as in the [Dev guide](dev.md#connect-claude).

## What only Admin can do in a project

- Change members and settings.
- Finish a manual run that someone else started, for example when that person is away: open it from **Runs**, select **Continue recording**, then **Finish run**. Without that, a run with no activity for 4 hours is aborted on its own.
- Every right of QC and Dev at once: write cases, sign off stories, mark failures fixed and verify them.

## Next

- [QC guide](qc.md)
- [Dev guide](dev.md)
- [Sprint workflow](sprint-workflow.md)
