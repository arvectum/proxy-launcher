#!/bin/bash
# Запуск proxy-движка в фоне + системный прокси (Linux/GNOME)
cd "$(dirname "$0")"
nohup python3 "$(dirname "$0")/proxy_core.py" --start >/dev/null 2>&1 &
echo "Proxy started. PAC: http://127.0.0.1:8082/proxy.pac"