; APL-REL-006. PayloadDir and AppVersion are supplied only by the canonical build script.
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
Uninstallable=yes
Compression=lzma2
SolidCompression=yes
CloseApplications=no

[Files]
; All required files are compiled into the setup executable; no portable folder is consulted at install time.
Source: "{#PayloadDir}\Arvectum Proxy Launcher.exe"; Flags: dontcopy
Source: "{#PayloadDir}\build_manifest.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\upgrade_helper.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\uninstall_helper.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\upgrade_helper.ps1"; Flags: dontcopy
Source: "{#PayloadDir}\uninstall_helper.ps1"; Flags: dontcopy
Source: "..\INSTALL.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Arvectum Proxy Launcher"; Filename: "{app}\Arvectum Proxy Launcher.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Arvectum Proxy Launcher"; Filename: "{app}\Arvectum Proxy Launcher.exe"; WorkingDir: "{app}"

[Code]
function RunEmbeddedHelper(const Helper, const Arguments: String; var ErrorText: String): Boolean;
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
var ErrorText: String;
begin
  Result := '';
  if not RunEmbeddedHelper('upgrade_helper.ps1', '-PayloadRoot "' + ExpandConstant('{tmp}') + '" -InstallRoot "' + ExpandConstant('{app}') + '" -PreflightOnly', ErrorText) then
    Result := ErrorText;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var ErrorText: String;
begin
  if CurStep = ssPostInstall then begin
    SaveStringToFile(ExpandConstant('{app}\.arvectum-install-owner'), 'ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER' + #13#10, False);
    if not RunEmbeddedHelper('upgrade_helper.ps1', '-PayloadRoot "' + ExpandConstant('{tmp}') + '" -InstallRoot "' + ExpandConstant('{app}') + '"', ErrorText) then
      RaiseException(ErrorText);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var ErrorText: String;
begin
  if CurUninstallStep = usUninstall then begin
    if not RunEmbeddedHelper('uninstall_helper.ps1', '-InstallRoot "' + ExpandConstant('{app}') + '"', ErrorText) then
      RaiseException(ErrorText);
  end;
end;
