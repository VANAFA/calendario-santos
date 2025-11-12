#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper para obtener evangelios desde Evangelizo.org
Esta web tiene evangelios de cualquier fecha del año litúrgico
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import time
import re

class EvangelizioScraper:
    def __init__(self):
        # URL base de Evangelizo
        self.base_url = "https://evangelizo.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelios.csv')
    
    def obtener_evangelio_fecha(self, fecha):
        """Obtiene el evangelio de una fecha específica"""
        try:
            # Formato: /ES/gospel/2025-11-12
            fecha_str = fecha.strftime('%Y-%m-%d')
            url = f"{self.base_url}/ES/gospel/{fecha_str}"
            
            print(f"📖 Obteniendo evangelio del {fecha.strftime('%d/%m/%Y')}...")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Inicializar datos
            primera_lectura_ref = ""
            primera_lectura_texto = []
            salmo_ref = ""
            salmo_texto = []
            evangelio_ref = ""
            evangelio_texto = []
            
            # Buscar todas las secciones de lecturas
            # Evangelizo.org usa divs con clases específicas
            
            # Primera lectura
            primera_seccion = soup.find('div', {'id': re.compile('lecture_.*')})
            if primera_seccion:
                # Referencia
                ref_elem = primera_seccion.find('p', class_='bibleref')
                if ref_elem:
                    primera_lectura_ref = ref_elem.get_text(strip=True)
                
                # Texto
                texto_elem = primera_seccion.find('div', class_='text')
                if texto_elem:
                    for p in texto_elem.find_all('p'):
                        texto = p.get_text(separator=' ', strip=True)
                        if texto and len(texto) > 20:
                            primera_lectura_texto.append(texto)
            
            # Salmo
            salmo_seccion = soup.find('div', {'id': re.compile('psaume_.*')})
            if salmo_seccion:
                # Referencia
                ref_elem = salmo_seccion.find('p', class_='bibleref')
                if ref_elem:
                    salmo_ref = ref_elem.get_text(strip=True)
                
                # Texto
                texto_elem = salmo_seccion.find('div', class_='text')
                if texto_elem:
                    for p in texto_elem.find_all('p'):
                        texto = p.get_text(separator=' ', strip=True)
                        if texto and len(texto) > 10:
                            salmo_texto.append(texto)
            
            # Evangelio
            evangelio_seccion = soup.find('div', {'id': re.compile('evangile_.*')})
            if evangelio_seccion:
                # Referencia
                ref_elem = evangelio_seccion.find('p', class_='bibleref')
                if ref_elem:
                    evangelio_ref = ref_elem.get_text(strip=True)
                
                # Texto
                texto_elem = evangelio_seccion.find('div', class_='text')
                if texto_elem:
                    for p in texto_elem.find_all('p'):
                        texto = p.get_text(separator=' ', strip=True)
                        if texto and len(texto) > 20:
                            evangelio_texto.append(texto)
            
            # Construir resultado
            evangelio_data = {
                'año': fecha.year,
                'mes': fecha.month,
                'dia': fecha.day,
                'titulo': f'Evangelio del día {fecha.strftime("%d/%m/%Y")}',
                'primera_lectura_ref': primera_lectura_ref,
                'primera_lectura_texto': ' '.join(primera_lectura_texto),
                'salmo_ref': salmo_ref,
                'salmo_texto': ' '.join(salmo_texto),
                'evangelio_ref': evangelio_ref,
                'evangelio_texto': ' '.join(evangelio_texto)
            }
            
            # Verificar que al menos tengamos el evangelio
            if evangelio_data['evangelio_texto']:
                print(f"  ✅ Evangelio obtenido ({len(evangelio_data['evangelio_texto'])} caracteres)")
                return evangelio_data
            else:
                print(f"  ⚠️  No se pudo extraer el evangelio")
                return None
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  ❌ No disponible (404)")
            else:
                print(f"  ❌ Error HTTP {e.response.status_code}")
            return None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def cargar_csv_existente(self):
        """Carga evangelios existentes del CSV"""
        evangelios_map = {}
        
        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        key = f"{row['año']}-{row['mes']}-{row['dia']}"
                        evangelios_map[key] = row
                print(f"📖 Cargados {len(evangelios_map)} evangelios existentes del CSV")
            except Exception as e:
                print(f"❌ Error leyendo CSV: {e}")
        
        return evangelios_map
    
    def guardar_en_csv(self, evangelios_map):
        """Guarda los evangelios en CSV"""
        # Ordenar por fecha (más reciente primero)
        evangelios_ordenados = sorted(
            evangelios_map.values(),
            key=lambda x: (int(x['año']), int(x['mes']), int(x['dia'])),
            reverse=True
        )
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        # Guardar en CSV
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['año', 'mes', 'dia', 'titulo', 'primera_lectura_ref', 
                         'primera_lectura_texto', 'salmo_ref', 'salmo_texto', 
                         'evangelio_ref', 'evangelio_texto']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for ev in evangelios_ordenados:
                writer.writerow(ev)
        
        print(f"\n✅ CSV actualizado: {self.csv_path}")
        print(f"📊 Total de evangelios: {len(evangelios_ordenados)}")
    
    def descargar_rango_fechas(self, fecha_inicio, fecha_fin, delay=2):
        """Descarga evangelios para un rango de fechas"""
        print("=" * 70)
        print("📥 DESCARGANDO EVANGELIOS DESDE EVANGELIZO.ORG")
        print("=" * 70)
        print(f"Fecha inicio: {fecha_inicio.strftime('%d/%m/%Y')}")
        print(f"Fecha fin: {fecha_fin.strftime('%d/%m/%Y')}")
        print(f"Delay entre requests: {delay} segundos")
        print()
        
        # Cargar evangelios existentes
        evangelios_map = self.cargar_csv_existente()
        
        fecha_actual = fecha_inicio
        nuevos = 0
        actualizados = 0
        errores = 0
        
        while fecha_actual <= fecha_fin:
            key = f"{fecha_actual.year}-{fecha_actual.month}-{fecha_actual.day}"
            
            # Solo descargar si no existe o está vacío
            debe_descargar = False
            if key not in evangelios_map:
                debe_descargar = True
            else:
                ev_existente = evangelios_map[key]
                if not ev_existente.get('evangelio_texto') or len(ev_existente.get('evangelio_texto', '').strip()) == 0:
                    debe_descargar = True
            
            if debe_descargar:
                evangelio_data = self.obtener_evangelio_fecha(fecha_actual)
                
                if evangelio_data:
                    if key in evangelios_map:
                        actualizados += 1
                    else:
                        nuevos += 1
                    evangelios_map[key] = evangelio_data
                else:
                    errores += 1
                
                # Delay para no sobrecargar el servidor
                time.sleep(delay)
            else:
                print(f"⏭️  Saltando {fecha_actual.strftime('%d/%m/%Y')} (ya existe con contenido)")
            
            fecha_actual += timedelta(days=1)
        
        # Guardar en CSV
        self.guardar_en_csv(evangelios_map)
        
        print(f"\n📊 RESUMEN:")
        print(f"🆕 Nuevos: {nuevos}")
        print(f"🔄 Actualizados: {actualizados}")
        print(f"❌ Errores: {errores}")

