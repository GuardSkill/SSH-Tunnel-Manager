@echo off
echo Installing PyInstaller if needed...
pip install pyinstaller

echo.
echo Cleaning old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable...
pyinstaller --name=SSHTunnelManager --windowed --onefile --clean ssh_tunnel_manage_v2.py
@REM pyinstaller --name=SSHTunnelManager --windowed --onefile --clean ssh_tunnel_manage_v1.py


echo.
echo Done! Check the dist folder for SSHTunnelManager.exe
pause