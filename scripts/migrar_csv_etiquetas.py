#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para migrar santos.csv agregando la columna 'etiquetas'
================================================================
Este script lee el CSV existente, agrega la columna 'etiquetas' vacía
y reescribe el archivo con el nuevo formato.
"""

import csv
import os
import sys

def migrar_csv():
    """Migra el CSV existente agregando la columna etiquetas"""
    # Rutas relativas al directorio raíz del proyecto
    directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    archivo_csv = os.path.join(directorio_base, "data", "santos.csv")
    archivo_backup = os.path.join(directorio_base, "backups", "santos_backup.csv")
    
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: No se encontró {archivo_csv}")
        return False
    
    # Crear backup
    print(f"📋 Creando backup en {archivo_backup}...")
    import shutil
    shutil.copy2(archivo_csv, archivo_backup)
    print(f"✅ Backup creado")
    
    # Leer datos existentes
    print(f"📖 Leyendo {archivo_csv}...")
    santos = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        campos_originales = reader.fieldnames
        print(f"  Campos originales: {campos_originales}")
        
        for row in reader:
            # Agregar campo etiquetas vacío si no existe
            if 'etiquetas' not in row:
                row['etiquetas'] = ''
            santos.append(row)
    
    print(f"✅ Leídos {len(santos)} santos")
    
    # Escribir con nuevo formato
    print(f"📝 Reescribiendo {archivo_csv} con columna 'etiquetas'...")
    campos_nuevos = ['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'etiquetas', 'oracion']
    
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos_nuevos, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(santos)
    
    print(f"✅ Migración completada!")
    print(f"  Campos nuevos: {campos_nuevos}")
    print(f"  Total santos: {len(santos)}")
    print(f"\n💡 Ahora puedes ejecutar el scraper para llenar las etiquetas")
    
    return True

if __name__ == "__main__":
    try:
        exito = migrar_csv()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
