@echo off
title Custodio - Matar puertos 8002 y 3000
color 0C

echo.
echo  ==========================================
echo   Mateniendo procesos en puertos 8002 y 3000
echo  ==========================================
echo.

echo  [INFO] Matando procesos node y python colgados...
taskkill /F /FI "IMAGENAME eq node.exe" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python3.exe" >nul 2>&1
echo       Procesos node/python liberados

echo.
echo  [INFO] Matando puertos 8002 y 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002" ^| findstr "LISTENING"') do (
    echo       PID %%a en puerto 8002 - matando...
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% equ 0 (
        echo       Puerto 8002: OK
    ) else (
        echo       Puerto 8002: no se pudo matar (puede que ya este libre)
    )
)

echo.
echo  [INFO] Buscando PID del puerto 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo       PID %%a en puerto 3000 - matando...
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% equ 0 (
        echo       Puerto 3000: OK
    ) else (
        echo       Puerto 3000: no se pudo matar (puede que ya este libre)
    )
)

echo.
echo  ==========================================
echo   Procesos muertos
echo  ==========================================
echo.
timeout /t 2 /nobreak >nul