@echo off
title Shifr Bot - O'rnatish
color 0A
echo.
echo  ╔══════════════════════════════════════╗
echo  ║        SHIFR BOT - O'RNATISH         ║
echo  ╚══════════════════════════════════════╝
echo.

:: Python tekshiruvi
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [XATO] Python topilmadi!
    echo  Python yuklab oling: https://python.org
    pause
    exit /b 1
)

echo  [✓] Python topildi
echo.

:: Virtual muhit yaratish
if not exist "venv" (
    echo  [*] Virtual muhit yaratilmoqda...
    python -m venv venv
    echo  [✓] Virtual muhit yaratildi
) else (
    echo  [✓] Virtual muhit allaqachon mavjud
)

echo.
echo  [*] Kutubxonalar o'rnatilmoqda...
venv\Scripts\pip install -r requirements.txt --quiet

echo.
echo  [✓] Barcha kutubxonalar o'rnatildi!
echo.
echo  ════════════════════════════════════════
echo.
echo  Keyingi qadam:
echo  1. config.py faylini oching
echo  2. BOT_TOKEN o'rniga tokeningizni qo'ying
echo  3. start.bat ni ishga tushiring
echo.
echo  BotFather dan token olish:
echo  t.me/BotFather → /newbot
echo.
pause
