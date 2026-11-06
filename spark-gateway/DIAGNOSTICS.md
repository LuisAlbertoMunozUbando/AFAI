# Automation diagnostic service

Implemented in this repository; Spark deployment is not yet verified. On 2026-11-06 the public gateway returned Cloudflare error 1033. The page fails closed and does not submit visitor data while `/diagnostics/health` is unavailable.

## Existing infrastructure preserved

- Existing `afai-gateway.service` / `token_gateway:app` on 127.0.0.1:8015 stays unchanged.
- The diagnostic service runs separately on **127.0.0.1:8016**, one Uvicorn worker.
- Reuses vLLM at `http://127.0.0.1:8001`; chooses a loaded model or `AFAI_MODEL_PREFERENCE`.
- Reuses **knowledge-drive** rclone OAuth without reading or publishing credentials.
- Private Drive destination: `1DqdrricH-3vNmZBs_wURJ12aa0RifLBi` — **AFAI - Automation Diagnostics**. Created at the owner's root and verified owner-only on 2026-11-06. Keep it private; never move it under a shared folder.

## Activate on Spark

Run as the SAME Linux user that owns the working `knowledge-drive` rclone remote:

```bash
cd ~/AFAI
git pull --ff-only
bash spark-gateway/install-diagnostics.sh
```

The script creates an isolated venv and user service; it does not restart or modify existing gateways, vLLM, Knowledge, ASR, or YouTube services. It refuses to overwrite an existing user service/config. Inspect `~/.config/afai-diagnostics.env` to change limits or model selection.

Then edit the existing Cloudflare Tunnel ingress, placing these entries **before** its current AFAI hostname rule (preserve all other hostnames):

```yaml
- hostname: afai-api.albertomunoz.ai
  path: ^/diagnostics(/.*)?$
  service: http://127.0.0.1:8016
- hostname: afai-api.albertomunoz.ai
  service: http://127.0.0.1:8015
```

For a dashboard-managed tunnel, add the equivalent hostname/path rule there. Validate the tunnel config with its actual config path before restarting the existing tunnel. The installer does not guess its path or restart a shared tunnel.

Verify:

```bash
curl --fail http://127.0.0.1:8016/diagnostics/health
curl --fail https://afai-api.albertomunoz.ai/diagnostics/health
systemctl --user status afai-diagnostics.service
```

`ready:true` requires a reachable model and accessible rclone destination. Complete one non-sensitive form submission, download the PDF, and check its copy in the private Drive folder. Do not announce generation as live until that round trip succeeds. Confirm the existing Q&A `/quota` and `/chat` still work. Use `loginctl enable-linger "$USER"` if needed to keep this user service running after logout, according to the host's administration policy.

## What actually runs

1. Local-model intake critique.
2. Local-model architecture/pitch proposal constrained by a checked-in official NVIDIA catalog and a validated JSON schema; one repair attempt for invalid output.
3. A separate critical review with the same local model, labeled as AI review rather than independent expert validation.
4. Escaped, Unicode PDF layout with sources, original pitch and provenance.
5. Private PDF upload through rclone, verified by size and MD5. Failure is disclosed and never reported as a successful archive.

The input is text-only. ASR and video tools are intentionally not invoked on text, and no simulation or robot actions run. Existing Knowledge databases may contain private evidence: this public service does not expose them. Connecting approved/public RAG, video uploads or other running Spark agents requires inspecting their live APIs and access boundaries; these are not claimed as connected.

## API and privacy

- `GET /diagnostics/health`: cached dependency readiness.
- `POST /diagnostics`: intake JSON; allowed Origin and random `Idempotency-Key` required. Returns HTTP 202 and opaque job ID.
- `GET /diagnostics/{id}` and `/pdf`: the same key as a Bearer capability. Never put it in a URL or localStorage. No job listing or Drive URL is exposed.
- Persistent SQLite queue, one inference worker, max five pending requests, default 20 total requests per rolling 24 hours and 3 per daily client IP hash. `CF-Connecting-IP` is trusted only with explicit configuration and a loopback tunnel peer; keep port 8016 loopback-only. Add edge bot/rate protections if traffic grows. Origin checks alone are not bot authentication.
- Email optional, used in filename plus date and random suffix; otherwise company/date/suffix. No email delivery or marketing subscription.
- No request bodies, model responses, emails or tokens are logged. Uvicorn access logs disabled.
- Submission payload cleared when processing finishes; PDF and job expire locally after 24 hours. Cleanup runs once per worker iteration. Drive copies remain until deletion requested. Operator handles deletion requests by report ID.
- Failed archive retries three times; local PDF remains downloadable until expiry. After resolving Drive, operator can copy the retained PDF privately. Expired local files cannot be recovered if archival failed.
- Disable intake with `AFAI_DIAGNOSTICS_ENABLED=0`, then restart the diagnostic service.

## Tests

```bash
python -m pip install -r spark-gateway/diagnostic-requirements.txt pytest pypdf
python -m pytest tests/test_diagnostics.py
node --check assets/diagnostic.js
```

Tests mock model inference and Drive. They verify consent, validation, private downloads, idempotency, queue limits, PDF generation, expiry and archival failures; they do not prove a deployed Spark integration.
