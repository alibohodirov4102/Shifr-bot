@echo off
title Shifr Bot - Ishlamoqda
color 0A
echo.
echo  ╔══════════════════════════════════════╗
echo  ║         SHIFR BOT ISHLAMOQDA         ║
echo  ║    To'xtatish uchun: Ctrl+C          ║
echo  ╚══════════════════════════════════════╝
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python bot.py
) else (
    echo  [XATO] Avval install.bat ni ishga tushiring!
    pause
)
