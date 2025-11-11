#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Script - Calendario de Santos
===================================
Script principal que ejecuta todos los scrapers necesarios para cargar los datos.

Uso:
    python3 main.py                    # Ejecuta todo (evangelio + santos)
    python3 main.py --evangelio        # Solo actualiza evangelio
    python3 main.py --santos           # Solo actualiza santos
    python3 main.py --santos-dia 11 11 # Solo actualiza un día específico
"""

import sys
import os
from datetime import datetime

# Agregar directorio scripts al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*70)
    print("🗓️  CALENDARIO DE SANTOS - SISTEMA DE ACTUALIZACIÓN")
    print("="*70)
    print("\nOpciones disponibles:")
    print("  1. Actualizar Evangelio del día")
    print("  2. Actualizar Santos (todo el año)")
    print("  3. Actualizar Santos (un día específico)")
    print("  4. Actualizar todo (evangelio + santos)")
    print("  5. Salir")
    print("="*70)

def actualizar_evangelio():
    """Actualiza el evangelio del día"""
    print("\n📖 ACTUALIZANDO EVANGELIO DEL DÍA...")
    print("-" * 70)
    
    try:
        from scraper_evangelio import EvangelioScraper
        
        scraper = EvangelioScraper()
        datos = scraper.obtener_evangelio_del_dia()
        
        if datos.get('exito'):
            scraper.guardar_json(datos)
            print("\n✅ Evangelio actualizado correctamente")
            print(f"📅 Fecha: {datos.get('fecha', 'N/A')}")
            return True
        else:
            print("\n❌ No se pudo obtener el evangelio")
            print(f"Error: {datos.get('error', 'Desconocido')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error al actualizar evangelio: {e}")
        import traceback
        traceback.print_exc()
        return False

def actualizar_santos_completo():
    """Actualiza todos los santos del año"""
    print("\n✝️  ACTUALIZANDO SANTOS (AÑO COMPLETO)...")
    print("-" * 70)
    print("⚠️  ADVERTENCIA: Este proceso puede tomar varias horas")
    
    respuesta = input("¿Deseas continuar? (s/N): ").strip().lower()
    if respuesta != 's':
        print("❌ Operación cancelada")
        return False
    
    try:
        from scraper_santos_wikipedia import SantosWikipediaScraper
        
        scraper = SantosWikipediaScraper(descargar_imagenes=True)
        scraper.ejecutar(mes_inicio=1, dia_inicio=1, mes_fin=12, dia_fin=31)
        
        print("\n✅ Santos actualizados correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al actualizar santos: {e}")
        import traceback
        traceback.print_exc()
        return False

def actualizar_santos_dia(mes=None, dia=None):
    """Actualiza santos de un día específico"""
    if mes is None or dia is None:
        print("\n✝️  ACTUALIZAR SANTOS DE UN DÍA ESPECÍFICO")
        print("-" * 70)
        
        try:
            mes = int(input("Mes (1-12): "))
            dia = int(input("Día (1-31): "))
        except ValueError:
            print("❌ Error: Debes ingresar números válidos")
            return False
    
    if not (1 <= mes <= 12 and 1 <= dia <= 31):
        print("❌ Error: Mes debe estar entre 1-12 y día entre 1-31")
        return False
    
    print(f"\n✝️  ACTUALIZANDO SANTOS DEL {dia:02d}/{mes:02d}...")
    print("-" * 70)
    
    try:
        from scraper_santos_wikipedia import SantosWikipediaScraper
        
        scraper = SantosWikipediaScraper(descargar_imagenes=True)
        scraper.ejecutar(mes_inicio=mes, dia_inicio=dia, mes_fin=mes, dia_fin=dia)
        
        print(f"\n✅ Santos del {dia:02d}/{mes:02d} actualizados correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al actualizar santos: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--evangelio':
            return actualizar_evangelio()
        
        elif arg == '--santos':
            return actualizar_santos_completo()
        
        elif arg == '--santos-dia':
            if len(sys.argv) < 4:
                print("❌ Uso: python3 main.py --santos-dia MES DIA")
                return False
            try:
                mes = int(sys.argv[2])
                dia = int(sys.argv[3])
                return actualizar_santos_dia(mes, dia)
            except ValueError:
                print("❌ Error: MES y DIA deben ser números")
                return False
        
        elif arg in ['--help', '-h']:
            print(__doc__)
            return True
        
        else:
            print(f"❌ Argumento desconocido: {arg}")
            print("Usa --help para ver las opciones disponibles")
            return False
    
    # Modo interactivo
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                actualizar_evangelio()
                input("\nPresiona Enter para continuar...")
            
            elif opcion == '2':
                actualizar_santos_completo()
                input("\nPresiona Enter para continuar...")
            
            elif opcion == '3':
                actualizar_santos_dia()
                input("\nPresiona Enter para continuar...")
            
            elif opcion == '4':
                print("\n🔄 ACTUALIZACIÓN COMPLETA")
                print("-" * 70)
                actualizar_evangelio()
                print("\n")
                actualizar_santos_completo()
                input("\nPresiona Enter para continuar...")
            
            elif opcion == '5':
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("\n❌ Opción inválida. Por favor selecciona 1-5")
                input("Presiona Enter para continuar...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Operación interrumpida. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
