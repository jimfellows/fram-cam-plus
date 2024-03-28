; -------------------------------
; FramCam installer NSI setup
; -------------------------------
; What are we trying to do:
; 1.) take in compiled python app results from cx_Freeze
; 2.) Copy those contents to the install directory selected by user (C:\trawl_backdeck by default)

; Helpful NSIS examples (https://nsis.sourceforge.io/Download)
; https://nsis.sourceforge.io/Examples/example2.nsi
; https://nsis.sourceforge.io/A_simple_installer_with_start_menu_shortcut_and_uninstaller
; https://nsis-dev.github.io/NSIS-Forums/html/t-284449.html

;--------------------------------
;Include Modern UI, nsDialogs
;--------------------------------
!include "MUI2.nsh"
!include nsDialogs.nsh
!include 'LogicLib.nsh'

;-------------------------------
; General Info
;-------------------------------
!define APPNAME "FramCam+"
!define ICON_PATH ".\..\resources\icons\noaa_installer_yellow.ico"
!define NOAA_BMP ".\..\resources\images\NOAA_logo.bmp"

; The name of the installer
Name "${APPNAME} ${VERSION}"

; The file to write out as installer
OutFile ".\FramCam+_setup_${VERSION}.exe"
Icon ".\..\resources\icons\noaa_installer_yellow.ico"

; Request application privileges for Windows Vista
RequestExecutionLevel user

; Build Unicode installer
Unicode True

; Suggested install dir, profile gives us current user dir
InstallDir $PROFILE\desktop\FramCam+

;--------------------------------
;Interface Settings
;--------------------------------
  !define MUI_ABORTWARNING
  !define MUI_HEADERIMAGE              ".\..\resources\images\NOAA_logo.bmp"
  !define MUI_ICON                     ".\..\resources\icons\noaa_installer_yellow.ico"
  !define MUI_HEADERIMAGE_BITMAP       ".\..\resources\images\NOAA_logo.bmp"
  !define MUI_WELCOMEFINISHPAGE_BITMAP ".\..\resources\images\NOAA_logo.bmp"
  !define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
  !define MUI_WELCOMEFINISHPAGE_BITMAP_NOSTRETCH

;--------------------------------
;Pages
;--------------------------------
  !insertmacro MUI_PAGE_WELCOME
  Page custom PAGE_OPTIONS_CREATE PAGE_OPTIONS_LEAVE  ; custom options page
  !insertmacro MUI_PAGE_LICENSE ".\..\LICENSE"
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES

  ;------------------------------
  ; Finish Page
  ;------------------------------
  ; Checkbox to launch the app after install completes
  !define MUI_FINISHPAGE_RUN
  !define MUI_FINISHPAGE_RUN_TEXT "Launch Application"
  !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchApp"
  !insertmacro MUI_PAGE_FINISH

;--------------------------------
;Languages
;------------------------------
  !insertmacro MUI_LANGUAGE "English"

;-------------------------------
; Sections
;-------------------------------
; The stuff to install
Section "FramCam+"

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Get all contents under fc
  File /r .\exe.win64-3.6\FramCam+\*

  ; if selected, create desktop and start shortcut
  Call CreateDesktopShortcut
  Call CreateStartShortcut

SectionEnd

Function LaunchApp
  Exec "$instdir\FramCam+.exe"
FunctionEnd

; vars to save button state on screen leave
Var CheckDesktopShortcut_State
Var CheckStartShortcut_State
Var CheckArchive_State
Var CheckWheelhouseDB_State

Function PAGE_OPTIONS_CREATE
    nsDialogs::Create 1018
    !insertmacro MUI_HEADER_TEXT "Custom Options" "Check options for install:"

    ; desktop shortcut
    ${NSD_CreateCheckBox} 0 20u 100% 10u "Create Desktop Shortcut"
    Pop $1
    ${NSD_Check} $1  ; default to checked

    ; zip and copy existing version to archive in same installdir
    ${NSD_CreateCheckBox} 0 40u 100% 10u "Create Start Menu Shortcut"
    Pop $2
    ${NSD_Check} $2  ; default to checked

    nsDialogs::Show
FunctionEnd

; stash checkbox state when leaving custom options
Function PAGE_OPTIONS_LEAVE
    ${NSD_GetState} $1 $CheckDesktopShortcut_State
    ${NSD_GetState} $2 $CheckStartShortcut_State
    ${NSD_GetState} $3 $CheckArchive_State
    ${NSD_GetState} $4 $CheckWheelhouseDB_State
FunctionEnd

Function CreateDesktopShortcut
    ${If} $CheckDesktopShortcut_State <> 0
        CreateShortcut "$DESKTOP\FramCam+_${VERSION}.lnk" "$INSTDIR\FramCam+.exe"
    ${EndIf}
FunctionEnd

Function CreateStartShortcut
    ${If} $CheckStartShortcut_State <> 0
        Delete $SMPROGRAMS\FramCam+\*.*
        createDirectory "$SMPROGRAMS\FramCam+"
        createShortCut "$SMPROGRAMS\FramCam+\FramCam+.lnk" "$INSTDIR\FramCam+.exe" "" "$INSTDIR\lib\icons\black_nautilus.ico"
    ${EndIf}
FunctionEnd