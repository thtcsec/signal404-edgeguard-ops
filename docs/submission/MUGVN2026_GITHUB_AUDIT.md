# Final GitHub submission audit — November 7, 2026

## Verdict: NO-GO for submission

The repository is PUBLIC, but judges currently see remote `main` at **`639c83a223c94b6d717450e7d7c8f66d9c10ff3d`**, not the hardened release. Only `refs/heads/main` is advertised. The hardening branch and `40ee9ee` commit pages return anonymous HTTP 404. The final MP4 still has no hosted URL. No push, merge, deployment, visibility change or form submission occurred during this audit.

## Git synchronization

At audit start: branch `mugvn2026/submission-hardening`, HEAD **`40ee9ee58f3a638f364850db2b5ab647b0d6b482`**. Local `main` and `origin/main` matched remote main. The remote is the expected `https://github.com/thtcsec/signal404-edgeguard-ops.git`; `git ls-remote --heads origin` confirms the live branch state.

| Commit | Local contents absent from remote main |
| --- | --- |
| `b8cf961` | Runtime reliability/security corrections and targeted tests |
| `40ee9ee` | Judge-first docs, form content, Q&A, walkthrough, source logs and editable November deck |

There was no failed transfer: earlier instructions expressly prohibited pushing without approval. Both commits therefore remained local. Public visibility does not synchronize commits or working-tree files. The committed difference `main...40ee9ee` is 32 files, 779 insertions and 444 deletions, including listed binaries.

The index was empty. Unstaged work included later validation pointers, the current checklist/report, 80.1-second SRT/manifest, editorial QA, preview replacements/deletions and video-builder edits. Untracked work included the November 6 validation JSON/report and unrelated recording scratch files. Full initial diffs/status were saved in ignored `artifacts/github-audit-20261107/`.

The final November 6 validation report and JSON were not yet in **any** commit. The documentation-only reconciliation commit **`f770f9618fe0de73ba1b8c9c98e791e238369a79`** (`f770f96`) adds them, current corrections, the verified existing SRT/manifest and the link audit. It descends from `40ee9ee` and has an identical product/runtime tree (`git diff 40ee9ee f770f96 -- services shared apps tests docker-compose.yml` is empty).

Unrelated user editorial QA, builder and preview changes remain unstaged; other untracked recordings are excluded. Existing SRT bytes were verified and retained as-is. Historical baseline and original E2E records are preserved. No blanket add, reset, stash or history rewrite was used.

## Local corrections

- Current README, architecture, submission/form/checklist/Q&A and slide content now say PUBLIC and distinguish published old main from the unpublished local release.
- November 6 private-repository observations remain dated historical findings with explicit November 7 updates.
- The Mermaid diagram names `telemetry`, `devices`, `incidents`, and `remediation_actions`. It labels reported-sample ingest, simulator polling/HTTP response, worker-only command updates, incident/action lifecycle writes and Datadog Agent/cloud flow. No hardware command push, change streams or Datadog-driven decision loop is implied.
- Current claims match source: HTTP 202 ingest; polling workers; time-series, 14-day default TTL and window aggregation; continuous recovery gate; dashboard/monitor/logs and cloud-verified **telemetry-api APM only**.
- The video guide, SRT and manifest identify the actual silent 80.1-second final. Historical voiced/TTS/90-second alternatives are not substituted.
- The editable November deck footer now reflects public visibility. Eight slides and layout are preserved; package/layout/import checks and visual review pass. The original October deck remains unchanged. Native PowerPoint playback was not performed.
- A genuine cropped frame from the unchanged MP4 at 35 seconds is prepared under `docs/submission/assets/`. It removes account/header chrome while retaining the explanatory historical/live-widget overlay; no values or incident text are replaced.
- Manifest `qa_frames` are explicitly scoped to local uncommitted preview edits. Older committed previews are historical. Unreviewed builder/preview edits are outside this publication commit; do not rebuild the final MP4.

The official form was anonymously readable (HTTP 200). Deadline remains **November 8, 2026, 23:59 ICT**. No answers were transmitted.

## Judge-access audit

Unsigned requests used no cookies or authentication. HTTP 200 after a login redirect does not establish dashboard access. Machine observations: [MUGVN2026_LINK_AUDIT.json](MUGVN2026_LINK_AUDIT.json).

| URL | Exists? | Accessible without permission? | Correct artifact? | Result |
| --- | --- | --- | --- | --- |
| https://github.com/thtcsec/signal404-edgeguard-ops | Yes, 200 | Yes | Repository is public, but old main only | BLOCKED for final release |
| https://github.com/thtcsec/signal404-edgeguard-ops/blob/main/README.md | Yes, 200 | Yes | No: old October 31 deadline | BLOCKED |
| https://github.com/thtcsec/signal404-edgeguard-ops/blob/main/docs/ARCHITECTURE.md | Yes, 200 | Yes | No: 501/idle scaffold | BLOCKED |
| https://github.com/thtcsec/signal404-edgeguard-ops/tree/mugvn2026/submission-hardening | No, 404 | No | Local branch not published | BLOCKED |
| https://github.com/thtcsec/signal404-edgeguard-ops/commit/40ee9ee58f3a638f364850db2b5ab647b0d6b482 | No, 404 | No | Tested commit not published | BLOCKED |
| https://app.datadoghq.com/dashboard/9rr-a4u-2st | Login response | No; redirects to `/account/login` | Org dashboard unavailable anonymously | BLOCKED |
| https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/main/docs/video/recordings/still-dashboard.png | Yes, 200 | Yes | Authentic October 21 capture; bytes match local file | PASS as historical screenshot, with caveats below |
| https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/main/docs/video/recordings/still-dashboard-logs.png | Yes, 200 | Yes | Authentic historical capture; bytes match local | PASS with same caveats |
| https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/mugvn2026/submission-hardening/docs/submission/assets/datadog-oct21-captioned-video-frame.png | Branch absent | Not yet | Preferred screenshot prepared locally | BLOCKED pending approved publication |
| Demo video URL | Not supplied | Not established | Correct MP4 local only | BLOCKED: human hosting action |
| https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/main/docs/presentation/EdgeGuard-Ops-Submission-20261106.pptx | No, 404 | No | Current deck not published | BLOCKED |
| https://raw.githubusercontent.com/thtcsec/signal404-edgeguard-ops/main/docs/presentation/EdgeGuard-Ops-Judge-Deck.pptx | Yes, 200 | Yes | Historical deck, obsolete deadline | BLOCKED as current presentation |
| Optional live demo | No URL | N/A | No public live application offered | Optional: leave blank |

