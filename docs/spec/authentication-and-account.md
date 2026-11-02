# Authentication and account

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.2 · Story prefix AUTH · Index: [README](README.md)

## Purpose

Let invited people in, and nobody else. Sign-in needs a password and a second factor. Each user manages their own profile, password, two-factor, saved preferences and personal API tokens for Claude. The server code is in [server/app/modules/auth](../../server/app/modules/auth) and [server/app/modules/api_tokens](../../server/app/modules/api_tokens). The screens are in [client/src/modules/auth](../../client/src/modules/auth), [profile](../../client/src/modules/profile) and [connect-claude](../../client/src/modules/connect-claude).

## Roles and capabilities

- Sign-in, invite, two-factor and password reset are public or need only a half session.
- Profile, password, recovery codes and own authenticator reset act on the caller's own account and need no capability.
- Creating an API token needs `api_token.create` in the token's project (every project role has it) and real membership in that project. Listing and revoking act on the caller's own tokens.
- Inviting and managing other users is [user management](user-management.md).

## User stories

### AUTH-1 Sign in with email and password (WBS 3.2.1)

As an invited user, I want to sign in with my email and password, so that I reach my projects. There is no public sign-up.

- AC1: `/sign-in` posts to `POST /api/auth/sign-in`. A correct password for an `active` user starts a half session and returns `nextStep` `two_factor_required`, or `two_factor_setup_required` when two-factor is not set up yet.
- AC2: A wrong password, an unknown email, an `invited` user or a `deactivated` user all get `INVALID_CREDENTIALS` ("Email or password is incorrect."). The server hashes a dummy password for unknown emails, so the answer takes the same time.
- AC3: After 5 failed attempts (passwords or two-factor codes), the account is locked for 15 minutes. While locked, sign-in answers `SIGN_IN_LOCKED` (429), even with the right password.
- AC4: The email is matched without case.
- AC5: A `next` query parameter brings the user back to the page they asked for after sign-in.
- AC6: An expired session lands on `/sign-in` with "Your session has expired. Sign in again."
- AC7: More than 20 sign-in requests from one IP address within 15 minutes get `RATE_LIMITED` (429) with a `Retry-After` header. The two-factor, invite and reset routes have the same per-IP limit.

### AUTH-2 Two-factor step at sign-in (WBS 3.2.1, 3.2.3)

As a user with two-factor set up, I want to enter a code from my app or a recovery code, so that only I can finish signing in.

- AC1: `/two-factor` posts the code to `POST /api/auth/two-factor` with the half session. A valid TOTP code turns the half session into a full session (`nextStep` `signed_in`).
- AC2: "Use a recovery code instead" accepts one of the 10 recovery codes. Each recovery code works once.
- AC3: A TOTP code from a time step that was already used is refused, so a code cannot be replayed.
- AC4: A wrong code gets `INVALID_TWO_FACTOR_CODE` and counts as a failed attempt. When that attempt locks the account, the half session is deleted.
- AC5: A half session lasts 10 minutes.

### AUTH-3 Accept an invite (WBS 3.2.2)

As an invited person, I want to set my password from the invite email, so that my account becomes active.

- AC1: `/invite/[token]` posts the password to `POST /api/auth/invites/{token}`. The user becomes `active` and gets a half session with `nextStep` `two_factor_setup_required`.
- AC2: The invite link is valid for 7 days and works once. An unknown, used or expired link, or a user who is no longer `invited`, gets `INVALID_ONE_TIME_LINK`, shown as "This invite link is invalid or has expired."
- AC3: The password needs at least 12 characters (`WEAK_PASSWORD`) and must not be in the Pwned Passwords list (`PASSWORD_BREACHED`).

### AUTH-4 Set up two-factor (WBS 3.2.3)

As a new user, I want to set up an authenticator app, so that my account is protected. Two-factor is required for everyone.

- AC1: `/two-factor/setup` calls `POST /api/auth/two-factor/setup` and shows a QR code plus the manual key.
- AC2: "Confirm" posts the first code to `POST /api/auth/two-factor/confirm`. A right code finishes setup, turns the session into a full session and returns 10 recovery codes.
- AC3: The recovery codes are shown once, with "Copy codes" and "Download". "Continue" stays disabled until "I have saved my recovery codes" is ticked.
- AC4: Confirming before setup started gets `TWO_FACTOR_SETUP_NOT_STARTED`. Setting up twice gets `TWO_FACTOR_ALREADY_SET_UP`.
- AC5: The TOTP key is stored encrypted (AES-256-GCM).

### AUTH-5 Forgot and reset password (WBS 3.2.4)

As a user who forgot their password, I want a reset link by email, so that I can choose a new one.

