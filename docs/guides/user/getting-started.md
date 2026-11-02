# Getting started

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for everyone. It covers your first sign-in, how to find your way, the dashboard and your profile. For what your role can do, see the [permission matrix](README.md#permission-matrix).

## Accept the invite

A workspace admin invites you by email. The link is valid for 7 days. If it has expired, ask for a new one.

1. Open the link in the email. The page **Welcome to Tessio** opens.
2. Choose a password of at least 12 characters, type it twice, and select **Set password**.
3. On **Set up two-factor authentication**, scan the QR code with an authenticator app. If you cannot scan it, enter the key shown under the code by hand.
4. Type the 6-digit code from the app and select **Confirm**.
5. On **Save your recovery codes**, keep the 10 codes somewhere safe. Use **Copy codes** or **Download**. They are shown only this once.
6. Tick **I have saved my recovery codes** and select **Continue**.

> Screenshot to add: accept-invite.png: the Welcome to Tessio page with the two password fields.

> Screenshot to add: two-factor-setup.png: the QR code, the manual key and the code field.

> Screenshot to add: recovery-codes.png: the 10 recovery codes with Copy codes and Download.

Each recovery code works once. Use one if you lose your phone.

## Sign in

1. Go to `/sign-in`, enter your email and password, and select **Sign in**.
2. Enter the 6-digit code from your authenticator app and select **Verify**.
3. Lost the app? Select **Use a recovery code instead** and type one of your saved codes.

The step between the password and the code lasts 10 minutes. After that, start again. Once signed in, you stay signed in until you have been inactive for 7 days. Too many wrong passwords lock sign-in for 15 minutes.

> Screenshot to add: sign-in.png: the sign-in form and the Forgot password? link.

### Forgot your password

1. Select **Forgot password?** on the sign-in page.
2. Enter your email and select **Send link**.
3. Open the email within 30 minutes, choose a new password and select **Change password**.

## Find your way

| Part of the screen | What it does |
| --- | --- |
| Project switcher | Pick the project you work in. **All projects** lists every project you can open. |
| Sidebar | **Dashboard**, **Sprints**, **Stories**, **Test cases**, **Shared steps**, **Suites**, **Runs**, **Plans**, **Failures**, **Test data**, **Members**, **Settings**. You see only the items your role can use; **Settings** is for project Admins. The workspace part of the sidebar has **Projects**, and for workspace admins also **Users** and **Workspace settings**. |
| Notifications bell | Tells you when a gap or a failure is assigned to you, or a run you follow finishes. Open it to read them; **Mark all as read** clears the count. |
| User menu | **My gaps**, **Profile**, **Connect Claude**, **Sign out** and **Sign out of all devices**. |
| Archived banner | **This project is archived**: you can view everything, but nothing can be changed. |

Project pages live under `/projects/{KEY}`, for example `/projects/SHOP/stories`.

> Screenshot to add: app-shell.png: the sidebar, project switcher, bell and user menu.

## Dashboard

The dashboard at `/projects/{KEY}` shows the current sprint. Pick another sprint with the sprint picker.

| Card | What it shows |
| --- | --- |
| **Current sprint** | Stories, open gaps, active failures and the share of AC covered. |
| **Stories by test status** | How many stories are *Not started*, *Ready for test*, *In test*, *Passed* or *Failed*. |
| **AC coverage** | AC that are *Passed*, *Failed*, *Blocked*, *Not run* or *Uncovered*. |
| **Recent runs** | The latest runs, with status, environment and results. Shows **No runs yet** until the first run. |
| **My work** | What waits for your role. |

**My work** depends on your role:

| Role | **My work** shows |
| --- | --- |
| Admin | Cases to write, failures to fix and gaps to answer |
| QC | Cases to write (**AC without a test case** and **My draft cases**) and gaps to answer |
| Dev | **Failures to fix** and **Gaps to answer** |
| PM, BA | **Gaps to answer** |
| Viewer | Nothing: **Nothing is assigned to your role.** |

If no sprint is active, the dashboard shows **No active sprint**. Pick a sprint, or ask a PM or BA to sync from Jira.

> Screenshot to add: dashboard.png: the dashboard of an active sprint with My work for QC.

## Profile

Open **Profile** from the user menu (`/profile`).

- Name and photo: edit your name and select **Save**. Use **Change photo** for a PNG, JPEG or WebP image.
- **Theme** and **Language**: English, French or Vietnamese. They are saved to your account and apply on every device.
- **Change password**: enter the current and the new password. Your other devices are signed out.
- **Generate new recovery codes**: your old codes stop working.
- **Reset authenticator**: set up the app again right away. Your other devices are signed out and your recovery codes stop working.
- **Sign out of all devices**: ends every session, this one included.

> Screenshot to add: profile.png: the profile page with preferences and two-factor actions.

## Next

Go to the page for your role in the [guide index](README.md#who-reads-what).
