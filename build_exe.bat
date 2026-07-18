@echo off
REM PayTrace Refund Tool - EXE Build Script (Windows)
REM Bu dosyayi Windows'ta calistirin

echo PayTrace Refund Tool - EXE olusturuluyor...
echo.

REM PyInstaller yoksa kur
pip install pyinstaller requests >nul 2>&1

REM EXE olustur (tek dosya, konsol uygulamasi)
pyinstaller --onefile --console --name PayTrace_Refund --icon=NONE paytrace_refund.py

echo.
echo ============================================
echo  EXE dosyasi olusturuldu:
echo  dist\PayTrace_Refund.exe
echo ============================================
echo.
echo Kullanim:
echo   PayTrace_Refund.exe -u USER -p PASS -i INTEGRATOR_ID --list-sales
echo.
pause
