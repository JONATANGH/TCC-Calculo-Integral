@echo off
REM Genera el ejecutable en Windows: dist\ResolutorIntegrales.exe
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --onefile --windowed --name ResolutorIntegrales --collect-submodules sympy --collect-submodules scipy.integrate app.py
echo.
echo Listo: revisa la carpeta dist\ResolutorIntegrales.exe
pause