- AC1: `/forgot-password` posts the email to `POST /api/auth/password/forgot`. The answer is always 204 and the page says "If an account exists for {email}, we sent a link. It is valid for 30 minutes." Only `active` users get an email.
- AC2: `/reset-password/[token]` posts the new password to `POST /api/auth/password/reset`. The link works once, for 30 minutes.
- AC3: A reset clears the lockout counter and signs the user out of every session. Two-factor is still needed at the next sign-in.
- AC4: The same password rules as AUTH-3 apply.
- AC5: One IP address can ask for 10 reset links per hour (`RATE_LIMITED` after that), and one email address gets at most 3 reset emails per hour; further requests still answer 204 but send nothing.

### AUTH-6 Profile details and avatar (WBS 3.2.5)

As a user, I want to set my name and photo, so that teammates recognise me.

- AC1: `/profile` shows the email (read-only) and the name (1 to 100 characters), saved with `PATCH /api/me`.
- AC2: "Change photo" takes a PNG, JPEG or WebP image up to 2 MB. The client crops it to a centred square of at most 512 px, uploads it through `POST /api/me/avatar-upload` and `POST /api/me/avatar-upload/{file_id}/complete`, then saves `avatarFileId` with `PATCH /api/me`.
- AC3: An avatar file that is not the caller's gets `NOT_FOUND`; one that is not uploaded yet gets `UPLOAD_NOT_COMPLETED`.
- AC4: "Remove photo" clears `avatarFileId`. Avatars are shown through `GET /api/users/{user_id}/avatar`, a 302 to a 5-minute link that browsers may cache for 240 s.

### AUTH-7 Change password (WBS 3.2.5)

As a user, I want to change my password, so that I can rotate it.

- AC1: `PUT /api/me/password` needs the current password (`INVALID_CURRENT_PASSWORD`, 400, when wrong) and a new one that passes the AUTH-3 rules.
- AC2: Every other session of the user is signed out; the current one stays. The page says "Your other devices were signed out."

### AUTH-8 Recovery codes and own authenticator (WBS 3.2.5)

As a user, I want new recovery codes or a new authenticator, so that I can recover when I lose one.

- AC1: "Generate new recovery codes" asks for the password and calls `POST /api/me/recovery-codes`. It returns 10 new codes; the old ones stop working.
- AC2: "Reset authenticator" asks for the password and calls `POST /api/me/two-factor/reset`. Two-factor and all recovery codes are cleared, every session is deleted, and a new half session goes to `/two-factor/setup?next=%2Fprofile`.
- AC3: Both refuse with `TWO_FACTOR_SETUP_NOT_STARTED` when two-factor is not set up.

### AUTH-9 Theme and language in the profile (WBS 3.2.5)

As a user, I want to pick the theme and language on my profile, so that they follow me to every device.

