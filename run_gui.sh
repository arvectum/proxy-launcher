#!/bin/bash
# Arvectum Proxy Launcher — запуск окна лаунчера (Linux)
cd "$(dirname "$0")"
exec python3 "$(dirname "$0")/proxy_gui.py"