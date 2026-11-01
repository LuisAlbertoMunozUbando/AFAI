# AFAI Spark Q&A → Google Docs

**Status:** code prepared; NOT deployed to the Spark. The public site stays in preview until its gateway URL is configured.

## Setup on spark-110e

1. Confirm vLLM: `curl -s http://127.0.0.1:8001/v1/models`. Choose the best tested model and set its exact ID in `AFAI_MODEL_PREFERENCE`. If exactly one is loaded it is selected automatically.
2. Create a venv and install: `pip install -r spark-gateway/requirements.txt`.
3. Copy `spark-gateway/.env.example` to a private local `.env`. Generate `AFAI_API_TOKEN` using `python3 -c 'import secrets; print(secrets.token_urlsafe(48))'`. Never commit secrets.
4. Configure **Google Application Default Credentials** for a Google account with permission to create files in folder `1XH56iWCCPidIG5SVO36otRkQCrx3DUbV`. A user OAuth ADC token with Drive and Docs scopes is preferable for a personal My Drive folder. A service account may require a shared-drive destination or domain-wide delegation and must have access. Store credentials on Spark only, not in the website. Test permissions before rollout.
5. From `spark-gateway`: `set -a; . ./.env; set +a; uvicorn app:app --host 127.0.0.1 --port 8015 --workers 1`.
6. Expose **only the gateway** via a secured HTTPS reverse proxy/Cloudflare Tunnel; never expose vLLM :8000. Configure `window.AFAI_GATEWAY_URL` in index.html with the public HTTPS gateway origin. The pilot UI asks for a token per session; no token is stored in GitHub.
7. Test `GET /health` and `POST /chat` with Authorization Bearer header. Confirm a real Google Doc appears in the folder and the returned `saved` flag is true.

## Naming and behavior

Every successful question/answer creates a separate native Google Doc named `YYYY-MM-DD_Question_N`, using **America/Monterrey** local date and the next available daily number. Contents: date, model, intent, full question and answer. The folder is queried each time to continue numbering after restarts. One gateway worker avoids concurrent filename collisions. For multiple instances, replace the in-memory lock with a transactional counter. The response reports `saved:false` if Google Docs creation fails; the frontend must not claim success.

## Security warning

The destination folder was observed to allow **anyone with the link to edit**. Restrict sharing before storing confidential questions and answers. The UI's Student/Silver/etc selection is not authentication. A shared browser-entered bearer token is only for a small trusted pilot, not public multiuser access. Implement user OAuth, identity-bound quotas, authorization, and audit logs before public release. No RAG, tools, agent execution, robot/IoT control, or simulations are connected in this phase.

## Smoke test

```bash
curl -s -H "Authorization: Bearer $AFAI_API_TOKEN" http://127.0.0.1:8015/health
curl -s -X POST http://127.0.0.1:8015/chat -H "Authorization: Bearer $AFAI_API_TOKEN" -H "Content-Type: application/json" -d '{"query":"How do I evaluate an industrial robotics pilot?","intent":"analyze","tier":"silver"}'
```

## Reuse audit (GitHub source, not live host verification)

- `youtube2knowledge/docker-compose.spark.yml` maps vLLM container port 8000 to host loopback **8001**. Reuse `youtube2knowledge-llm-1`; do not start another vLLM instance.
- `youtube2knowledge` has a `drive-sync` service based on rclone, but it archives JSON/Markdown, **not native Google Docs**. AFAI therefore uses Google Docs API for its required native Docs output, reusing the existing Drive authentication only if compatible.
- `Research-Knowledge-Backend` already has SQLite FTS5, embeddings, hybrid retrieval and grounded RAG. Keep that existing service untouched during the initial Q&A-only phase.
- ASR, slide extraction and VLM workers are not used for text-only Q&A.

### Inspect running services before deployment

```bash
sudo systemctl --no-pager --full status research-knowledge-api.service research-knowledge-web.service slideextractor-worker.service
sudo docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'
curl -fsS http://127.0.0.1:8001/v1/models | python3 -m json.tool
curl -fsS http://127.0.0.1:8020/healthz
```

Only change the AFAI service, not the stable Knowledge or YouTube2Knowledge services. If the vLLM host port differs from the checked-in Compose file, use the observed live port in `SPARK_VLLM_URL`.