- AC1: The Preferences card has the same controls as the sidebar and saves through `PATCH /api/me` ([SHELL-5](app-shell.md#shell-5-saved-theme-and-language-wbs-315)).

### AUTH-10 Create an API token for Claude (WBS 3.2.6)

As a developer or tester, I want a personal token and one install command, so that Claude Code can run tests in my project.

- AC1: `/connect-claude` creates a token with `POST /api/me/api-tokens`: a name (1 to 100 characters), one project, and a lifetime of 7, 30, 60 or 90 days (30 by default; the API accepts 1 to 90).
- AC2: The token has the form `tsio_<prefix>_<secret>`. It is shown once, inside `claude plugin install tessio --marketplace <origin>/api/plugin/marketplace.json --config tessio_url=<origin> --config tessio_token=<token>`, and is never kept in the query cache. The server stores only its SHA-256 hash.
- AC3: The marketplace is the one this Tessio serves ([ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md)), built from the page's own address. On an address that is not HTTPS, the dialog adds: "Claude Code installs the plugin only from an HTTPS address. On a local copy of Tessio, start Claude Code with claude --plugin-dir claude from the repository instead."
- AC4: A user can hold at most 10 active tokens (`TOKEN_LIMIT_REACHED`, "You have 10 active tokens. Revoke one to create another.").
- AC5: The caller must be a real member of the project (`PERMISSION_DENIED` otherwise). Acting as a workspace admin is not enough. A call made with an API token cannot create tokens.
- AC6: A Viewer may create a token. The page warns "You are a Viewer in this project, so Claude can read but not record results."
- AC7: Creating a token on an archived project is refused with `PROJECT_ARCHIVED`.
- AC8: A token has a scope (`scope`, WBS 9.6): `mcp` (the default, for Claude Code and the plugin hooks) or `api` (for the public REST routes, from CI). The list and create answers return it. An `mcp` token is refused on REST routes that need a session, as before; an `api` token works only on the routes [integrations.md, INT-6](integrations.md#int-6-api-scope-tokens-for-the-public-rest-api-wbs-96) lists, and gets `TOKEN_SCOPE_NOT_ALLOWED` everywhere else, including `/mcp`. The form's "Used for" field picks the scope; for an `api` token the dialog shows a `curl` call to the JUnit import instead of the plugin install command, and the token list has a "Used for" column ([integrations.md, Screens and states](integrations.md#screens-and-states)).

### AUTH-11 List and revoke tokens (WBS 3.2.6)

As a token owner, I want to see and revoke my tokens, so that I can cut off a lost laptop.

- AC1: `GET /api/me/api-tokens` lists the caller's tokens with name, project, prefix, status (`active`, `expired`, `revoked`), expiry, last used and created dates, and the plugin version the token last sent (`pluginVersion`, shown in the Plugin column). Revoked and expired tokens stay listed.
- AC2: `DELETE /api/me/api-tokens/{token_id}` revokes a token at once; another user's token gets `NOT_FOUND`.
- AC3: "Last used" is refreshed at most once every 60 seconds, and at once when the plugin version changes.
- AC4: Each MCP call saves the `X-Tessio-Plugin-Version` header on the token before the plugin version check, so an outdated plugin's version is kept ([AI Harness rules](ai-harness.md#rules)).

### AUTH-12 Sign out and sign out of all devices (WBS 3.2.7)

As a user, I want to sign out here or everywhere, so that I control my sessions.

- AC1: "Sign out" calls `POST /api/auth/sign-out` and deletes the current session.
- AC2: "Sign out of all devices" asks for confirmation, calls `POST /api/auth/sign-out-all`, deletes every session of the user, clears the query cache and goes to `/sign-in`.
- AC3: API tokens are not revoked by signing out.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Failed attempts before lockout | 5 | `MAXIMUM_FAILED_SIGN_INS` |
| Lockout | 15 minutes | `LOCKOUT_DURATION` |
| Half session (password done, two-factor pending) | 10 minutes | `HALF_SESSION_LIFETIME` |
| Session idle timeout | 7 days | `SESSION_IDLE_LIFETIME` |
| Last-seen refresh | every 1 minute | `LAST_SEEN_REFRESH_INTERVAL` |
| Session cookie | `tessio_session`, HttpOnly, SameSite=Lax, Secure, 30 days | `SESSION_COOKIE_LIFETIME` |
| Invite link | 7 days, one use | `INVITE_LIFETIME` |
| Password reset link | 30 minutes, one use | `PASSWORD_RESET_LIFETIME` |
| Password | at least 12 characters, not breached | `MINIMUM_PASSWORD_LENGTH` |
| Recovery codes | 10, one use each | `RECOVERY_CODE_COUNT` |
| API token default and maximum lifetime | 30 and 90 days | `DEFAULT_API_TOKEN_LIFETIME_DAYS`, `MAXIMUM_API_TOKEN_LIFETIME_DAYS` |
| Active API tokens per user | 10 | `MAXIMUM_ACTIVE_API_TOKENS` |
| API token prefix | `tsio_` | `API_CREDENTIAL_START` |
| Requests per client IP | sign-in: 20 per 15 min; two-factor and two-factor confirm: 20 per 15 min together; invite accept and password reset: 20 per 15 min together; forgot password: 10 per hour | `SIGN_IN_RATE_LIMIT`, `TWO_FACTOR_RATE_LIMIT`, `ONE_TIME_LINK_RATE_LIMIT`, `PASSWORD_FORGOT_RATE_LIMIT` |
| Reset emails per address | 3 per hour; extra requests still answer 204 but send nothing | `PASSWORD_FORGOT_EMAIL_RATE_LIMIT` |

- The sign-in steps are `two_factor_setup_required`, `two_factor_required` and `signed_in` (`SignInStep`). `GET /api/auth/me` accepts a half session and returns the step as `nextStep`.
- Sessions and one-time links are stored as SHA-256 hashes. Passwords use Argon2id.
- Deactivating a user deletes their sessions, expires their open links and revokes their tokens ([USER-4](user-management.md)).
- Every `POST`, `PUT`, `PATCH` and `DELETE` under `/api/` passes the CSRF `Origin` check ([non-functional requirements](non-functional-requirements.md)).

## Screens and states

| Route | Empty | Loading | Error | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- |
| `/sign-in` | – | button busy | field or form error from the code | – | – |
| `/two-factor` | – | button busy | "The code is incorrect." | a full session is sent on | – |
| `/two-factor/setup` | – | QR loading | "We could not start the two-factor setup." + Try again | – | – |
| `/invite/[token]` | – | button busy | invalid link message + "Go to sign in" | – | – |
| `/forgot-password`, `/reset-password/[token]` | – | button busy | invalid link + "Request a new link" | – | – |
| `/profile` | no photo: initials | skeletons | inline errors per card | – | – |
| `/connect-claude` | "No tokens yet" | table skeleton | "Tokens could not be loaded" + Try again | "You are not a member of any project yet." | – |

The `(auth)` routes are public. `proxy.ts` sends a browser without the session cookie to `/sign-in?next=…` for every other page.

## API

| Method and path | Who | Notes |
| --- | --- | --- |
| `POST /api/auth/sign-in` | public | starts a half session |
| `POST /api/auth/two-factor` | half session | code or recovery code |
| `POST /api/auth/two-factor/setup` | half session | key and QR URI |
| `POST /api/auth/two-factor/confirm` | half session | returns recovery codes |
| `POST /api/auth/invites/{token}` | public | set password |
| `POST /api/auth/password/forgot` | public | always 204 |
| `POST /api/auth/password/reset` | public | |
| `GET /api/auth/me` | any session | `nextStep` |
| `POST /api/auth/sign-out` | signed in | |
| `POST /api/auth/sign-out-all` | signed in | |
| `PATCH /api/me` | signed in | name, language, colorScheme, avatarFileId |
| `PUT /api/me/password` | signed in | |
| `POST /api/me/recovery-codes` | signed in | needs the password |
| `POST /api/me/two-factor/reset` | signed in | needs the password |
| `POST /api/me/avatar-upload`, `POST /api/me/avatar-upload/{file_id}/complete` | signed in | 2 MB, image types |
| `GET /api/users/{user_id}/avatar` | signed in | 302 to a signed link |
| `GET /api/me/api-tokens` | signed in | own tokens |
| `POST /api/me/api-tokens` | `api_token.create` + membership | |
| `DELETE /api/me/api-tokens/{token_id}` | signed in | own token |

## Errors

| ErrorCode | When |
| --- | --- |
| `INVALID_CREDENTIALS` | Wrong email or password, or the user is not `active` |
| `SIGN_IN_LOCKED` | 5 failed attempts in a row; locked for 15 minutes (429) |
| `RATE_LIMITED` | Too many requests from one IP on a public auth route (429, with `Retry-After`) |
| `INVALID_TWO_FACTOR_CODE` | Wrong TOTP or recovery code |
| `TWO_FACTOR_ALREADY_SET_UP` | Setup started when two-factor is already set up |
| `TWO_FACTOR_SETUP_NOT_STARTED` | Confirm before setup, or recovery codes or reset without two-factor |
| `INVALID_ONE_TIME_LINK` | Invite or reset link unknown, used or expired |
| `WEAK_PASSWORD` | Password shorter than 12 characters |
| `PASSWORD_BREACHED` | Password found in the breached-password list |
| `INVALID_CURRENT_PASSWORD` | Wrong current password on change, regenerate or reset |
| `NOT_SIGNED_IN` | No session, or a half session on a full-session route |
| `ORIGIN_NOT_ALLOWED` | A write request from another site |
| `UPLOAD_NOT_COMPLETED` | Avatar saved before its upload finished |
| `FILE_TYPE_NOT_ALLOWED`, `FILE_TOO_LARGE` | Avatar not PNG, JPEG or WebP, or over 2 MB |
| `TOKEN_LIMIT_REACHED` | An 11th active token |
| `PERMISSION_DENIED` | Token for a project the caller is not a member of, or a token used to create a token |
| `PROJECT_ARCHIVED` | Token for an archived project |
| `NOT_FOUND` | Revoking another user's token; avatar file not the caller's |

## Later

- 3.2.8 SSO (Google, Microsoft, Atlassian).

## Differences from the proposals

- The [platform proposal §1](../discussions/platform-features-proposal.md#1-authentication) planned AWS SES for email. The code sends through generic SMTP (Mailpit locally); the production provider is not chosen.
- Sign-in lockout also counts wrong two-factor codes, not only wrong passwords.
- API tokens can be created by every project role, Viewer included; a Viewer token can only read.
- The Connect Claude page shows a `claude plugin install … --config` command, not the `claude mcp add` command that WBS 8.2 names.

## Open points

- Not checked by hand yet: invite email in Mailpit → set password → scan the QR code with a real app → recovery codes → dashboard (W2 carry-over).
- The install command puts the token on the command line, so it can end up in shell history (accepted, W3.T4).
- Two token creates that race can exceed the limit of 10 by one (accepted MVP behaviour).
- The plugin marketplace host is undecided (blocker for WBS 5.3 and 8.2).
- The per-IP limits were added by the W7.T1 security review while this spec was written; the client shows `errors.api.RATE_LIMITED` once the wave's integration adds it ([NFR-SEC-20](non-functional-requirements.md#sec-security)).
