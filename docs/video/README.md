# EdgeGuard Ops — demo video (local deliverable)

## Submission file (local)

| Artifact | Path |
| --- | --- |
| **Final MP4** | `docs/video/edgeguard-ops-final-demo.mp4` |
| Subtitles | `docs/video/edgeguard-ops-subtitles.srt` |
| Voice-over WAV | `docs/video/voiceover-vi.wav` |
| Build manifest | `docs/video/video-build-manifest.json` |
| Preview frames | `docs/video/preview-frames/` |
| Datadog graph captures | `docs/video/captures/` |

Large MP4 / WAV / scene intermediates are **gitignored**. Rebuild locally before upload:

```powershell
python scripts/fetch-datadog-captures.py   # optional authentic historical graphs
python scripts/build-demo-video.py
```

## Evidence policy

- Datadog graphs in `captures/` come from the **Datadog graph snapshot API** for the verified incident window (`2026-10-18 08:48–08:55 UTC`).
- Monitor UI Alert/OK screenshots require an authenticated browser session; if absent, the video uses **labeled** status cards + MongoDB evidence (never fabricated dashboards).
- Narration explicitly discloses the **staged Alert** (delayed response-worker) and that **111.4s ≠ autonomous MTTA**.
- All telemetry is labeled **SYNTHETIC**.

## Voice-over

Primary: `edge-tts` voice `vi-VN-NamMinhNeural`  
Fallback: `gTTS` (`lang=vi`) when edge-tts returns no audio.
