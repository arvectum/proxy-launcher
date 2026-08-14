#!/bin/bash
# Аварийное восстановление настроек сети (Linux)
cd "$(dirname "$0")"
python3 "$(dirname "$0")/proxy_core.py" --rollback
echo
echo "Network settings restored. You can close this window."
read -r -p "" x