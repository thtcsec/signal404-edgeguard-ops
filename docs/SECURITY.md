# Security and data rules

EdgeGuard Ops uses synthetic telemetry only.

Do not put any of the following into MongoDB, Datadog, the repository, screenshots, or the demo video:

- production data
- employer internal information, source code, logs, or architecture
- customer information
- personal data
- API keys, passwords, or other credentials

## Secrets

- `.env.example` lists variable names and empty or local defaults.
- `.env`, `secrets/`, `*.key`, and `*.pem` are gitignored.
- MongoDB and Datadog credentials, when they exist, come from environment variables.
- `Observability:DatadogEnabled` stays false until those variables are set on a machine, not in git.

Local MongoDB in Compose has no root password. That is a development convenience on localhost, not a pattern for a hosted database.

## Hackathon accounts

Datadog trial credentials and any Atlas URI are build-window inputs. They are local configuration, not judge artifacts. Do not reuse an employer organization or a production API key.

## November 6 review boundary

Compose host ports bind loopback; API errors no longer return raw exception details. The lab API has no authentication and local MongoDB has no credentials: do not expose them publicly. The focused tracked/proposed-file secret scan found no pattern matches, but is not a full-history or OCR guarantee. Transitive SharpCompress/Snappier advisories remain; see the [release report](submission/MUGVN2026_RELEASE_REPORT.md). No deployment or visibility change was performed.
