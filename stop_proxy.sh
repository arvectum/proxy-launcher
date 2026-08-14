#!/bin/bash
# Остановка proxy-движка + снятие системного прокси (Linux/GNOME)
cd "$(dirname "$0")"
python3 "$(dirname "$0")/proxy_core.py" --stop
echo "Proxy stopped, system proxy removed."