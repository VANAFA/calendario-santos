#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recalcular datos de santos existentes:
- Prioridades (arreglar beatos marcados como festividad)
- Imágenes desde Google
- URLs de Wikipedia con nombre completo
"""

import csv
import os
from scraper_santos import SantosCalendarioScraper
import time

def recalcular_todos_los_datos():
    """Recalcula prioridades, imágenes y Wikipedia para todos los santos en el CSV"""
    
    scraper = SantosCalendarioScraper()
    
    print("=" * 70)
    print("🔄 RECALCULANDO DATOS DE TODOS LOS SANTOS")
    print("=" * 70)
    print()
    
    # Leer CSV existente
    santos = []
    with open('santos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        santos = list(reader)
    
    print(f"📊 Total de santos a procesar: {len(santos)}")
    print()
    
    # Crear backup
    backup_file = f'santos_backup_{int(time.time())}.csv'
    print(f"💾 Creando backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'oracion'])
        writer.writeheader()
        writer.writerows(santos)
    print()
    
    # Procesar cada santo
    santos_actualizados = []
    contador = 0
    
    for santo in santos:
        contador += 1
        nombre = santo['nombre']
        mes = int(santo['mes'])
        dia = int(santo['dia'])
        
        print(f"[{contador}/{len(santos)}] 🔄 {nombre}")
        
        # 1. Recalcular prioridad
        prioridad_nueva = scraper._calcular_prioridad(nombre, santo.get('descripcion', ''))
        if prioridad_nueva != int(santo.get('prioridad', 0)):
            print(f"  ✏️  Prioridad: {santo.get('prioridad')} → {prioridad_nueva}")
            santo['prioridad'] = prioridad_nueva
        
        # 2. Buscar nueva imagen en Google
        nombre_archivo = scraper.limpiar_nombre_archivo(nombre)
        url_imagen_google = scraper.buscar_imagen_google(nombre)
        if url_imagen_google:
            imagen_descargada = scraper.descargar_imagen(url_imagen_google, nombre_archivo)
            if imagen_descargada:
                print(f"  🖼️  Nueva imagen: {imagen_descargada}")
                santo['imagen'] = imagen_descargada
        
        # 3. Buscar Wikipedia con nombre completo
        info_wiki = scraper.buscar_en_wikipedia(nombre)
        if info_wiki:
            url_nueva = info_wiki['url_wikipedia']
            if url_nueva != santo.get('url_wikipedia', ''):
                print(f"  📖 Wikipedia actualizada")
                santo['url_wikipedia'] = url_nueva
                
                # Actualizar descripción si está vacía o muy corta
                if not santo.get('descripcion') or len(santo.get('descripcion', '')) < 50:
                    santo['descripcion'] = info_wiki['descripcion']
                    print(f"  📝 Descripción actualizada")
                
                # Actualizar oración si no existe
                if not santo.get('oracion'):
                    oracion = scraper.extraer_oracion(info_wiki['titulo_pagina'])
                    if oracion:
                        santo['oracion'] = oracion
                        print(f"  🙏 Oración agregada")
        
        santos_actualizados.append(santo)
        
        # Pausa para no saturar los servicios
        time.sleep(0.5)
        print()
    
    # Guardar CSV actualizado
    print("=" * 70)
    print("💾 Guardando datos actualizados...")
    
    with open('santos.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'oracion'])
        writer.writeheader()
        writer.writerows(santos_actualizados)
    
    print("=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print(f"✅ Santos procesados: {len(santos_actualizados)}")
    print(f"✅ Backup guardado en: {backup_file}")
    print(f"✅ CSV actualizado: santos.csv")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⚠️  ADVERTENCIA: Este proceso puede tomar varias horas")
    print("⚠️  Se descargaran nuevas imágenes para todos los santos")
    print("⚠️  Se recalcularán todas las prioridades")
    print("⚠️  Se actualizarán las URLs de Wikipedia\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
    if respuesta == 's':
        recalcular_todos_los_datos()
    else:
        print("\n❌ Proceso cancelado")
