# 0005. Local object storage: RustFS instead of MinIO

**Status:** Accepted. Amends [0004](0004-backend-stack.md) and the [platform features proposal](../discussions/platform-features-proposal.md) §5 (local file storage). Production storage: see [0009](0009-production-storage-and-proxy.md).
**Date:** 2026-11-01

## Context

- The plan was MinIO in Docker for local development and AWS S3 from the dev environment.
- On 2026-11-01, `docker pull` of `minio/minio` (Docker Hub) and `quay.io/minio/minio` both failed: "pull access denied" and "401 UNAUTHORIZED". MinIO can no longer be pulled anonymously.
- Tessio needs **signed POST uploads** with policy rules (key prefix, content type, size limit), because files go straight from the browser or the Claude hook to storage.

## Options considered

1. **RustFS** (`rustfs/rustfs`): S3-compatible, one container, access key from environment variables. Tested: a valid signed POST is stored (204); a wrong content type and a key outside the prefix are rejected (400).
2. **SeaweedFS** (`chrislusf/seaweedfs`): every signed POST was refused (403) without extra identity configuration.
3. **MinIO from source**: we would build and maintain the image ourselves.

## Decision

Use **RustFS** in Docker Compose for local development. AWS S3 from the dev environment is unchanged. The backend talks to both through the same S3 API (`boto3`), so switching is configuration only.

## Consequences

- `docker-compose.yml` runs `rustfs` and a one-off `rustfs-bucket` container (AWS CLI) that creates the `tessio` bucket.
- Settings: `S3_ENDPOINT_URL=http://localhost:3208` locally; empty on AWS.
- Follow-up: pin the `rustfs/rustfs` and `amazon/aws-cli` image versions before CI (WBS 7.2).
