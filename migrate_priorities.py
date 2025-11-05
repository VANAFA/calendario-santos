#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración para agregar columna 'prioridad' al CSV existente
"""

import csv
import os

def calcular_prioridad(nombre, descripcion=""):
    """
    Calcula la prioridad de un santo basándose en:
    1. Fiestas litúrgicas mayores: 100
    2. Santos argentinos: 85-95
    3. Santos con 'argentina' en descripción: 75
    4. Santos populares (San/Santa): 50
    5. Beatos: 40
    6. Venerables: 35
    7. Resto: 25
    """
    nombre_lower = nombre.lower()
    
    # Diccionario de fiestas mayores (prioridad 100)
    fiestas_mayores = {
        'todos los santos': 100,
        'semana santa': 100,
        'pascua': 100,
        'navidad': 100,
        'inmaculada concepción': 100,
        'epifanía': 100,
        'ascensión': 100,
        'pentecostés': 100,
        'corpus christi': 100,
        'sagrado corazón': 100,
        'asunción': 100,
        'natividad de maría': 100,
        'san josé': 100,
        'san pedro y san pablo': 100,
    }
    
    # Santos argentinos con sus prioridades específicas
    santos_argentinos = {
        'nuestra señora de luján': 95,
        'ceferino namuncurá': 90,
        'san martín de tours': 90,
        'san cayetano': 85,
        'mama antula': 85,
        'héctor valdivielso sáez': 85,
        'josé gabriel brochero': 90,
    }
    
    # Verificar fiestas mayores
    for fiesta, prioridad in fiestas_mayores.items():
        if fiesta in nombre_lower:
            return prioridad
    
    # Verificar santos argentinos
    for santo, prioridad in santos_argentinos.items():
        if santo in nombre_lower:
            return prioridad
    
    # Verificar si menciona Argentina en la descripción
    if descripcion and 'argentina' in descripcion.lower():
        return 75
    
    # Verificar prefijos comunes
    if nombre_lower.startswith('san ') or nombre_lower.startswith('santa ') or nombre_lower.startswith('santo '):
        return 50
    elif nombre_lower.startswith('beato ') or nombre_lower.startswith('beata '):
        return 40
    elif nombre_lower.startswith('venerable '):
        return 35
    
    # Prioridad por defecto
    return 25


def migrar_csv(archivo_entrada='santos.csv', archivo_salida='santos_migrado.csv'):
    """Migra el CSV agregando la columna 'prioridad'"""
    
    if not os.path.exists(archivo_entrada):
        print(f"❌ Error: No se encontró el archivo {archivo_entrada}")
        return False
    
    print(f"📚 Leyendo {archivo_entrada}...")
    
    # Leer todos los datos
    santos = []
    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        campos_originales = reader.fieldnames
        
        for row in reader:
            # Calcular prioridad
            prioridad = calcular_prioridad(row['nombre'], row.get('descripcion', ''))
            
            # Agregar prioridad al diccionario
            row['prioridad'] = prioridad
            santos.append(row)
    
    print(f"✅ Leídos {len(santos)} santos")
    print(f"📝 Escribiendo {archivo_salida}...")
    
    # Escribir con la nueva columna
    nuevos_campos = ['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'url_vatican', 'oracion']
    
    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=nuevos_campos)
        writer.writeheader()
        
        for santo in santos:
            writer.writerow(santo)
    
    print(f"✅ Migración completada!")
    print(f"📊 Estadísticas de prioridades:")
    
    # Contar por prioridad
    prioridades = {}
    for santo in santos:
        p = santo['prioridad']
        prioridades[p] = prioridades.get(p, 0) + 1
    
    for prioridad in sorted(prioridades.keys(), reverse=True):
        count = prioridades[prioridad]
        print(f"   Prioridad {prioridad}: {count} santos")
    
    print(f"\n💡 Pasos siguientes:")
    print(f"   1. Revisa {archivo_salida} para verificar los datos")
    print(f"   2. Si todo está bien, renombra:")
    print(f"      mv {archivo_entrada} {archivo_entrada}.backup")
    print(f"      mv {archivo_salida} {archivo_entrada}")
    
    return True


if __name__ == '__main__':
    migrar_csv()
