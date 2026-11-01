# Platform features: authentication, authorization, projects, users, files, design system

**Status:** Accepted
**Date:** 2026-10-31
**Related:** [testing-workflow-proposal.md](testing-workflow-proposal.md) (roles and permissions for the testing workflow)

## Decisions at a glance

| Area | Decision |
| --- | --- |
| Who uses Tessio | **One company** (single tenant) for MVP. |
| Sign-in | **Email + password**, invite-only (no public sign-up). |
| Two-factor authentication | **Required for everyone** (authenticator app). |
| Roles per person | **One role per person per project.** |
| Viewer role | **Yes**: read-only project role. |
| Who creates projects | **Workspace admins only.** |
| Projects ↔ Jira | **One Tessio project = one Jira project.** |
| File storage | **RustFS (S3-compatible) in Docker, locally and on the VPS** ([ADR 0005](../decisions/0005-local-object-storage.md), [ADR 0009](../decisions/0009-production-storage-and-proxy.md)); a hosted S3-compatible service stays possible by configuration. |
| Test case files | **Yes**: test cases can carry files used during the test (e.g. files attached in a chat). |
| Brand | **Blue** (trust). Logo drafted in [design/brand/](../design/brand/). |
| Theme | **Light and dark**, via Mantine's color-scheme manager. |
| UI library | **Mantine 9** with a custom Tessio theme ([ADR 0002](../decisions/0002-ui-library.md)). |
| Languages | **English, French, Vietnamese**, set up from the start ([ADR 0003](../decisions/0003-translations.md)). |

---

## 1. Authentication

- **Invite-only:** a workspace admin invites a person by email. The invite link lets them set a password, then set up two-factor authentication.
- **Password rules:** minimum 12 characters, checked against known-breached passwords. Stored with a slow hash (Argon2id or bcrypt).
- **Two-factor (required):**
  - TOTP authenticator app (Google Authenticator, 1Password…).
  - 10 one-time recovery codes shown at setup.
  - A workspace admin can reset a user's two-factor if they lose their phone.
- **Forgot password:** email link valid for 30 minutes; two-factor is still required after the reset.
- **Sessions:** signed out after 7 days of inactivity; "sign out of all devices" in the profile.
- **Lockout:** temporary lock after repeated failed sign-ins.
- **Claude / MCP tokens:** personal API tokens, each limited to one project, with an expiry date, revocable at any time. A token can never do more than its owner's role allows.
- **Emails** (invites, password reset) need an email service: **Mailpit** locally; a production SMTP provider, not chosen yet.
- **Later:** SSO (Google, Microsoft, Atlassian).

## 2. Authorization

Two levels of roles. **Each person has exactly one role per project.**

### Workspace roles

| Role | Can |
| --- | --- |
| **Owner** | Everything, including transferring ownership. One per workspace. |
| **Workspace admin** | Invite and deactivate users, create and archive projects, reset two-factor, set the Jira connection. |
| **Member** | Everyone else. Sees only the projects they belong to. |

### Project roles

Admin, PM, BA, QC and Dev work as in the permission table of [testing-workflow-proposal.md](testing-workflow-proposal.md) §5, plus:

| Role | Can |
| --- | --- |
| **Viewer** | Read stories, test cases, runs, reports and failures. Cannot see secret values, start runs, answer gaps or edit anything. |

### Enforcement

- Every API request and every MCP call is checked on the server against the user's project role.
- Hiding buttons in the UI is for convenience only.
- Users never see that a project exists unless they are a member (or a workspace admin).

## 3. Project management

- **Create:** workspace admins only. Required: name, key (e.g. `SHOP`), the linked **Jira project** (one-to-one).
- **Contents:** Jira link, environments, test data, test files, members, settings.
- **Members:** the project Admin adds workspace users to the project and picks their one role.
- **Archive, not delete:** an archived project is read-only and hidden from the switcher. Its runs and screenshots are kept forever.
- **Planning stays in Jira.** Tessio does not manage tasks, sprints or estimates.

