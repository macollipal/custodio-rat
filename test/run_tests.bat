@echo off
REM =============================================
REM Custodio RAT — Ejecutar Test Suite
REM =============================================
REM Uso: hacer doble click o ejecutar desde cmd
REM =============================================

cd /d %~dp0backend

echo.
echo ================================
echo Custodio RAT — Test Suite
echo ================================
echo.
echo 1) Todos los tests (completo)
echo 2) Solo tests P0 nuevos
echo 3) Con coverage HTML
echo 4) Solo hash chain
echo.
set /p choice="Seleccionar opcion (1-4): "

if "%choice%"=="1" goto ALL
if "%choice%"=="2" goto P0
if "%choice%"=="3" goto COVERAGE
if "%choice%"=="4" goto HASH
goto END

:ALL
echo.
echo Ejecutando todos los tests...
python -m pytest tests/ -v --tb=short
goto END

:P0
echo.
echo Ejecutando tests P0 (hash chain, ARCO, RBAC)...
python -m pytest tests/test_hash_chain.py tests/test_arco_tickets.py tests/test_rbac_deep.py -v
goto END

:COVERAGE
echo.
echo Ejecutando tests con coverage...
python -m pytest tests/ --cov=app --cov-report=html
echo.
echo Abrir: backend/htmlcov/index.html
goto END

:HASH
echo.
echo Ejecutando solo hash chain...
python -m pytest tests/test_hash_chain.py -v
goto END

:END
echo.
pause