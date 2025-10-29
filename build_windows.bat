@echo off
setlocal

echo Ensuring build dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Cleaning old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable...
python -m PyInstaller --name=SSHTunnelManager --windowed --onefile --clean ^
    --collect-all PyQt5 ^
    --hidden-import PyQt5.sip ^
    --icon resources\app_icon.ico ^
    ssh_tunnel_manage_v2.py
@REM python -m PyInstaller --name=SSHTunnelManager --windowed --onefile --clean ^
@REM     --collect-all PyQt5 ^
@REM     --hidden-import PyQt5.sip ^
@REM     --icon resources\app_icon.ico ^
@REM     ssh_tunnel_manage_v1.py


echo.
echo Done! Check the dist folder for SSHTunnelManager.exe
pause
endlocal
