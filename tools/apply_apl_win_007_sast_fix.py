from pathlib import Path


path = Path("proxy_gui.py")
text = path.read_text(encoding="utf-8")
old = "            root = ET.fromstring(xml)\n"
new = (
    "            # Task XML is produced locally by Windows schtasks for a fixed task name;\n"
    "            # it is not remote/user-supplied XML. Keep ElementTree dependency-free.\n"
    "            root = ET.fromstring(xml)  # nosec B314\n"
)
if text.count(old) != 1:
    raise SystemExit("expected ElementTree parse site not found exactly once")
path.write_text(text.replace(old, new), encoding="utf-8")
