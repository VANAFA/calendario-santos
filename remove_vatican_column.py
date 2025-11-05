#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar la columna url_vatican del CSV
"""

import csv

def remove_vatican_column():
    input_file = 'santos.csv'
    output_file = 'santos_sin_vatican.csv'
    
    print(f"📚 Leyendo {input_file}...")
    
    santos = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Eliminar url_vatican si existe
            if 'url_vatican' in row:
                del row['url_vatican']
            santos.append(row)
    
    print(f"✅ Leídos {len(santos)} santos")
    print(f"📝 Escribiendo {output_file} sin columna url_vatican...")
    
    # Nuevos campos sin url_vatican
    campos = ['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'oracion']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        
        for santo in santos:
            writer.writerow(santo)
    
    print(f"✅ Archivo creado: {output_file}")
    print(f"\n💡 Para reemplazar el original:")
    print(f"   mv {input_file} {input_file}.backup")
    print(f"   mv {output_file} {input_file}")

if __name__ == '__main__':
    remove_vatican_column()
