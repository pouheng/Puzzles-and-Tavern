@echo off
cd /d "%~dp0"

echo 請選擇:
echo 1. 執行遊戲
echo 2. 開發者工具
echo.

set /p choice=請輸入選項 (1/2): 

if "%choice%"=="1" (
    python main.py
) else if "%choice%"=="2" (
    python dev_tool.py
) else (
    python main.py
)

pause