def main():
    import sys
    
    scraper = EvangelizioScraper()
    
    if len(sys.argv) >= 2:
        # Modo con argumentos
        if sys.argv[1] == '--mes':
            # Descargar un mes completo
            if len(sys.argv) >= 4:
                mes = int(sys.argv[2])
                año = int(sys.argv[3])
                fecha_inicio = datetime(año, mes, 1)
                # Último día del mes
                if mes == 12:
                    fecha_fin = datetime(año, 12, 31)
                else:
                    fecha_fin = datetime(año, mes + 1, 1) - timedelta(days=1)
                
                scraper.descargar_rango_fechas(fecha_inicio, fecha_fin)
            else:
                print("Uso: python3 scraper_evangelios_evangelizo.py --mes MES AÑO")
                print("Ejemplo: python3 scraper_evangelios_evangelizo.py --mes 11 2025")
        
        elif sys.argv[1] == '--rango':
            # Descargar un rango personalizado
            if len(sys.argv) >= 8:
                dia1, mes1, año1 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
                dia2, mes2, año2 = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
                fecha_inicio = datetime(año1, mes1, dia1)
                fecha_fin = datetime(año2, mes2, dia2)
                
                scraper.descargar_rango_fechas(fecha_inicio, fecha_fin)
            else:
                print("Uso: python3 scraper_evangelios_evangelizo.py --rango DIA1 MES1 AÑO1 DIA2 MES2 AÑO2")
                print("Ejemplo: python3 scraper_evangelios_evangelizo.py --rango 1 11 2025 30 11 2025")
        
        elif sys.argv[1] == '--año':
            # Descargar un año completo
            if len(sys.argv) >= 3:
                año = int(sys.argv[2])
                fecha_inicio = datetime(año, 1, 1)
                fecha_fin = datetime(año, 12, 31)
                
                scraper.descargar_rango_fechas(fecha_inicio, fecha_fin, delay=1.5)
            else:
                print("Uso: python3 scraper_evangelios_evangelizo.py --año AÑO")
                print("Ejemplo: python3 scraper_evangelios_evangelizo.py --año 2025")
        
        elif sys.argv[1] == '--dia':
            # Descargar un día específico
            if len(sys.argv) >= 5:
                dia, mes, año = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
                fecha = datetime(año, mes, dia)
                
                evangelios_map = scraper.cargar_csv_existente()
                evangelio_data = scraper.obtener_evangelio_fecha(fecha)
                
                if evangelio_data:
                    key = f"{año}-{mes}-{dia}"
                    evangelios_map[key] = evangelio_data
                    scraper.guardar_en_csv(evangelios_map)
                else:
                    print("❌ No se pudo obtener el evangelio")
            else:
                print("Uso: python3 scraper_evangelios_evangelizo.py --dia DIA MES AÑO")
                print("Ejemplo: python3 scraper_evangelios_evangelizo.py --dia 12 11 2025")
    else:
        # Modo interactivo
        print("\n" + "=" * 70)
        print("📖 SCRAPER DE EVANGELIOS - EVANGELIZO.ORG")
        print("=" * 70)
        print("\nOpciones:")
        print("1. Descargar mes completo")
        print("2. Descargar año completo")
        print("3. Descargar rango de fechas")
        print("4. Descargar día específico")
        print("5. Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            mes = int(input("Mes (1-12): "))
            año = int(input("Año: "))
            fecha_inicio = datetime(año, mes, 1)
            if mes == 12:
                fecha_fin = datetime(año, 12, 31)
            else:
                fecha_fin = datetime(año, mes + 1, 1) - timedelta(days=1)
            
            scraper.descargar_rango_fechas(fecha_inicio, fecha_fin)
        
        elif opcion == '2':
            año = int(input("Año: "))
            fecha_inicio = datetime(año, 1, 1)
            fecha_fin = datetime(año, 12, 31)
            
            print("\n⚠️  ATENCIÓN: Esto descargará 365 evangelios y puede tomar ~15 minutos")
            confirmar = input("¿Continuar? (s/n): ").strip().lower()
            
            if confirmar == 's':
                scraper.descargar_rango_fechas(fecha_inicio, fecha_fin, delay=1.5)
        
        elif opcion == '3':
            print("\nFecha inicio:")
            dia1 = int(input("  Día: "))
            mes1 = int(input("  Mes: "))
            año1 = int(input("  Año: "))
            
            print("\nFecha fin:")
            dia2 = int(input("  Día: "))
            mes2 = int(input("  Mes: "))
            año2 = int(input("  Año: "))
            
            fecha_inicio = datetime(año1, mes1, dia1)
            fecha_fin = datetime(año2, mes2, dia2)
            
            scraper.descargar_rango_fechas(fecha_inicio, fecha_fin)
        
        elif opcion == '4':
            dia = int(input("Día: "))
            mes = int(input("Mes: "))
            año = int(input("Año: "))
            fecha = datetime(año, mes, dia)
            
            evangelios_map = scraper.cargar_csv_existente()
            evangelio_data = scraper.obtener_evangelio_fecha(fecha)
            
            if evangelio_data:
                key = f"{año}-{mes}-{dia}"
                evangelios_map[key] = evangelio_data
                scraper.guardar_en_csv(evangelios_map)
        
        elif opcion == '5':
            print("\n👋 ¡Hasta luego!")
        else:
            print("\n❌ Opción inválida")

if __name__ == '__main__':
    main()
