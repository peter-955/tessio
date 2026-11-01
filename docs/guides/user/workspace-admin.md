# Workspace admin guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for the *Owner* and for *Workspace admins*. You manage people, the Jira connection and projects. In every project you act as project Admin in the browser, so the [project admin guide](project-admin.md) applies to you too. A Claude token you create keeps only your real project role.

## Rules

| Rule | Detail |
| --- | --- |
| Only the owner changes workspace roles | A workspace admin cannot make someone a workspace admin or invite one. |
| No changes to yourself or the owner | Nobody can change their own account or the owner's account from `/users`. |
| Deactivation keeps history | The runs, results, gaps and test case versions of a deactivated person stay. |
| Two-factor is required | Everyone sets up an authenticator app at the first sign-in. |

## Manage users

Open **Users** in the sidebar (`/users`). Filter by name, email, status or workspace role.

### Invite someone

1. Select **Invite user**.
2. Enter the email and the name, and pick the workspace role: *Member* for most people.
3. Select **Send invite**. The link in the email is valid for 7 days.
4. Add the person to projects from each project's **Members** page. Invited people can be added before they accept.

If the link expired or the email got lost, open the person's actions menu and select **Resend invite**.

> Screenshot to add: users-list.png: the users table with statuses, two-factor column and the actions menu.

### Other actions

Each row has an actions menu.

| Action | What happens |
| --- | --- |
| **Change workspace role** | Owner only. Pick *Member* or *Workspace admin*, then **Save role**. |
| **Reset two-factor** | The person is signed out and sets up an authenticator app at the next sign-in. Use it when someone lost their phone and their recovery codes. |
| **Deactivate** | The person is signed out everywhere and their API tokens stop working. Their history is kept. Gaps and failures assigned to them show a *Deactivated* badge so others can reassign them. |
| **Reactivate** | The person can sign in again. If they never accepted the invite, a new one is sent. |
| **View project access** | Lists the projects and project roles of the person (`/users/{id}`). |

Deactivated people cannot be added to projects.

## Connect Jira

Tessio reads stories, sprints and AC from one Jira Cloud site. Set it up once for the workspace.

1. Open **Workspace settings** (`/settings`).
2. Under **Jira connection**, enter the site URL (for example `https://your-team.atlassian.net`), a Jira user email and that user's API token.
3. Select **Test and save**. Tessio checks the credentials before it saves them.

Any Jira user's email and API token work. Jira admin rights are not needed, but the user must be able to see the projects and boards you link. To change the token later, enter a new one; leave it empty to keep the saved token.

> Screenshot to add: jira-connection.png: the Jira connection form showing Connected and the account it uses.

## Create a project

Each Tessio project is linked to one Jira project and one board.

1. Open **Projects** (`/projects`) and select **New project** (`/projects/new`).
2. Pick the **Jira project** and the **Jira board**. A Jira project already linked to another Tessio project is not offered.
3. Enter the **Name** and the **Key**. The key is 2–10 capital letters or digits, starting with a letter, for example `SHOP`. It cannot be changed later.
4. Add a **Description** if you like, and select **Create project**.

You become the project Admin. Then add the members and set the project up, as in the [project admin guide](project-admin.md).

> Screenshot to add: new-project.png: the New project form with Jira project, board and key.

## Archive and unarchive

1. On `/projects`, open the project's actions menu and select **Archive**. You can also use **Archive project** at the bottom of the project's **Settings**. Only workspace admins see it there.
2. Confirm. Everyone keeps read access, but nothing can be changed. Secrets can still be revealed by the roles allowed to.
3. To undo, tick **Show archived**, open the menu and select **Unarchive**.

## Next

- [Project admin guide](project-admin.md)
- [Pilot checklist](../pilot.md) for the first sprint in Tessio
