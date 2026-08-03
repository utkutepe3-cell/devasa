@echo off
echo ========================================
echo  PayTrace Checker - EXE Olusturucu
echo ========================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Once Python kur: https://python.org
    pause
    exit /b 1
)

echo [1/3] Gerekli paketler yukleniyor...
pip install requests pyinstaller --quiet

echo [2/3] EXE derleniyor...
pyinstaller --onefile --name paytrace_checker --console paytrace_checker.py

echo [3/3] Temizlik...
rmdir /s /q build 2>nul
del paytrace_checker.spec 2>nul

echo.
echo ========================================
echo  TAMAM! EXE dosyasi: dist\paytrace_checker.exe
echo ========================================
echo.
echo Kullanim:
echo   dist\paytrace_checker.exe -f combo.txt -t 10
echo.
pause
