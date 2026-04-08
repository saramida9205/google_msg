[Setup]
AppName=Google Messenger
AppVersion=1.0
DefaultDirName={autopf}\GoogleMessenger
DefaultGroupName=Google Messenger
OutputDir=.\dist_setup
OutputBaseFilename=GoogleMessenger_Setup_v1.4
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "바탕화면 바로가기 생성"; GroupDescription: "추가 아이콘:"; Flags: checkedonce

[Files]
Source: "dist\GoogleMessenger\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Google Messenger"; Filename: "{app}\GoogleMessenger.exe"
Name: "{autodesktop}\Google Messenger"; Filename: "{app}\GoogleMessenger.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\GoogleMessenger.exe"; Description: "Google Messenger 실행"; Flags: nowait postinstall skipifsilent
