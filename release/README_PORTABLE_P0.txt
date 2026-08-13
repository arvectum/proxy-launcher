Arvectum Proxy Launcher - portable 0.2.3 P0.2 hotfix

1. Extract the ZIP to a normal folder and run "Arvectum Proxy Launcher.exe".
2. The Launcher tries to use its permanent working copy in:
   %USERPROFILE%\Documents\ArvectumProxyLauncher
3. Settings, no_proxy, recovery files and logs remain in:
   %LOCALAPPDATA%\Arvectum\ProxyLauncher
4. If Windows allows the permanent Documents copy, autostart may be enabled normally.
5. If Windows blocks the permanent copy but the original portable EXE is already running,
   the current portable session remains usable. In this fallback mode autostart is disabled
   and existing Run entries are left unchanged rather than redirected to a blocked EXE.
6. Do not move/delete the currently running portable EXE while proxy is active.
7. Do not remove the AppData Arvectum folder while proxy recovery is pending.

For App Control diagnostics run diagnose_app_control.ps1.
For read-only native execution QA run run_p01_native_qa_v2.ps1 with -SourceExe.

This P0.2 package intentionally remains unsigned. Full installer, signing and
SmartScreen/reputation work are deferred to the production release track.
