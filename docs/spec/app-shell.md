# App shell and navigation

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.1 · Story prefix SHELL · Index: [README](README.md)

## Purpose

The frame around every signed-in page: the sidebar, the top bar, the mobile drawer, the saved theme and language, and the not-found and error pages. It works out which project the user is in and which sections they may open.

## Roles and capabilities

- Every signed-in user sees the shell. The [session guard](client-api.md#api-3-session-handling-wbs-3143) keeps signed-out users and half sessions out.
- Project sidebar items are shown by capability (table in SHELL-1). Workspace items are shown by workspace role.
- The shell itself writes nothing except the user's saved preferences (`PATCH /api/me`, own account, no capability).

## User stories

### SHELL-1 Project sidebar (WBS 3.1.1)

As a project member, I want a sidebar with the project's sections, so that I reach each part of the testing work in one click.

- AC1: Inside `/projects/[projectKey]`, the sidebar lists Dashboard, Sprints, Stories, Test cases, Runs, Failures, Test data, Members and Settings, in that order, each linking to `/projects/[projectKey]/<segment>`.
- AC2: An item shows only when the project's `capabilities` contain its capability: Dashboard and Members `project.view`, Sprints `sprint.view`, Stories `story.view`, Test cases `test_case.view`, Runs `run.view`, Failures `failure.view`, Test data `test_data.view`, Settings `project.edit`.
- AC3: On an archived project the `capabilities` list holds read capabilities only, so Settings is hidden.
- AC4: The workspace section always lists Projects (`/projects`). It lists Users (`/users`) and Workspace settings (`/settings`) only for the Owner and Workspace admins.
- AC5: Outside a project, only the workspace section shows, with the hint "Pick a project to see its sprints, stories and runs."
- AC6: A "Skip to main content" link is the first focusable element.

### SHELL-2 Top bar (WBS 3.1.2)

As a signed-in user, I want a top bar with the project switcher, search, notifications and my account, so that the common actions are always in reach.

- AC1: The project switcher lists the active projects the user can open (`GET /api/projects` without archived projects), with an "All projects" link to `/projects`. Picking a project opens its dashboard. The details are in [PROJ-6](projects.md#proj-6-project-switcher-wbs-333).
- AC2: The search field is shown but disabled, with the hint "Search is coming in a later version" (global search is Later, WBS 3.1.3).
- AC3: The notification bell shows the unread count and opens the panel ([NOTIF-1](notifications.md)).
- AC4: The account menu has My gaps (`/gaps`), Profile (`/profile`), Connect Claude (`/connect-claude`), Sign out and Sign out of all devices.

### SHELL-3 Home route (WBS 3.1.2)

As a returning user, I want `/` to open the project I used last, so that I land where I work.

- AC1: `/` loads the user's active projects and redirects to the last project kept in the browser, if the user can still see it.
- AC2: Otherwise it redirects to the first project in the list, or to `/projects` when the list is empty.
- AC3: While loading it shows a skeleton. If the list fails to load, it shows "Could not load your projects." with Retry.

### SHELL-4 Responsive layout (WBS 3.1.4)

As a user on a phone, I want the shell to fit a small screen, so that I can check runs and failures on the go.

- AC1: Below the `md` breakpoint the sidebar is replaced by a drawer that "Open navigation" opens and "Close navigation" closes.
- AC2: At 375 px wide no page scrolls sideways; wide tables scroll inside their own container.

### SHELL-5 Saved theme and language (WBS 3.1.5)

As a user, I want my theme and language saved to my account, so that every device shows them.

- AC1: The theme control offers Light, Dark and System (`light`, `dark`, `auto`). The language control offers EN, FR and VI (`en`, `fr`, `vi`).
- AC2: A change is applied at once and saved with `PATCH /api/me` (`colorScheme` or `language`).
- AC3: After sign-in, the saved values from `GET /api/auth/me` are applied on any device.

### SHELL-6 Not-found and error pages (WBS 3.1.6)

As a user, I want clear pages when something is missing or broken, so that I know where to go next.

- AC1: An unknown route shows "Page not found" with "Back to the home page".
- AC2: An unknown project key, or a project the user is not a member of, shows "Project not found" ("This project does not exist, or you are not a member of it.") with "See your projects". Both cases look the same.
- AC3: An error thrown while rendering shows "Something went wrong" with "Try again", "Go to the home page" and the error reference (digest) when there is one.
- AC4: An error in the root layout shows the global error page, in the language saved on the document.

### SHELL-7 Archived project banner (WBS 3.3.2)

As a member of an archived project, I want a clear banner, so that I know why I cannot change anything.

- AC1: Every page of an archived project shows "This project is archived" with "You can still view everything, but nothing can be changed."
- AC2: Buttons that need a write capability are hidden, because the `capabilities` list holds read capabilities only.

## Rules

- The last project key is kept per browser (local storage), not on the server.
- The sidebar reads capabilities from the project response, so it changes as soon as `GET /api/projects/{project_key}` is refetched (for example after `project.members_changed`).
- The session guard renders nothing of the shell until `GET /api/auth/me` says `nextStep` is `signed_in`.

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/` | redirects to `/projects` | skeleton | "Could not load your projects." + Retry | archived projects are skipped | – | – |
| `/projects/[projectKey]/*` layout | – | "Loading the project" | "This project could not be loaded" | banner (SHELL-7) | "Project not found" view | `project.members_changed` refetches the project and members |
| Sidebar | workspace items only | – | – | Settings hidden | items hidden by capability | as above |
| Not-found, error, global error | – | – | the page itself | – | – | – |

## API

| Method and path | Capability | Used for |
| --- | --- | --- |
| `GET /api/auth/me` | any session (also a half session) | current user, `nextStep`, saved theme and language |
| `GET /api/projects` | signed in | switcher and home redirect |
| `GET /api/projects/{project_key}` | `project.view` | project context, role and `capabilities` |
| `PATCH /api/me` | own account | save `colorScheme` and `language` |
| `GET /api/events` | signed in | live refresh ([API-4](client-api.md)) |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | The project key does not exist or the user is not a member: the "Project not found" view |
| `NOT_SIGNED_IN` | The session expired: the guard sends the user to `/sign-in` with the expired message |

## Later

- 3.1.3 Global search (stories, test cases, runs). The top bar keeps a disabled placeholder.

## Differences from the proposals

- The [workflow proposal §9](../discussions/testing-workflow-proposal.md#9-what-this-changes-in-the-current-plan) listed eight sidebar items. The code has nine: Failures was added, as in WBS 3.1.1.
- The gap inbox is in the account menu (My gaps), not in the sidebar.
- Archived projects are left out of the switcher, as proposed, but they are still listed on `/projects` with "Show archived".

## Open points

- Not checked in a real browser yet: the 375 px layout, the drawer, and the switcher remembering the project after a reload (carry-over from W2–W6). The pilot checklist covers them.
- The accessibility review (WBS 6.4, W7.T2) may change focus order and labels.
