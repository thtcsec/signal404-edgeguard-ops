# Independent final video audit — November 6

**PASS with editorial/readability caveats. Final bytes preserved; no rebuild or recapture.**

| Property | Independently measured |
| --- | --- |
| Path | `docs/video/edgeguard-ops-final-demo.mp4` |
| Duration | 80.100000 s |
| Resolution / pixel format | 1920×1080 / yuv420p |
| Codec / frame rate | H.264 High / 30/1 fps, 2403 frames |
| File size | 5,458,614 bytes |
| Audio | AAC LC, stereo 44,100 Hz, 80.085011 s |
| Audio volume | mean and maximum −91.0 dB (silent track) |
| SHA-256 | `deb7e1ababa4826dc5470ba098aa9537f043449713d5dfc11043bcebe673d348` |
| Full stream decode | `ffmpeg -v error -i docs/video/edgeguard-ops-final-demo.mp4 -f null -` exits 0 |
| Git | MP4 ignored, not staged |

Commands used: ffprobe `-show_streams -show_format -of json`; Get-FileHash SHA256; full ffmpeg decode; audio `volumedetect`; independent 5-second contact sheet plus before/after boundary frames at 2.7/2.95, 30.7/30.95, 46.7/46.95, 63.2/63.45, 77.2/77.45 and 79.7 seconds. Frames are private QA artifacts under `artifacts/submission-qa/`, not replacements for historical previews. No interactive media-player playback is claimed; full decode confirms stream playability.

## Visual observations

- Title 0–2.8 s; Inject 2.8–30.8; Detect 30.8–46.8; Respond 46.8–63.3; Verify 63.3–77.3; close 77.3–80.1. Sampled every scene and both sides of each cut.
- Inject shows healthy/full start, GPU over 85°C, FPS degradation and commanded/reported safe with cooling.
- Detect shows authentic Datadog paused historical graphs and a zoomed RESOLVED log carrying the intended incident ID. Live “GPU now / FPS now” widgets are covered by an explanatory overlay; they cannot be used as recovered historical readings.
- Respond replays a transcript of authentic worker messages in a console, then holds timestamped APPLIED → RECOVERING → RESOLVED lines with matching IDs. Holds are intentional static editorial evidence, not original live worker-process footage, live polling footage or a continuous real-time recording. The replay script `docs/video/recordings/conhost-worker-respond.ps1` prints selected messages; each is independently corroborated by the raw JSON worker log. This provenance limitation is disclosed, not represented as a live capture.
- Verify shows MongoDB RESOLVED / VERIFIED and safe device, with a later safe telemetry sample (13:25:40.599Z, 55.31°C / 18 FPS / 58.47 ms). That query is not the primary JSON snapshot sample at 13:21:30.432Z. Device samples have no run ID; do not claim this later sample independently establishes run identity. Incident/action linkage establishes identity.
- Burned-in English captions are visible, within the canvas in sampled frames. Terminal details are dense and require fullscreen; captions do not obscure the key state lines. Datadog crop deliberately zooms logs; not every dashboard label remains visible during the zoom.
- Cuts are direct editorial cuts, not corrupted frames. Inject includes cooling before the later Detect scene returns to history. Original timeline/held-frame notes remain in the manifest. No accidental black transition or caption clipping observed in inspected samples; this is sampled visual review, not frame-by-frame OCR.

The 90.1-second pre-recut backup remains separate and unchanged. The final checksum is recorded in the existing dirty manifest as an independent audit field; existing timeline and build data are preserved. Host the exact final MP4, verify signed-out/judge-equivalent access and replace the URL placeholder before submission. There is no hosted video URL verified in this review.
