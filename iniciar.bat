@echo off
color 0A

title Custodio - Sistema RAT

echo.
echo  ==========================================
echo   CUSTODIO - Iniciando sistema...
echo  ==========================================
echo.

taskkill /F /FI "WINDOWTITLE eq Custodio - Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Custodio - Frontend" >nul 2>&1

echo  [INFO] Procesos anteriores cerrados (si existian)
echo.

echo  [0/3] Verificando configuraciones...
if not exist "backend\venv" (
    echo  [ERROR] No se encontro venv en backend\venv
    echo         Ejecuta: cd backend ^&^& python -m venv venv
    pause
    exit /b 1
)
echo       venv: OK

netstat -ano ^| findstr ":8002" ^| findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [ERROR] Puerto 8002 ya esta en uso
    echo         Deten el proceso o cambia el puerto
    pause
    exit /b 1
)
echo       puerto 8002: disponible

netstat -ano ^| findstr ":3000" ^| findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [ERROR] Puerto 3000 ya esta en uso
    echo         Deten el proceso o cambia el puerto
    pause
    exit /b 1
)
echo       puerto 3000: disponible

echo.
echo  [1/3] Iniciando Backend (FastAPI)...
start "Custodio - Backend" cmd /k "cd /d C:\Users\chelo\Desktop\RAT_opencode\backend && venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"

timeout /t 3 /nobreak >nul

echo  [2/3] Iniciando Frontend (Next.js)...
start "Custodio - Frontend" cmd /k "cd /d C:\Users\chelo\Desktop\RAT_opencode\frontend-next && npm run dev"

timeout /t 5 /nobreak >nul

echo  [3/3] Verificando servicios...
netstat -ano ^| findstr ":8002" ^| findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Backend:  http://localhost:8002/docs - OK
) else (
    echo       Backend:  FALLO (revisar ventana)
)

netstat -ano ^| findstr ":3000" ^| findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Frontend: http://localhost:3000 - OK
) else (
    echo       Frontend: FALLO (revisar ventana)
)

echo.
echo  ==========================================
echo   Sistema iniciado
echo  ==========================================
start http://localhost:3000

cmd /k