# User management (workspace)

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.3b · Story prefix USER · Index: [README](README.md)

## Purpose

The workspace user directory: who can sign in to Tessio, with which workspace role, and which projects each person belongs to. Users are never deleted, only deactivated, so their names stay on runs, answers and failures. Server: the users router in [server/app/modules/auth](../../server/app/modules/auth/users_router.py) and the access view in [server/app/modules/projects](../../server/app/modules/projects). Client: [client/src/modules/users](../../client/src/modules/users).

## Roles and capabilities

| Action | Owner | Workspace admin | Member |
| --- | --- | --- | --- |
| Open `/users`, list and filter users | ✓ (`user.manage`) | ✓ | – |
| Invite a Member | ✓ | ✓ | – |
| Invite a Workspace admin | ✓ (`workspace_role.manage`) | – | – |
| Resend an invite (any invited user) | ✓ | ✓ | – |
| Deactivate, reactivate, reset two-factor of a Member | ✓ | ✓ | – |
| The same three actions on a Workspace admin | ✓ | – (`OWNER_ONLY`) | – |
| Change a workspace role | ✓ | – (`OWNER_ONLY`) | – |
| See a user's project access | ✓ (`user_access.view`) | ✓ | – |

Nobody can deactivate, reactivate, reset the two-factor of, or change the role of their own account or the Owner's account (`CANNOT_CHANGE_OWN_OR_OWNER`). Nobody can make someone Owner.

## User stories

### USER-1 User directory (WBS 3.3b.1)

As a workspace admin, I want to see every user with their role and status, so that I know who has access.

- AC1: `/users` lists each user's name, email, workspace role (Owner, Workspace admin, Member), status (Invited, Active, Deactivated) and whether two-factor is set up.
- AC2: Filters: search by name or email (up to 100 characters), status, and workspace role, sent as `query`, `status` and `workspaceRole`.
- AC3: A Member who opens `/users` sees "Only workspace admins can manage users"; the sidebar has no Users item for them.

### USER-2 Invite a user (WBS 3.3b.1)

As a workspace admin, I want to invite someone by email, so that they can set a password and join.

- AC1: "Invite user" posts email, name (1 to 100 characters) and workspace role to `POST /api/users`. The user starts as `invited` and gets an invite email with a link valid for 7 days.
- AC2: An email that exists gets `EMAIL_ALREADY_USED`. Emails are stored in lower case.
- AC3: Only the Owner may invite a Workspace admin; a Workspace admin who tries gets `OWNER_ONLY` and the form says "Only the owner can invite workspace admins."
- AC4: The first Owner is created from the command line (`app/commands/invite_user.py`).

### USER-3 Resend an invite (WBS 3.3b.1)

As a workspace admin, I want to resend an invite, so that someone whose link expired can still join.

- AC1: `POST /api/users/{user_id}/resend-invite` expires the old link and emails a new one, valid for 7 days.
- AC2: A user who already accepted gets `USER_NOT_INVITED` ("This user has already accepted the invite.").

### USER-4 Deactivate and reactivate (WBS 3.3b.1)

As a workspace admin, I want to switch off someone who left, so that they lose access but their history stays.

- AC1: Deactivate asks for confirmation and calls `POST /api/users/{user_id}/deactivate`. The user becomes `deactivated`; their sessions are deleted, their open invite and reset links expire, and their API tokens are revoked.
- AC2: A deactivated user cannot sign in (`INVALID_CREDENTIALS`), cannot be added to a project (`USER_DEACTIVATED`), and is never chosen as a gap or failure assignee. Existing assignments show a Deactivated badge with a hint to reassign.
- AC3: Reactivate calls `POST /api/users/{user_id}/reactivate`. A user who had set a password becomes `active` again, with the lockout cleared. A user who never accepted the invite goes back to `invited` and gets a new invite email.
- AC4: Both calls do nothing when the user is already in the target state.

### USER-5 Workspace roles (WBS 3.3b.2)

As the Owner, I want to make people Workspace admins or Members, so that admin rights stay under control.

