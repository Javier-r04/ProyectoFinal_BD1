#!/usr/bin/env bash
# =================================================
# Script de inicio rapido para Linux/Mac
# Proyecto Final - Base de Datos I
# =================================================

set -e

echo
echo "=== Levantando PostgreSQL en Docker ==="
docker compose up -d

echo
echo "=== Esperando a que PostgreSQL este listo ==="
sleep 5

echo
echo "=== Instalando dependencias del backend ==="
cd backend
[ -f .env ] || cp .env.example .env
pip install -r requirements.txt

echo
echo "=== Iniciando servidor Flask ==="
echo "Abre tu navegador en http://localhost:5000"
echo "Presiona CTRL+C para detener"
python3 app.py
