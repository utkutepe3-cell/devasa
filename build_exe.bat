@echo off
title PayTrace Checker - EXE Derleme
echo.
echo  ===================================
echo   PayTrace Checker EXE Derleme
echo  ===================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo  [HATA] Python bulunamadi!
    echo  Python'u https://python.org adresinden indirin.
    pause
    exit /b 1
)

echo  [1/3] PyInstaller kontrol ediliyor...
pip install pyinstaller requests urllib3 --quiet

echo  [2/3] EXE derleniyor...
pyinstaller --onefile --name PayTrace_Checker --clean paytrace_checker.py

if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Derleme basarisiz!
    pause
    exit /b 1
)

echo.
echo  [3/3] Derleme tamamlandi!
echo.
echo  Dosya: dist\PayTrace_Checker.exe
echo.
echo  Kullanim:
echo    PayTrace_Checker.exe --test
echo    PayTrace_Checker.exe -u USER -p PASS
echo    PayTrace_Checker.exe -f combo.txt
echo    PayTrace_Checker.exe
echo.
pause
