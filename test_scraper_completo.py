#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo del scraper con un día
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scraper_santos import SantosCalendarioScraper

def test_scraper_completo():
    scraper = SantosCalendarioScraper()
    
    print("🧪 TEST: Scraper completo con día de ejemplo\n")
    print("=" * 70)
    print("📅 Probando con 4 de octubre (San Francisco de Asís)")
    print("=" * 70 + "\n")
    
    # Procesar un día específico
    datos = scraper.procesar_dia(mes=10, dia=4)
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS:")
    print("=" * 70)
    
    if datos:
        for santo in datos:
            print(f"\n✅ Santo: {santo['nombre']}")
            print(f"   Prioridad: {santo['prioridad']}")
            print(f"   Descripción: {santo['descripcion'][:100] if santo['descripcion'] else 'N/A'}...")
            print(f"   Imagen: {'✓' if santo['imagen'] else '✗'} {santo['imagen']}")
            print(f"   Wikipedia: {'✓' if santo['url_wikipedia'] else '✗'}")
            print(f"   Oración: {'✓' if santo['oracion'] else '✗'}")
    else:
        print("\n⚠️ No se encontraron santos nuevos (pueden ya existir en CSV)")
    
    print("\n" + "=" * 70)
    print("✅ Test completado")

if __name__ == "__main__":
    test_scraper_completo()
