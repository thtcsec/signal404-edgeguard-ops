# AI and reuse disclosure — Signal404 / EdgeGuard Ops

Transparency for MUGVN Hackathon 2026 judges and organizers. AI coding tools are allowed when declared (per public organizer posts).

## Pre-hackathon baseline

| Item | Detail |
| --- | --- |
| Repository created | 2026-09-30 |
| Official build window | 2026-10-17 → 2026-10-31 |
| Baseline doc | [PRE_HACKATHON_BASELINE.md](PRE_HACKATHON_BASELINE.md) |
| Pre-window contents | Layout, contracts/DTOs, config shells, placeholder services, docs scaffold |
| Pre-window tooling | Cursor used to draft scaffold (2026-09-30) |

Functional Detect → Remediate → Verify and Datadog live wiring were implemented **during** the official build window (commits from `1dffaf6` onward; Datadog live hardening `b0a5b35`).

## AI tools used during the build window

| Tool | Use |
| --- | --- |
| **Cursor** (AI pair-programmer) | Implementation assistance, tests, Datadog wiring, docs, live validation scripts |
| **ChatGPT** | Advisory review of architecture/edge cases (profile overwrite, recovery evidence) — human team decided acceptance |

No proprietary customer data was pasted into AI tools. Secrets (Datadog keys) stay in local `.env` only.

## Third-party dependencies (selected)

| Dependency | Role |
| --- | --- |
| ASP.NET Core / .NET 9 | Services |
| MongoDB.Driver | Persistence & aggregations |
| Datadog.Trace.Bundle | .NET APM automatic instrumentation |
| DogStatsD-CSharp-Client | Custom metrics |
| Python 3 + pytest | Simulator & tests |
| Docker / Datadog Agent 7 | Local Agent |

## Human ownership

Architecture choices (polling vs change streams, commanded vs reported profile, continuous recovery evidence, staged demo monitor timing) were made and reviewed by the Signal404 team. AI output was reviewed, tested, and corrected (e.g. JsonFileLogger crash, Windows UDS APM failure).

## What was **not** reused

- No vendor sample apps copied wholesale.
- No prior production IoT codebase.
- No undisclosed private datasets.
