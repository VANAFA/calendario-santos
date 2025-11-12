#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper masivo para descargar evangelios de múltiples fechas desde Vatican News
Utiliza la misma fuente confiable (Vatican News) que ya funciona
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import time
import json

class VaticanNewsMassScraper:
    def __init__(self):
        self.rss_url = "https://www.vaticannews.va/es/evangelio-de-hoy.rss.xml"
        self.json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelio_hoy.json')
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelios.csv')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def parse_fecha_rss(self, fecha_str):
        """Parsea fecha del formato RSS: 'Tue, 12 Nov 2024 00:00:00 +0000'"""
        try:
            # Formato: Tue, 12 Nov 2024 00:00:00 +0000
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(fecha_str)
            return dt
        except:
            return None
    
    def obtener_desde_rss(self):
        """Obtiene todos los evangelios disponibles en el RSS"""
        try:
            print("📥 Descargando RSS de Vatican News...")
            response = requests.get(self.rss_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            evangelios = []
            
            for item in items:
                try:
                    # Extraer título y fecha
                    titulo = item.find('title').text if item.find('title') else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                    
                    fecha = self.parse_fecha_rss(pub_date)
                    if not fecha:
                        continue
                    
                    # Extraer descripción (contiene el evangelio)
                    descripcion = item.find('description').text if item.find('description') else ""
                    
                    if not descripcion:
                        continue
                    
                    # Parsear el HTML de la descripción
                    desc_soup = BeautifulSoup(descripcion, 'html.parser')
                    
                    # Extraer textos
                    parrafos = desc_soup.find_all(['p', 'div'])
                    
                    primera_lectura_ref = ""
                    primera_lectura_texto = []
                    salmo_ref = ""
                    salmo_texto = []
                    evangelio_ref = ""
                    evangelio_texto = []
                    
                    seccion_actual = None
                    
                    for p in parrafos:
                        texto = p.get_text(separator=' ', strip=True)
                        if not texto or len(texto) < 10:
                            continue
                        
                        texto_lower = texto.lower()
                        
                        # Detectar secciones
                        if 'primera lectura' in texto_lower or 'lectura del libro' in texto_lower:
                            seccion_actual = 'lectura'
                            if len(texto) < 100:
                                primera_lectura_ref = texto
                                continue
                        elif 'salmo' in texto_lower:
                            seccion_actual = 'salmo'
                            if len(texto) < 100:
                                salmo_ref = texto
                                continue
                        elif 'evangelio' in texto_lower and 'según' in texto_lower:
                            seccion_actual = 'evangelio'
                            if len(texto) < 150:
                                evangelio_ref = texto
                                continue
                        
                        # Agregar texto
                        if len(texto) > 50:
                            if seccion_actual == 'lectura':
                                primera_lectura_texto.append(texto)
                            elif seccion_actual == 'salmo':
                                salmo_texto.append(texto)
                            elif seccion_actual == 'evangelio':
                                evangelio_texto.append(texto)
                    
                    evangelio_data = {
                        'año': fecha.year,
                        'mes': fecha.month,
                        'dia': fecha.day,
                        'titulo': titulo,
                        'primera_lectura_ref': primera_lectura_ref,
                        'primera_lectura_texto': ' '.join(primera_lectura_texto),
                        'salmo_ref': salmo_ref,
                        'salmo_texto': ' '.join(salmo_texto),
                        'evangelio_ref': evangelio_ref,
                        'evangelio_texto': ' '.join(evangelio_texto)
                    }
                    
                    if evangelio_data['evangelio_texto']:
                        evangelios.append(evangelio_data)
                        print(f"  ✅ {fecha.strftime('%d/%m/%Y')} - {len(evangelio_data['evangelio_texto'])} caracteres")
                
                except Exception as e:
                    print(f"  ⚠️  Error procesando item: {e}")
                    continue
            
            print(f"\n✅ Total extraídos del RSS: {len(evangelios)}")
            return evangelios
            
        except Exception as e:
            print(f"❌ Error obteniendo RSS: {e}")
            return []
    
    def obtener_desde_json(self):
        """Obtiene el evangelio del día desde el JSON local"""
        if not os.path.exists(self.json_path):
            return None
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parsear la fecha del título
            # Formato: "Evangelio y palabra del día 12 noviembre 2025"
            titulo = data.get('titulo', '')
            import re
            match = re.search(r'(\d+)\s+(\w+)\s+de\s+(\d+)|(\d+)\s+(\w+)\s+(\d+)', titulo)
            
            if not match:
                return None
            
            meses = {
                'enero': 1, 'february': 2, 'marzo': 3, 'april': 4,
                'mayo': 5, 'june': 6, 'julio': 7, 'august': 8,
                'septiembre': 9, 'october': 10, 'noviembre': 11, 'november': 11, 'december': 12, 'diciembre': 12
            }
            
            if match.group(1):  # "12 noviembre de 2025"
                dia = int(match.group(1))
                mes_nombre = match.group(2).lower()
                año = int(match.group(3))
            else:  # "12 noviembre 2025"
                dia = int(match.group(4))
                mes_nombre = match.group(5).lower()
                año = int(match.group(6))
            
            mes = meses.get(mes_nombre, 1)
            
            evangelio_data = {
                'año': año,
                'mes': mes,
                'dia': dia,
                'titulo': titulo,
                'primera_lectura_ref': data.get('lectura', {}).get('referencia', ''),
                'primera_lectura_texto': data.get('lectura', {}).get('texto', ''),
                'salmo_ref': data.get('salmo', {}).get('referencia', ''),
                'salmo_texto': data.get('salmo', {}).get('texto', ''),
                'evangelio_ref': data.get('evangelio', {}).get('referencia', ''),
                'evangelio_texto': data.get('evangelio', {}).get('texto', '')
            }
            
            if evangelio_data['evangelio_texto']:
                print(f"✅ JSON local: {dia}/{mes}/{año} - {len(evangelio_data['evangelio_texto'])} caracteres")
                return evangelio_data
            
        except Exception as e:
            print(f"⚠️ Error leyendo JSON: {e}")
        
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
        evangelios_ordenados = sorted(
            evangelios_map.values(),
            key=lambda x: (int(x['año']), int(x['mes']), int(x['dia'])),
            reverse=True
        )
        
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
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
    
    def actualizar_todo(self):
        """Actualiza el CSV con todos los evangelios disponibles"""
        print("=" * 70)
        print("📥 ACTUALIZANDO EVANGELIOS DESDE VATICAN NEWS")
        print("=" * 70)
        print()
        
        # Cargar existentes
        evangelios_map = self.cargar_csv_existente()
        nuevos = 0
        actualizados = 0
        
        # Obtener del JSON local (día actual)
        evangelio_json = self.obtener_desde_json()
        if evangelio_json:
            key = f"{evangelio_json['año']}-{evangelio_json['mes']}-{evangelio_json['dia']}"
            if key in evangelios_map:
                # Solo actualizar si el existente está vacío
                if not evangelios_map[key].get('evangelio_texto') or len(evangelios_map[key].get('evangelio_texto', '').strip()) == 0:
                    evangelios_map[key] = evangelio_json
                    actualizados += 1
            else:
                evangelios_map[key] = evangelio_json
                nuevos += 1
        
        # Obtener del RSS (últimos 15 días)
        evangelios_rss = self.obtener_desde_rss()
        for ev in evangelios_rss:
            key = f"{ev['año']}-{ev['mes']}-{ev['dia']}"
            if key in evangelios_map:
                # Solo actualizar si el existente está vacío
                ev_existente = evangelios_map[key]
                if not ev_existente.get('evangelio_texto') or len(ev_existente.get('evangelio_texto', '').strip()) == 0:
                    evangelios_map[key] = ev
                    actualizados += 1
            else:
                evangelios_map[key] = ev
                nuevos += 1
        
        # Guardar
        self.guardar_en_csv(evangelios_map)
        
        print(f"\n📊 RESUMEN:")
        print(f"🆕 Nuevos: {nuevos}")
        print(f"🔄 Actualizados: {actualizados}")
        print(f"📖 Total en CSV: {len(evangelios_map)}")

def main():
    scraper = VaticanNewsMassScraper()
    scraper.actualizar_todo()

if __name__ == '__main__':
    main()
