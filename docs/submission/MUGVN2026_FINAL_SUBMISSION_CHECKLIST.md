# MUGVN 2026 — final submission checklist

Reviewed November 6, 2026. **CONDITIONAL PASS — not ready to submit until release synchronization and final-video hosting are closed. Runtime validation is now complete at `40ee9ee`; see [final release validation](MUGVN2026_RELEASE_VALIDATION.md).** Deadline **November 8, 23:59 ICT** confirmed on the official form.

## Prepared locally

- [x] Isolated branch; original main HEAD and dirty baseline identified.
- [x] Current README/architecture/submission claims reconciled with source.
- [x] Primary automatic E2E IDs/timestamps correlated; staged monitor evidence separate.
- [x] Historical E2E JSON and baseline retained; no collection resets or E2E recapture.
- [x] Final 80.1 s MP4 metadata, decode, silence and representative/boundary frames checked; checksum recorded; bytes preserved.
- [x] Exact form sections/fields inspected read-only; proposed answers prepared.
- [x] Judge Q&A, current slide content, impact and claim audit prepared.
- [x] Full .NET tests and Python tests pass; Release build, Compose config, real-Mongo fault checks and automatic E2E pass (details in final validation).
- [x] Tracked text secret-pattern scan found no matches; `.env` and MP4 remain ignored.
- [x] PUBLIC repository status confirmed November 7 through metadata and unsigned HTTP 200; remote still contains the older main.

## Before submitting — team owner

- [x] Close full Mongo-backed test/runtime smoke gate: 15 .NET + 6 Python tests, 16 additional Mongo checks and automatic E2E pass on `40ee9ee`.
- [ ] Review local commits, then explicitly approve push to the chosen remote branch; no push has been performed.
- [x] Repository home is anonymously accessible.
- [ ] After approved publication, confirm judges see the audited release, not old main; check every artifact URL separately.
- [ ] Host the exact checksummed MP4; test playback/download from a signed-out or judge-equivalent account.
- [ ] Provide judge-readable architecture and authentic Datadog screenshot links. A private org dashboard URL alone is insufficient.
- [ ] Replace every placeholder in prepared form content; enter registered leader name/email and team membership yourself.
- [ ] Review final presentation content and any deck caveat in release report.
- [ ] Review dependency advisories and lab-only security limitations; do not deploy the lab publicly.
- [ ] Team leader checks all four form attestations and submits before November 8, 23:59 ICT.
- [ ] Save response/edit URL and confirmation; respect organizer post-deadline change policy.
- [ ] Maintain reviewer access through evaluation/finals; prior team notes say through November 22 (reconfirm with organizers).

## Schedule supplied by team

Technical evaluation November 9–12; Top 8 November 13; online final November 15. Connected Gmail search returned no matching November 6 organizer email, so these are team-supplied dates; the deadline is independently corroborated by the form.

[Form content](MUGVN2026_FORM_CONTENT.md) · [Release report](MUGVN2026_RELEASE_REPORT.md) · [Judge Q&A](MUGVN2026_JUDGE_QA.md)
