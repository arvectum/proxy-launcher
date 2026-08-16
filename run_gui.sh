#!/bin/bash
# Arvectum Proxy Launcher — запуск окна лаунчера (Linux/Astra)
cd "$(dirname "$0")"
exec python3 "$(dirname "$0")/linux_gui.py"
