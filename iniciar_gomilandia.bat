@echo off
setlocal enabledelayedexpansion
title Gomilandia - Servidor Web
cd /d "%~dp0"

echo ============================================================
echo             INICIANDO TIENDA WEB GOMILANDIA
echo ============================================================
echo   Tienda Publica:      http://127.0.0.1:5000
echo   Panel Administrador: http://127.0.0.1:5000/admin
echo ============================================================
echo.

:: 1. Detectar ejecutable de Python
set "PYTHON_EXE="

:: Probar ruta de instalacion de Python
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

:: Si no se encontro, buscar cualquier otra version en Programs\Python
if not defined PYTHON_EXE (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%D\python.exe" set "PYTHON_EXE=%%D\python.exe"
    )
)

:: Si no se encontro, probar comandos de PATH
if not defined PYTHON_EXE (
    where py >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py"
    ) else (
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=python"
        )
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] No se pudo encontrar Python en tu computadora.
    echo Por favor asegurate de tener Python instalado desde python.org
    echo.
    pause
    exit /b 1
)

:: 2. Verificar dependencias (Flask)
echo [+] Verificando componentes...
"%PYTHON_EXE%" -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Instalando Flask...
    "%PYTHON_EXE%" -m pip install flask
)

:: 3. Abrir navegador e iniciar servidor
echo [+] Abriendo navegador en http://127.0.0.1:5000 ...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000

echo [+] Levantando el servidor de Gomilandia...
echo [!] Para detener el servidor presiona Ctrl + C o cierra esta ventana.
echo.
"%PYTHON_EXE%" app.py

pause

