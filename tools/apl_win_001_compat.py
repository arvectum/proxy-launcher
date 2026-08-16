from pathlib import Path

path = Path(__file__).resolve().parents[1] / "proxy_gui.py"
text = path.read_text(encoding="utf-8")

old = '''        self.btn_restore.configure(\n            style="Mint.TButton" if view["restore_primary"] else "Ghost.TButton")\n'''
new = '''        if view["restore_primary"]:\n            self.btn_restore.configure(style="Mint.TButton")\n        else:\n            self.btn_restore.configure(style="Ghost.TButton")\n'''
if old not in text:
    raise SystemExit("restore style block not found")
text = text.replace(old, new, 1)

marker = 'def _final_status_view(running, enabled, pending, orphaned_pac, stale_proxy):\n'
compat = 'LEGACY_ORPHANED_PAC_DIAGNOSTIC = "ОБНАРУЖЕН СТАРЫЙ PAC ARVECTUM"\n\n\n'
if marker not in text:
    raise SystemExit("status helper marker not found")
text = text.replace(marker, compat + marker, 1)

path.write_text(text, encoding="utf-8")
