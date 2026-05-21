@echo off
REM ===============================================
REM Script de inicio rapido para Windows
REM Proyecto Final - Base de Datos I
REM ===============================================

echo.
echo === Levantando PostgreSQL en Docker ===
docker compose up -d
if errorlevel 1 (
    echo ERROR: Docker no esta corriendo. Inicia Docker Desktop primero.
    pause
    exit /b 1
)

echo.
echo === Esperando a que PostgreSQL este listo ===
timeout /t 5 /nobreak >nul

echo.
echo === Instalando dependencias del backend ===
cd backend
if not exist .env copy .env.example .env
pip install -r requirements.txt

echo.
echo === Iniciando servidor Flask ===
echo Abre tu navegador en http://localhost:5000
echo Presiona CTRL+C para detener
python app.py
