#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper para obtener evangelios de cualquier fecha desde USCCB
United States Conference of Catholic Bishops tiene lecturas de todos los días
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import time

class USCCBEvangelioScraper:
    def __init__(self):
        # URL base de USCCB para lecturas en español
        self.base_url = "https://bible.usccb.org/es/bible/lecturas"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelios.csv')
    
    def obtener_evangelio_fecha(self, fecha):
        """Obtiene el evangelio de una fecha específica"""
        try:
            # Formato de URL: /es/bible/lecturas/110125.cfm (MMDDYY)
            fecha_str = fecha.strftime('%m%d%y')
            url = f"{self.base_url}/{fecha_str}.cfm"
            
            print(f"📖 Obteniendo evangelio del {fecha.strftime('%d/%m/%Y')}...")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el contenedor de las lecturas
            content = soup.find('div', class_='content-body')
            if not content:
                content = soup.find('div', {'id': 'content-body'})
            
            if not content:
                print(f"  ❌ No se encontró contenido para {fecha.strftime('%d/%m/%Y')}")
                return None
            
            # Extraer secciones
            primera_lectura_ref = ""
            primera_lectura_texto = []
            salmo_ref = ""
            salmo_texto = []
            evangelio_ref = ""
            evangelio_texto = []
            
            seccion_actual = None
            
            # Buscar todos los encabezados y contenido
            for elemento in content.find_all(['h3', 'h4', 'p', 'div']):
                texto = elemento.get_text(separator=' ', strip=True)
                
                if not texto or len(texto) < 3:
                    continue
                
                texto_lower = texto.lower()
                
                # Detectar secciones por encabezados
                if elemento.name in ['h3', 'h4']:
                    if 'primera lectura' in texto_lower or 'lectura i' in texto_lower:
                        seccion_actual = 'lectura'
                        continue
                    elif 'salmo' in texto_lower:
                        seccion_actual = 'salmo'
                        continue
                    elif 'evangelio' in texto_lower or 'aleluya' in texto_lower:
                        seccion_actual = 'evangelio'
                        continue
                
                # Detectar referencias (texto corto con números)
                if len(texto) < 100 and any(char.isdigit() for char in texto):
                    if seccion_actual == 'lectura' and not primera_lectura_ref:
                        primera_lectura_ref = texto
                        continue
                    elif seccion_actual == 'salmo' and not salmo_ref:
                        salmo_ref = texto
                        continue
                    elif seccion_actual == 'evangelio' and not evangelio_ref and 'aleluya' not in texto_lower:
                        evangelio_ref = texto
                        continue
                
                # Agregar texto a la sección actual
                if len(texto) > 50:
                    if seccion_actual == 'lectura':
                        primera_lectura_texto.append(texto)
                    elif seccion_actual == 'salmo':
                        salmo_texto.append(texto)
                    elif seccion_actual == 'evangelio' and 'aleluya' not in texto_lower:
                        evangelio_texto.append(texto)
            
            # Construir resultado
            evangelio_data = {
                'año': fecha.year,
                'mes': fecha.month,
                'dia': fecha.day,
                'titulo': f'Evangelio del día {fecha.strftime("%d de %B de %Y")}',
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
                print(f"  ❌ No disponible (404) - puede ser domingo/festividad especial")
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
        print("📥 DESCARGANDO EVANGELIOS DESDE USCCB")
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
    
    scraper = USCCBEvangelioScraper()
    
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
                print("Uso: python3 scraper_evangelios_usccb.py --mes MES AÑO")
                print("Ejemplo: python3 scraper_evangelios_usccb.py --mes 11 2025")
        
        elif sys.argv[1] == '--rango':
            # Descargar un rango personalizado
            if len(sys.argv) >= 8:
                dia1, mes1, año1 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
                dia2, mes2, año2 = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
                fecha_inicio = datetime(año1, mes1, dia1)
                fecha_fin = datetime(año2, mes2, dia2)
                
                scraper.descargar_rango_fechas(fecha_inicio, fecha_fin)
            else:
                print("Uso: python3 scraper_evangelios_usccb.py --rango DIA1 MES1 AÑO1 DIA2 MES2 AÑO2")
                print("Ejemplo: python3 scraper_evangelios_usccb.py --rango 1 11 2025 30 11 2025")
        
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
                print("Uso: python3 scraper_evangelios_usccb.py --dia DIA MES AÑO")
                print("Ejemplo: python3 scraper_evangelios_usccb.py --dia 12 11 2025")
    else:
        # Modo interactivo
        print("\n" + "=" * 70)
        print("📖 SCRAPER DE EVANGELIOS - USCCB")
        print("=" * 70)
        print("\nOpciones:")
        print("1. Descargar mes completo")
        print("2. Descargar rango de fechas")
        print("3. Descargar día específico")
        print("4. Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
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
        
        elif opcion == '3':
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
        
        elif opcion == '4':
            print("\n👋 ¡Hasta luego!")
        else:
            print("\n❌ Opción inválida")

if __name__ == '__main__':
    main()
