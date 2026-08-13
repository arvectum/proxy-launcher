#define AppName "Arvectum Proxy Launcher"
#define AppVersion "0.2.1"
#define AppPublisher "ООО «Арвектум»"
#define AppURL "https://arvectum.com"
#define AppDir "{userdocs}\ArvectumProxyLauncher"

[Setup]
AppId={{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
DefaultDirName={#AppDir}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=release\setup
OutputBaseFilename=ArvectumProxyLauncherSetup
SetupIconFile=assets\arvectum.ico
Uninstallable=no
CreateAppDir=yes
CloseApplications=yes
CloseApplicationsFilter=Arvectum Proxy Launcher.exe
RestartApplications=no
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\Arvectum Proxy Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "restore_network.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALL.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "RELEASE_NOTES_0.2.1.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Arvectum Proxy Launcher"; Filename: "{app}\Arvectum Proxy Launcher.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Arvectum Proxy Launcher"; Filename: "{app}\Arvectum Proxy Launcher.exe"; WorkingDir: "{app}"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#AppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#AppVersion}"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "Publisher"; ValueData: "{#AppPublisher}"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\Arvectum Proxy Launcher.exe"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#AppURL}"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "UninstallString"; ValueData: "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""{app}\uninstall.ps1"" -AppDir ""{app}"""
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ArvectumProxyLauncher"; ValueType: string; ValueName: "QuietUninstallString"; ValueData: "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""{app}\uninstall.ps1"" -AppDir ""{app}"" -NonInteractive"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    SaveStringToFile(
      ExpandConstant('{app}\\.arvectum-install-owner'),
      'ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER' + #13#10,
      False);
end;

function CloseOwnedLauncher(const ExistingExe: String): Boolean;
var
  PowerShell, Params: String;
  ResultCode: Integer;
begin
  PowerShell := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
  Params := '-NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq ''Arvectum Proxy Launcher.exe'' -and $_.ExecutablePath -and [IO.Path]::GetFullPath($_.ExecutablePath) -ieq [IO.Path]::GetFullPath(''' + ExistingExe + ''') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }"';
  Result := Exec(PowerShell, Params, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ExistingExe, StateDir, InternetBackup, EnvBackup: String;
  ResultCode: Integer;
begin
  Result := '';
  ExistingExe := ExpandConstant('{app}\Arvectum Proxy Launcher.exe');
  StateDir := ExpandConstant('{localappdata}\Arvectum\ProxyLauncher');
  InternetBackup := AddBackslash(StateDir) + 'proxy_internet_backup.json';
  EnvBackup := AddBackslash(StateDir) + 'proxy_env_backup.json';
  if FileExists(ExistingExe) then begin
    if not Exec(ExistingExe, '--stop', ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ResultCode) then begin
      Result := 'UPDATE BLOCKED: could not start safe rollback of the previous version.';
      exit;
    end;
    if ResultCode <> 0 then begin
      Result := 'UPDATE BLOCKED: previous version did not complete network rollback.';
      exit;
    end;
    if not CloseOwnedLauncher(ExistingExe) then begin
      Result := 'UPDATE BLOCKED: could not close the previous Launcher window.';
      exit;
    end;
  end;
  if FileExists(InternetBackup) or FileExists(EnvBackup) then
    Result := 'UPDATE BLOCKED: recovery backups remain. Restore network before updating.';
end;