## 4. User management

- **Workspace user directory** (workspace admins): invite, resend invite, deactivate, reactivate, reset two-factor.
- **Deactivate, never delete:** a deactivated user can't sign in, their API tokens stop working, but their name stays on runs, answers and failures.
- **Profile** (each user): name, avatar, password change, two-factor devices, API tokens, theme preference.
- **Per-user view of access:** which projects a person belongs to and with which role.

## 5. File management

### What files Tessio stores

| Kind | Attached to | Uploaded by | Example |
| --- | --- | --- | --- |
| **Test case files** | Test case (or step) | QC | Image and PDF that a chat test attaches to a message |
| **Step screenshots** | Step result | Claude | One per step, kept forever |
| **Manual run evidence** | Step result | QC | Screenshot from a manual run |
| **Imports** | Project | QC | Google Sheets / CSV export |
| **Report exports** | Run | Anyone with access | PDF / Markdown report |

### Test case files in practice

- QC uploads the files on the test case and references them in a step: `Attach {{file.invoice-sample.pdf}} to the chat message`.
- During a run, Claude asks the MCP server for the file (new tool `get_test_file(runId, key)`), downloads it to a temporary folder and uploads it through the browser.
- The run records which file version was used.

### Storage

- **Local and VPS:** **RustFS** in Docker, a self-hosted server that speaks the S3 API ([ADR 0005](../decisions/0005-local-object-storage.md) replaced MinIO; [ADR 0009](../decisions/0009-production-storage-and-proxy.md) keeps it in production). Files persist in a Docker volume.
- **Later, if needed:** a hosted S3-compatible service. Switching is configuration only (endpoint, bucket, keys), not code.
- **Access:** files are private. The app hands out short-lived signed links after checking the user's project role.
- **Limits:** 20 MB per file. Allowed types are configurable per project.

## 6. Design system

### Brand

- **Primary color: blue** (trust). See [design/brand/README.md](../design/brand/README.md) for the palette and logo.
- **Logo:** a ring (the "o" of Tessio) with a check mark breaking out of it, meaning a test has passed.

### UI library: Mantine 9

Decided in [ADR 0002](../decisions/0002-ui-library.md): **Mantine 9** with a custom **Tessio theme** (blue primary, Geist, sizes, radius and spacing below). Our own layout and page styles stay in SCSS modules using Mantine's CSS variables.

### Theme: light and dark

- Handled by **Mantine's color-scheme manager**: follows the OS by default, switch in the UI, choice saved in the user profile.
- Our SCSS uses Mantine's CSS variables, so it switches with the theme.
- Not verified yet: using plain CSS `light-dark()` in our SCSS next to Mantine's switch. Check when setting up Mantine.

### Tokens and type (set in the Mantine theme)

- **Font:** Geist (sans and mono).
- **Font sizes:** 12 · 14 (base) · 16 · 20 · 24 px.
- **Spacing:** 8 · 12 · 16 · 24 · 32 px.
- **Radius:** 4 · 6 · 10 (default) · 14 · 20 px.
- **Status colors:** passed (green), failed (red), running (blue), queued (amber), skipped (gray), each with a soft background variant.
- **Contrast:** WCAG AA for all text.

### Components

- **Mantine components** for everything: button, inputs, select, checkbox, switch, badge, card, table, tabs, modal, menu, tooltip, avatar, date pickers, dropzone (file upload), skeleton.
- **Toasts:** Sonner, rendered by `DSToaster` and triggered with the `useShowToast()` hook.
- **Our own components** only where Mantine has nothing: step editor, traceability matrix, run step timeline, empty states.
- **Icons:** Tabler (`@tabler/icons-react`).
- Mobbin references guide the theme and component variants; log them in [design/mobbin-references.md](../design/mobbin-references.md).
