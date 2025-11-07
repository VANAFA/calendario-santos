#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de búsqueda en Wikipedia con nombre completo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_santos import SantosCalendarioScraper

def test_busqueda_wikipedia():
    scraper = SantosCalendarioScraper()
    
    # Probar con diferentes tipos de nombres
    santos_prueba = [
        "San Francisco de Asís",
        "Santa Teresa de Ávila",
        "San José",
        "Beato Ceferino Namuncurá",
        "Nuestra Señora de Luján",
        "San Martín de Tours",
        "Santa Rosa de Lima"
    ]
    
    print("🧪 TEST: Búsqueda en Wikipedia con nombre completo\n")
    print("=" * 70)
    
    for santo in santos_prueba:
        print(f"\n🔍 Buscando: {santo}")
        info = scraper.buscar_en_wikipedia(santo)
        
        if info:
            print(f"✅ Encontrado: {info['titulo_pagina']}")
            print(f"   URL: {info['url_wikipedia']}")
            print(f"   Descripción: {info['descripcion'][:100]}...")
            if info.get('url_imagen'):
                print(f"   Imagen: ✓")
        else:
            print(f"❌ No se encontró Wikipedia")
    
    print("\n" + "=" * 70)
    print("✅ Test completado")

if __name__ == "__main__":
    test_busqueda_wikipedia()
