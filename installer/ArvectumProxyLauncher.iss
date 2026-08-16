; APL-REL-006 / APL-WIN-009. PayloadDir and AppVersion are supplied only by the canonical build script.
#ifndef AppVersion
  #error AppVersion must be supplied by tools/build_windows_installer.ps1
#endif
#ifndef PayloadDir
  #error PayloadDir must be supplied by tools/build_windows_installer.ps1
#endif
#define AppName "Arvectum Proxy Launcher"
#define AppPublisher "ООО «Арвектум»"
#define AppDir "{userdocs}\ArvectumProxyLauncher"
#define SetupName "Arvectum-Proxy-Launcher-" + AppVersion + "-windows-x64-setup"
#define RepairExeName "Arvectum Proxy Launcher Repair.exe"

[Setup]
AppId={{6A5A0706-4015-4EAF-BFA1-25EF435C9E1B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={#AppDir}
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputBaseFilename={#SetupName}
OutputDir=..\out\installer
SetupIconFile=..\assets\arvectum.ico
UninstallDisplayIcon={app}\Arvectum Proxy Launcher.exe
Uninstallable=yes
Compression=lzma2
SolidCompression=yes
CloseApplications=no

[Files]
; All required files are compiled into the setup executable; no portable folder is consulted at install time.
Source: "{#PayloadDir}\Arvectum Proxy Launcher.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; AfterInstall: InstallVerifiedPayload
Source: "{#PayloadDir}\build_manifest.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\build_manifest.json"; Flags: dontcopy
Source: "{#PayloadDir}\upgrade_helper.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\uninstall_helper.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\upgrade_helper.ps1"; Flags: dontcopy
Source: "..\INSTALL.txt"; DestDir: "{app}"; Flags: ignoreversion

[UninstallDelete]
Type: files; Name: "{app}\Arvectum Proxy Launcher.exe"
Type: files; Name: "{app}\Arvectum Proxy Launcher.exe.new"
Type: files; Name: "{app}\Arvectum Proxy Launcher.exe.old"
Type: files; Name: "{app}\{#RepairExeName}"
Type: files; Name: "{app}\.arvectum-install-owner"

[Icons]
Name: "{autoprograms}\Arvectum Proxy Launcher"; Filename: "{app}\Arvectum Proxy Launcher.exe"; WorkingDir: "{app}"
Name: "{autoprograms}\Repair Arvectum Proxy Launcher"; Filename: "{app}\{#RepairExeName}"; Parameters: "/SP-"; WorkingDir: "{app}"
Name: "{autodesktop}\Arvectum Proxy Launcher"; Filename: "{app}\Arvectum Proxy Launcher.exe"; WorkingDir: "{app}"

[Code]
function RunEmbeddedHelper(const Helper, Arguments: String; var ErrorText: String): Boolean;
var
  PowerShell, HelperPath: String;
  ExitCode: Integer;
begin
  ExtractTemporaryFile(Helper);
  ExtractTemporaryFile('Arvectum Proxy Launcher.exe');
  ExtractTemporaryFile('build_manifest.json');
  HelperPath := ExpandConstant('{tmp}\' + Helper);
  PowerShell := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
  Result := Exec(PowerShell, '-NoProfile -ExecutionPolicy Bypass -File "' + HelperPath + '" ' + Arguments,
    '', SW_HIDE, ewWaitUntilTerminated, ExitCode);
  if (not Result) or (ExitCode <> 0) then begin
    ErrorText := 'InstallFailure: ' + Helper + ' failed with exit code ' + IntToStr(ExitCode);
    Result := False;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  { The actual install/repair occurs in the [Files] callback below. This event
    remains intentionally side-effect free so silent and interactive modes share
    the same verified placement path. Re-running Setup is the repair flow. }
  Result := '';
end;

procedure InstallVerifiedPayload();
var ErrorText: String;
begin
  { Runs during the primary [Files] phase. RaiseException makes hash, ownership,
    rollback, repair, or transactional replacement failure abort Setup. }
  if not RunEmbeddedHelper('upgrade_helper.ps1', '-PayloadRoot "' + ExpandConstant('{tmp}') + '" -InstallRoot "' + ExpandConstant('{app}') + '"', ErrorText) then
    RaiseException(ErrorText);
end;

procedure CacheRepairInstaller();
var
  SourcePath, TargetPath: String;
begin
  SourcePath := ExpandConstant('{srcexe}');
  TargetPath := ExpandConstant('{app}\{#RepairExeName}');
  { When repair is launched from the cached copy, the source and target are the
    same file and no copy is necessary. For downloaded/newer Setup builds, cache
    the exact Setup that successfully completed this install/repair session. }
  if CompareText(SourcePath, TargetPath) <> 0 then begin
    if not FileCopy(SourcePath, TargetPath, False) then
      RaiseException('InstallFailure: could not cache the Windows repair installer.');
  end;
  if not FileExists(TargetPath) then
    RaiseException('InstallFailure: cached Windows repair installer is missing.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    SaveStringToFile(ExpandConstant('{app}\.arvectum-install-owner'), 'ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER' + #13#10, False);
    CacheRepairInstaller();
  end;
end;

function RunInstalledUninstallHelper(var ErrorText: String): Boolean;
var
  PowerShell, HelperPath: String;
  ExitCode: Integer;
begin
  HelperPath := ExpandConstant('{app}\uninstall_helper.ps1');
  if not FileExists(HelperPath) then begin
    ErrorText := 'InstallFailure: installed uninstall helper is missing.';
    Result := False;
    exit;
  end;
  PowerShell := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
  Result := Exec(PowerShell, '-NoProfile -ExecutionPolicy Bypass -File "' + HelperPath + '" -InstallRoot "' + ExpandConstant('{app}') + '"', '', SW_HIDE, ewWaitUntilTerminated, ExitCode);
  if (not Result) or (ExitCode <> 0) then begin
    ErrorText := 'InstallFailure: installed uninstall helper failed with exit code ' + IntToStr(ExitCode);
    Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
var ErrorText: String;
begin
  Result := RunInstalledUninstallHelper(ErrorText);
  if not Result then
    MsgBox(ErrorText, mbError, MB_OK);
end;
