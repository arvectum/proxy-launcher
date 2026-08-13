# Arvectum Proxy Launcher 0.2.2

- Updated application icon for the window, taskbar, shortcuts and Windows
  executable metadata.
- Visible version updated to 0.2.2 in the application and Windows properties.
- Keeps the P0.3 safe upgrade flow: verified staging, exact-path process close,
  protected recovery handling and ownership-safe autostart migration.

Known limitations:

- WinHTTP is configured separately and is not changed by this application.
- This release is unsigned; Authenticode signing is pending a separate final
  audit.
