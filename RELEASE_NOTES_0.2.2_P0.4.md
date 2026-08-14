# Arvectum Proxy Launcher 0.2.2 — P0.4 installer update

- Safely detects and gracefully stops only a strictly proven active legacy
  Arvectum recovery process before updating the installed application.
- Removes stale, proven legacy recovery Run entries and migrates proven legacy
  user autostart to the canonical installation.
- Blocks the update without replacing the installed EXE when ownership,
  shutdown, or network recovery cannot be proven safe.
- Installer console now uses UTF-8 and retains an interactive failure message.

The application EXE and proxy engine are unchanged by this installer-only
update.
