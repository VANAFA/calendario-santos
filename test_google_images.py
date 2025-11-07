#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de búsqueda de imágenes en Google
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_santos import SantosCalendarioScraper

def test_busqueda_google():
    scraper = SantosCalendarioScraper()
    
    # Probar con algunos santos
    santos_prueba = [
        "San Francisco de Asís",
        "Santa Teresa de Ávila",
        "San José",
        "Nuestra Señora de Luján",
        "Beato Ceferino Namuncurá"
    ]
    
    print("🧪 TEST: Búsqueda de imágenes en Google\n")
    print("=" * 60)
    
    for santo in santos_prueba:
        print(f"\n🔍 Buscando: {santo}")
        url_imagen = scraper.buscar_imagen_google(santo)
        
        if url_imagen:
            print(f"✅ Imagen encontrada")
            print(f"   URL: {url_imagen[:100]}...")
        else:
            print(f"❌ No se encontró imagen")
    
    print("\n" + "=" * 60)
    print("✅ Test completado")

if __name__ == "__main__":
    test_busqueda_google()
