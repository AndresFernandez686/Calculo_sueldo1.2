@echo off
echo ==========================================
echo    Iniciando Calculadora de Sueldos
echo ==========================================
echo.
cd "C:\Users\xblac\OneDrive\Datos adjuntos\calculo.sueldo1.1"
echo Directorio actual: %CD%
echo.
echo Verificando archivos...
if exist main.py (
    echo [OK] main.py encontrado
) else (
    echo [ERROR] main.py no encontrado
    pause
    exit /b 1
)
echo.
echo Verificando Streamlit...
python -c "import streamlit; print('[OK] Streamlit version:', streamlit.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] Streamlit no esta instalado
    echo Instalando Streamlit...
    pip install streamlit
)
echo.
echo ==========================================
echo Ejecutando aplicacion...
echo ==========================================
echo.
echo La aplicacion se abrira en tu navegador
echo Presiona Ctrl+C para detener el servidor
echo.
streamlit run main.py
pause