Existing public screenshots can support the required authentic screenshot link when labeled correctly: top graphs and ID-correlated logs use the paused October window; lower GPU-now/FPS-now values are capture-time values, not recovered telemetry. The preferred cropped video frame retains this distinction visibly after publication. A public PNG requires no Datadog account invitation or credential sharing.

Remote manifest/SRT return 200 but describe the previous 90.1-second edit. Remote November release reports return 404. Public accessibility alone does not make them correct final artifacts.

## Video and tested-code provenance

Independent ffprobe: **80.100000 s**, **1920×1080 H.264**, **30 fps**, AAC, **5,458,614 bytes**. Local SRT ends at `00:01:20,100`. Burned captions sampled in the Datadog and closing scenes agree with the SRT. The earlier full decode and boundary inspection evidence remains available. No video rebuild, edit or recapture occurred.

Unchanged SHA-256:

`deb7e1ababa4826dc5470ba098aa9537f043449713d5dfc11043bcebe673d348`

The video depicts October 21 run `20261021202014`, including editorial compression and corroborated worker-message replay. It **does not record `40ee9ee`** or the November 6 validation. Separate [validation report](MUGVN2026_RELEASE_VALIDATION.md) and [machine evidence](../evidence/final-release-validation-20261106225132.json) retain the current-code results.

Product source/config/test trees in the intended publication are Git-identical to `40ee9ee`. Only documentation, evidence, presentation, screenshot and video metadata/SRT differ. The local user-edited video builder is excluded. No behavior-affecting changes require a new E2E.

| Execution | Result | Scope |
| --- | --- | --- |
| .NET focused tests executed November 7 | 11 passed, 0 failed | Detached 40ee9ee Release binaries |
| Python tests executed November 7 | 6 passed, 0 failed | Same exact source |
| Full .NET suite, November 6 | 15 passed, 0 failed | TRX re-read; includes four Mongo-backed tests |
| Real-Mongo retry/failure checks, November 6 | 16 passed | Results re-read; not invoked again today |
| Automatic E2E, November 6 | PASS | 40ee9ee, default 20-second recovery gate |
| Full Mongo suite/E2E today | NOT RUN | No runtime changes; Docker daemon currently unavailable; no reset attempted |
| New live Datadog/APM/monitor validation | NOT RUN | Historical evidence only |

Exact full-runtime-tested SHA: **`40ee9ee58f3a638f364850db2b5ab647b0d6b482`**. Publication candidate HEAD: **`f770f9618fe0de73ba1b8c9c98e791e238369a79`** — documentation-only descendant with identical product code, not a newly filmed runtime.

## Security and scope

Credential-pattern review covers tracked/proposed text, decoded UTF-16 logs and PPTX XML; no key/token/private-key/credential-URI matches were found. Binary review is bounded: not every historical image is OCR-audited; this is not full-history/entropy clearance. Workstation/project paths remain in historical capture scripts and validation metadata; they are not credentials. Exclude `.env`, ignored artifacts/browser profiles, MP4/WAV files and unrelated recording scratch files from publication.

Historical captures contain account/trial chrome; no keys or production/customer data were observed in inspected screenshots. The preferred crop removes that chrome. Device data is synthetic; no real camera stream is connected.

Dependency advisories remain visible: transitive **SharpCompress 0.30.1 Moderate** and **Snappier 1.0.0 High**. No dependency migration, feature or infrastructure was added. Lab-only authentication and single-worker limits remain explicit.

## Safe publication commands — instructions only

No command in this section was executed. Push only after explicit approval. Committed content can be published without changing the dirty working tree; do not use blanket add, reset, stash or force-push.

```powershell
Set-Location D:/tu_projects/signal404-edgeguard-ops
git status --short
git log -3 --oneline
git diff 40ee9ee HEAD -- services shared apps tests docker-compose.yml Directory.Build.props global.json
# Expected: no product/runtime differences.
git ls-remote --heads origin
git push --dry-run origin mugvn2026/submission-hardening:refs/heads/mugvn2026/submission-hardening
# Only after approval to publish this audited branch:
git push --set-upstream origin mugvn2026/submission-hardening
```

Publishing the branch alone leaves default main stale. If the owner separately approves fast-forwarding main, use a normal non-force push without switching branches:

```powershell
# Separate approval for main publication required:
git push origin mugvn2026/submission-hardening:refs/heads/main
git ls-remote --heads origin
```

If remote history changes or a push is rejected, stop and inspect; do not force. Recheck unsigned README, architecture, screenshot, deck and report URLs at the published SHA. Host the exact MP4 separately, verify permission-free playback/download and replace the form placeholder. The registered leader must review attestations and submit before November 8, 23:59 ICT. No visibility change is necessary: the repository is already public.
