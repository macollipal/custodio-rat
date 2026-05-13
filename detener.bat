@echo off
title Custodio - Deteniendo sistema...
color 0C

echo.
echo  ==========================================
echo   CUSTODIO - Deteniendo sistema...
echo  ==========================================
echo.

echo  [1/2] Deteniendo Backend...
taskkill /F /FI "WINDOWTITLE eq Custodio - Backend" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Backend detenido
) else (
    echo       Backend no estaba en ejecucion
)

echo  [2/2] Deteniendo Frontend...
taskkill /F /FI "WINDOWTITLE eq Custodio - Frontend" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Frontend detenido
) else (
    echo       Frontend no estaba en ejecucion
)

echo.
echo  ==========================================
echo   Sistema detenido correctamente
echo  ==========================================
echo.

timeout /t 2 /nobreak >nul