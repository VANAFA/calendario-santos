#!/bin/bash
# Script para actualizar el evangelio del día
# NOTA: Este script está obsoleto. Usa mejor: python3 main.py --evangelio

cd "$(dirname "$0")"
source venv/bin/activate
python3 main.py --evangelio

echo "✅ Evangelio actualizado exitosamente"
echo "💡 Tip: Puedes usar directamente: python3 main.py --evangelio"
