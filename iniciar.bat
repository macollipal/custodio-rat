@echo off
color 0A

title Custodio - Sistema RAT

echo.
echo  ==========================================
echo   CUSTODIO - Iniciando sistema...
echo  ==========================================
echo.

echo  [INFO] Matando procesos anteriores...
taskkill /F /FI "WINDOWTITLE eq Custodio - Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Custodio - Frontend*" >nul 2>&1
timeout /t 1 /nobreak >nul

echo.
echo  [0/4] Verificando configuraciones...
if not exist "backend\venv" (
    echo  [ERROR] No se encontro venv en backend\venv
    pause
    exit /b 1
)
echo       venv: OK

netstat -ano | findstr ":8002" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [ERROR] Puerto 8002 ya esta en uso
    echo         Ejecuta: matar_puertos.bat
    pause
    exit /b 1
)
echo       puerto 8002: disponible

netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [ERROR] Puerto 3000 ya esta en uso
    echo         Ejecuta: matar_puertos.bat
    pause
    exit /b 1
)
echo       puerto 3000: disponible

echo.
echo  [1/4] Iniciando Backend (FastAPI)...
cd /d C:\Users\chelo\Desktop\RAT_opencode\backend
start "Custodio - Backend" cmd /c "venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8002"

timeout /t 3 /nobreak >nul

echo  [2/4] Verificando Backend...
netstat -ano | findstr ":8002" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Backend:  http://localhost:8002/docs - OK
) else (
    echo       Backend:  FALLO - verificando...
)

echo.
echo  [3/4] Compilando Frontend (production build)...
cd /d C:\Users\chelo\Desktop\RAT_opencode\frontend-next
call npm run build >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo la compilacion del frontend
    pause
    exit /b 1
)
echo       Build: OK

echo.
echo  [4/4] Iniciando Frontend (standalone production)...
start "Custodio - Frontend" cmd /c "node .next\standalone\server.js"

timeout /t 3 /nobreak >nul

echo.
echo  [FINAL] Verificando servicios...
netstat -ano | findstr ":8002" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Backend:  http://localhost:8002/docs - OK
) else (
    echo       Backend:  FALLO
)

netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Frontend: http://localhost:3000 - OK
) else (
    echo       Frontend: FALLO
)

echo.
echo  ==========================================
echo   Listo - http://localhost:3000
echo  ==========================================
start http://localhost:3000

pause
