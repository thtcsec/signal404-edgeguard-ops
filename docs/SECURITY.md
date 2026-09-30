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

Datadog trial credentials and any Atlas URI are build-window inputs. They are not part of this scaffold. Do not reuse an employer organization or a production API key.
