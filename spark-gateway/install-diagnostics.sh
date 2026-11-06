#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
config_file="$HOME/.config/afai-diagnostics.env"
service_file="$HOME/.config/systemd/user/afai-diagnostics.service"
if [[ -e "$config_file" || -e "$service_file" ]]; then
  echo 'Existing diagnostic configuration found. Review it before updating; nothing overwritten.' >&2
  exit 1
fi
command -v rclone >/dev/null
rclone listremotes | rg -q '^knowledge-drive:$'
python3 -m venv "$project_dir/spark-gateway/.diagnostic-venv"
"$project_dir/spark-gateway/.diagnostic-venv/bin/pip" install -r "$project_dir/spark-gateway/diagnostic-requirements.txt"
mkdir -p "$HOME/.config/systemd/user"
umask 077
cat > "$config_file" <<'ENV'
AFAI_DIAGNOSTICS_ENABLED=1
SPARK_VLLM_URL=http://127.0.0.1:8001
AFAI_DIAGNOSTIC_RCLONE_REMOTE=knowledge-drive
AFAI_DIAGNOSTIC_DRIVE_FOLDER=1DqdrricH-3vNmZBs_wURJ12aa0RifLBi
AFAI_DIAGNOSTIC_DAILY_LIMIT=20
AFAI_DIAGNOSTIC_IP_DAILY_LIMIT=3
AFAI_TRUST_CLOUDFLARE=1
ENV
cat > "$service_file" <<UNIT
[Unit]
Description=AFAI automation diagnostic PDF service
After=network-online.target
[Service]
WorkingDirectory=$project_dir/spark-gateway
EnvironmentFile=$config_file
ExecStart=$project_dir/spark-gateway/.diagnostic-venv/bin/uvicorn diagnostic_service:app --host 127.0.0.1 --port 8016 --workers 1 --no-access-log --no-proxy-headers
Restart=on-failure
RestartSec=5
UMask=0077
NoNewPrivileges=true
[Install]
WantedBy=default.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now afai-diagnostics.service
printf '%s\n' 'Installed on loopback :8016. Follow DIAGNOSTICS.md to route /diagnostics through the existing Cloudflare tunnel and test a real PDF.'
