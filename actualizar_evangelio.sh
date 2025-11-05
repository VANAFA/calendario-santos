#!/bin/bash
# Script para actualizar el evangelio del día

cd "$(dirname "$0")"
source venv/bin/activate
python3 scraper_evangelio.py

echo "✅ Evangelio actualizado exitosamente"
