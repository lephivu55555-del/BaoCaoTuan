@echo off
title He Thong Bao Cao Tu Dong
color 0B

echo ===================================================
echo   KHOI DONG HE THONG BAO CAO TU DONG - TO KY THUAT
echo ===================================================
echo.

echo [1/2] Dang kiem tra thu vien Python...
pip install -r requirements.txt >nul 2>&1

echo [2/2] Dang khoi dong Server...
echo.
echo ===================================================
echo 🌐 TRUY CAP WEB TAI: http://localhost:5000
echo Ctrl+C de tat he thong
echo ===================================================
echo.

set PYTHONPATH=%cd%
python app/main.py

pause
