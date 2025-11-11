#!/bin/bash
# Script para sincronizar archivos web a la raíz (para GitHub Pages)

echo "🔄 Sincronizando archivos web..."

# Copiar archivos HTML
cp web/index.html .
cp web/cita-biblica.html .

# Crear symlink de images si no existe
if [ ! -L images ]; then
    ln -sf web/images images
fi

echo "✅ Sincronización completada:"
echo "   ✓ index.html → raíz"
echo "   ✓ cita-biblica.html → raíz"
echo "   ✓ images → symlink a web/images"
echo ""
echo "💡 Ahora puedes hacer commit y push para actualizar GitHub Pages"
