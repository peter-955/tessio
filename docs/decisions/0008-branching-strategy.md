# 0008. Branching strategy: trunk-based development with Conventional Commits

**Status:** Accepted
**Date:** 2026-11-01

## Context

- Tessio is built by a small team, in waves of parallel tasks, and deployed from Docker images to a VPS ([ADR 0007](0007-hosting-vps-docker.md)).
- CI (`.github/workflows/ci.yml`) checks the server, the client, the Claude plugin and the Docker images, then builds images tagged with the commit SHA.
- `client/commitlint.config.mjs` already enforces Conventional Commits through a Husky hook.
- We need one simple rule set for branches, commit messages, merging and releases.

## Options considered

1. **Trunk-based development**: one protected `main`, short-lived branches merged in hours or days. Pros: small reviews, few merge conflicts, `main` is always deployable, fits a continuous deploy from CI. Cons: unfinished features must stay hidden or behind a flag until they are ready.
2. **Git Flow**: `develop`, `release/*` and `hotfix/*` branches next to `main`. Pros: explicit release stabilisation. Cons: long-lived branches, more merges and conflicts, and a release process Tessio does not need with a single deployed version.
3. **GitHub Flow without rules on commits**: like option 1 but free-form commit messages. Cons: the history and the changelog are harder to read, and commitlint is already in place.

## Decision

Use **trunk-based development** on a protected `main`, with short-lived branches named `feat/<wbs-id>-<slug>`, `fix/<wbs-id>-<slug>` or `chore/<wbs-id>-<slug>` (for example `feat/3.4.1-sprint-list`), **squash-merged** after review. Commit messages and squash titles follow **Conventional Commits** as configured in `client/commitlint.config.mjs`: a header of at most 72 characters and a type from `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `revert`.

## Consequences

- `main` is protected: no direct pushes, every pull request needs a review, and every CI job (server, client, commitlint, claude-plugin, docker) must pass before merging.
- Each merge to `main` builds `tessio-api` and `tessio-client` images tagged with the commit SHA (plus `main`). Deploys come from `main` only, by SHA, through `deploy/deploy.sh`.
- There are no release or develop branches. A hotfix is an ordinary `fix/<wbs-id>-<slug>` branch merged to `main` and deployed like any other change; rolling back means deploying an earlier SHA.
- Work that is not ready for users stays unlinked from navigation or behind a setting until it is complete.
- For now nothing is committed or pushed: the repository stays uncommitted until Peter approves the first commit. The first commit and the GitHub remote, branch protection and `DEPLOY_ENABLED` variable are set up then.
