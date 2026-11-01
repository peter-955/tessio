# 0006. Background jobs: Redis + BullMQ instead of procrastinate

**Status:** Accepted. Amends [0004](0004-backend-stack.md) (the jobs row).
**Date:** 2026-11-01

## Context

- Some work should not run inside an HTTP request: sending email, Jira sync, and periodic clean-ups ([server proposal §13](../discussions/server-proposal.md#13-background-jobs)).
- ADR 0004 picked `procrastinate`, a queue stored in Postgres, to avoid running Redis.
- The team finds Postgres-backed queues hard to debug and already knows Redis + BullMQ, which it finds simple and small.
- BullMQ has an official Python package (`bullmq`, by Taskforce.sh, the same team as the Node library) with workers, retries with backoff, deduplication and cron Job Schedulers.

## Options considered

1. **Redis + BullMQ (Python)**: known to the team; queue state can be inspected with `redis-cli` or a dashboard such as Bull Board; cron built in. Cons: one more container; the Python package has fewer features than the Node one; no type hints (`py.typed` missing).
2. **procrastinate on Postgres**: no extra service; a job can be added in the same transaction as the data. Cons: the team finds it hard to debug.
3. **Celery on Redis**: the best-known Python queue, with the Flower dashboard. Cons: synchronous at heart, a poor fit for our async use cases.

## Decision

Use **Redis + BullMQ** for background jobs. The API adds jobs through a `JobQueue` port (`app/shared/queue/`); a worker process from the same image (`python -m app.workers.worker`) runs them.

## Consequences

- Local services gain a `redis` container (append-only file on, so queued jobs survive a restart) and `bull-board` (`venatum/bull-board`, http://localhost:3205) to inspect jobs.
- Jobs are retried 5 times with exponential backoff from 30 seconds. Completed jobs are removed at once (an email job holds the invite link), and failed jobs are kept 7 days for debugging.
- Adding a job and committing the data are two separate steps. A job lost between them is acceptable for email (an admin can resend an invite). If a job ever must not be lost, add an outbox table.
- Periodic jobs (stale runs, orphan files, expired sessions) will use BullMQ Job Schedulers with cron patterns.
- Follow-up: pinning the `redis` image version before CI (WBS 7.2), and putting Bull Board behind a login (`USER_LOGIN` / `USER_PASSWORD`) if it ever runs on the VPS.
