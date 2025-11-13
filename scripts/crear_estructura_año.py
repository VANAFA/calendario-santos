#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear estructura de evangelios de un año completo
Crea placeholders (espacios vacíos) para todos los días del año
que luego serán llenados automáticamente por el scraper diario
"""

import csv
import os
from datetime import datetime, timedelta

def crear_placeholders_año(año):
    """Crea placeholders para todos los días de un año"""
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'evangelios.csv')
    
    print("=" * 70)
    print(f"📅 CREANDO ESTRUCTURA PARA EL AÑO {año}")
    print("=" * 70)
    
    # Cargar existentes
    evangelios_map = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['año']}-{row['mes']}-{row['dia']}"
                evangelios_map[key] = row
        print(f"📖 Evangelios existentes en CSV: {len(evangelios_map)}")
    
    # Crear placeholders para todo el año
    fecha = datetime(año, 1, 1)
    fecha_fin = datetime(año, 12, 31)
    nuevos = 0
    existentes = 0
    
    while fecha <= fecha_fin:
        key = f"{fecha.year}-{fecha.month}-{fecha.day}"
        
        if key not in evangelios_map:
            evangelios_map[key] = {
                'año': str(fecha.year),
                'mes': str(fecha.month),
                'dia': str(fecha.day),
                'titulo': f'Evangelio del {fecha.strftime("%d/%m/%Y")}',
                'primera_lectura_ref': '',
                'primera_lectura_texto': '',
                'salmo_ref': '',
                'salmo_texto': '',
                'evangelio_ref': '',
                'evangelio_texto': ''
            }
            nuevos += 1
        else:
            existentes += 1
        
        fecha += timedelta(days=1)
    
    # Guardar ordenado por fecha (más reciente primero)
    evangelios_ordenados = sorted(
        evangelios_map.values(),
        key=lambda x: (int(x['año']), int(x['mes']), int(x['dia'])),
        reverse=True
    )
    
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['año', 'mes', 'dia', 'titulo', 'primera_lectura_ref', 
                     'primera_lectura_texto', 'salmo_ref', 'salmo_texto', 
                     'evangelio_ref', 'evangelio_texto']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ev in evangelios_ordenados:
            writer.writerow(ev)
    
    # Contar cuántos tienen contenido
    con_contenido = sum(1 for ev in evangelios_map.values() 
                       if ev.get('evangelio_texto') and len(ev['evangelio_texto']) > 100)
    vacios = len(evangelios_map) - con_contenido
    
    print(f"\n✅ CSV actualizado: {csv_path}")
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  🆕 Nuevos placeholders: {nuevos}")
    print(f"  ✓  Ya existían: {existentes}")
    print(f"  📖 Total días en CSV: {len(evangelios_map)}")
    print(f"  ✅ Con contenido: {con_contenido}")
    print(f"  📭 Vacíos (sin contenido): {vacios}")
    print(f"\n💡 Próximos pasos:")
    print(f"  1. Ejecuta diariamente: python3 scripts/scraper_evangelios_masivo.py")
    print(f"  2. Los espacios vacíos se llenarán automáticamente")
    print(f"  3. En unos meses tendrás el año completo!")
    print("=" * 70)

def main():
    import sys
    
    if len(sys.argv) >= 2:
        año = int(sys.argv[1])
    else:
        print("\n📅 CREADOR DE ESTRUCTURA DE EVANGELIOS")
        print("-" * 70)
        año = int(input("¿Para qué año quieres crear la estructura? (ej: 2025): "))
    
    crear_placeholders_año(año)

if __name__ == '__main__':
    main()