- AC1: The roles are `owner`, `admin` and `member`. There is one Owner.
- AC2: "Change workspace role" calls `PUT /api/users/{user_id}/workspace-role` with `admin` or `member`. Only the Owner may do it (`OWNER_ONLY`); asking for `owner` is refused the same way.
- AC3: A Workspace admin acts as project Admin in every project for signed-in calls ([README rules](README.md#rules-every-spec-relies-on)).

### USER-6 Reset a user's two-factor (WBS 3.3b.3)

As a workspace admin, I want to reset the two-factor of someone who lost their phone, so that they can set it up again.

- AC1: "Reset two-factor" asks for confirmation and calls `POST /api/users/{user_id}/reset-two-factor`.
- AC2: The user's authenticator and recovery codes are cleared and all their sessions are deleted. At the next sign-in they must set up two-factor again (`two_factor_setup_required`).

### USER-7 Per-user project access (WBS 3.3b.4)

As a workspace admin, I want to see a user's projects and roles, so that I can check their access.

- AC1: "View project access" opens `/users/[userId]`, which lists project, key, role and state (Archived) from `GET /api/users/{user_id}/access`.
- AC2: For a workspace admin, the page notes "Workspace admins act as Admin in every project, including projects not listed here."
- AC3: A user with no membership shows "Not a member of any project. Add them from a project's Members page."
- AC4: An unknown user shows "User not found".

## Rules

- User statuses: `invited`, `active`, `deactivated`. Transitions: `invited` → `active` (accept invite); `invited` or `active` → `deactivated`; `deactivated` → `active` (had a password) or `invited` (never accepted). The diagram is in [user-flows.md](../design/user-flows.md#user-status).
- Name: 1 to 100 characters. Search query: up to 100 characters.
- Owner transfer does not exist yet.

## Screens and states

| Route | Empty | Loading | Error | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- |
| `/users` | "No users match these filters" | table skeleton | "Users could not be loaded" + Try again | "Only workspace admins can manage users" | – (refetch after each action) |
| `/users/[userId]` | "Not a member of any project" | skeleton | "Project access could not be loaded" | same as `/users` | – |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/users` | `user.manage` |
| `POST /api/users` | `user.manage` (+ `workspace_role.manage` to invite an admin) |
| `GET /api/users/{user_id}` | `user.manage` |
| `POST /api/users/{user_id}/resend-invite` | `user.manage` |
| `POST /api/users/{user_id}/deactivate` | `user.manage` |
| `POST /api/users/{user_id}/reactivate` | `user.manage` |
| `POST /api/users/{user_id}/reset-two-factor` | `user.manage` |
| `PUT /api/users/{user_id}/workspace-role` | `user.manage` + `workspace_role.manage` |
| `GET /api/users/{user_id}/access` | `user_access.view` |

## Errors

| ErrorCode | When |
| --- | --- |
| `PERMISSION_DENIED` | A Member calls any of these routes |
| `OWNER_ONLY` | A Workspace admin invites a Workspace admin, deactivates, reactivates or resets the two-factor of one, or changes a role; anyone asks for `owner` |
| `CANNOT_CHANGE_OWN_OR_OWNER` | Deactivate, reactivate, reset two-factor or role change aimed at the caller or the Owner |
| `EMAIL_ALREADY_USED` | Invite with an email that exists |
| `USER_NOT_INVITED` | Resend to a user who already accepted |
| `NOT_FOUND` | Unknown user id |
| `INVALID_REQUEST` | Invalid email or name |

## Later

- Owner transfer (assumption for WBS 3.3b.2).
- 4.10 Full audit log: admin actions (invite, deactivate, reactivate, reset two-factor, role change) write no audit event today.

## Differences from the proposals

- The [platform proposal §2](../discussions/platform-features-proposal.md#workspace-roles) let the Owner transfer ownership. That is not built.
- User management lives in the `auth` server module, not a separate `users` module, to avoid an import cycle between users, auth and projects.

## Open points

- The access page does not list a workspace admin's implicit Admin access; it shows the note instead (W1 carry-over).
- Not checked by hand in a browser with Mailpit: invite, resend, deactivate, reactivate, reset two-factor and role change (W3 carry-over).
