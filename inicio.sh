#!/bin/bash
# Script de inicio rápido para el Calendario de Santos

echo "🗓️  CALENDARIO DE SANTOS - Inicio Rápido"
echo "========================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ No se encontró el entorno virtual"
    echo "Ejecuta primero: python3 -m venv venv"
    exit 1
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Verificar dependencias
if ! python3 -c "import bs4" 2>/dev/null; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
fi

# Ejecutar main.py
echo ""
python3 main.py "$@"
