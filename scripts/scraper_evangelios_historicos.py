#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper para obtener evangelios históricos de Vatican News
Guarda los datos en un CSV con formato: año,mes,dia,titulo,primera_lectura_ref,primera_lectura_texto,salmo_ref,salmo_texto,evangelio_ref,evangelio_texto
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import time
import json

class EvangelioHistoricoScraper:
    def __init__(self):
        self.base_url = "https://www.vaticannews.va/es/evangelio-de-hoy.rss.xml"
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelios.csv')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def parse_rss_feed(self, xml_content):
        """Parsea el RSS de Vatican News y extrae los evangelios"""
        soup = BeautifulSoup(xml_content, 'xml')
        items = soup.find_all('item')
        
        evangelios = []
        for item in items:
            try:
                # Extraer fecha del pubDate
                pub_date = item.find('pubDate').text if item.find('pubDate') else None
                if pub_date:
                    # Formato: Wed, 12 Nov 2025 00:00:00 +0100
                    # Remover el timezone para parsearlo más fácilmente
                    pub_date_clean = ' '.join(pub_date.split()[:5])  # Toma solo: Wed, 12 Nov 2025 00:00:00
                    fecha = datetime.strptime(pub_date_clean, '%a, %d %b %Y %H:%M:%S')
                else:
                    continue
                
                titulo = item.find('title').text if item.find('title') else ''
                descripcion = item.find('description').text if item.find('description') else ''
                
                # Parsear el contenido HTML de la descripción
                desc_soup = BeautifulSoup(descripcion, 'html.parser')
                
                # Extraer secciones
                primera_lectura_ref = ''
                primera_lectura_texto = ''
                salmo_ref = ''
                salmo_texto = ''
                evangelio_ref = ''
                evangelio_texto = ''
                
                # Buscar todas las secciones strong (encabezados)
                sections = desc_soup.find_all('strong')
                
                current_section = None
                for elem in desc_soup.descendants:
                    if elem.name == 'strong':
                        text = elem.get_text().strip().lower()
                        if 'primera lectura' in text or 'lectura del libro' in text:
                            current_section = 'lectura'
                        elif 'salmo' in text:
                            current_section = 'salmo'
                        elif 'evangelio' in text or 'lectura del santo evangelio' in text:
                            current_section = 'evangelio'
                    
                    elif elem.name == 'em' and current_section:
                        # Las referencias están en <em>
                        ref_text = elem.get_text().strip()
                        if current_section == 'lectura' and not primera_lectura_ref:
                            primera_lectura_ref = ref_text
                        elif current_section == 'salmo' and not salmo_ref:
                            salmo_ref = ref_text
                        elif current_section == 'evangelio' and not evangelio_ref:
                            evangelio_ref = ref_text
                    
                    elif elem.name == 'p' and current_section:
                        # El texto está en párrafos
                        texto = elem.get_text().strip()
                        if texto and not texto.startswith('Palabra') and not texto.startswith('Lectura'):
                            if current_section == 'lectura':
                                primera_lectura_texto += texto + '\n'
                            elif current_section == 'salmo':
                                salmo_texto += texto + '\n'
                            elif current_section == 'evangelio':
                                evangelio_texto += texto + '\n'
                
                evangelio_data = {
                    'fecha': fecha,
                    'año': fecha.year,
                    'mes': fecha.month,
                    'dia': fecha.day,
                    'titulo': titulo.strip(),
                    'primera_lectura_ref': primera_lectura_ref.strip(),
                    'primera_lectura_texto': primera_lectura_texto.strip(),
                    'salmo_ref': salmo_ref.strip(),
                    'salmo_texto': salmo_texto.strip(),
                    'evangelio_ref': evangelio_ref.strip(),
                    'evangelio_texto': evangelio_texto.strip()
                }
                
                evangelios.append(evangelio_data)
                print(f"✅ Obtenido evangelio del {fecha.strftime('%d/%m/%Y')}")
                
            except Exception as e:
                print(f"❌ Error parseando item: {e}")
                continue
        
        return evangelios
    
    def obtener_evangelio_desde_json(self):
        """Obtiene el evangelio del día desde el evangelio_hoy.json ya existente"""
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelio_hoy.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data.get('exito'):
                return []
            
            # Parsear la fecha
            fecha_str = data.get('fecha', '')
            # Formato: "12 de November de 2025"
            import locale
            try:
                # Intentar parsear diferentes formatos
                partes = fecha_str.split(' de ')
                if len(partes) == 3:
                    dia = int(partes[0].strip())
                    mes_nombre = partes[1].strip()
                    año = int(partes[2].strip())
                    
                    # Convertir nombre de mes a número
                    meses = {
                        'january': 1, 'february': 2, 'march': 3, 'april': 4,
                        'may': 5, 'june': 6, 'july': 7, 'august': 8,
                        'september': 9, 'october': 10, 'november': 11, 'december': 12,
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                    }
                    mes = meses.get(mes_nombre.lower(), 1)
                    fecha = datetime(año, mes, dia)
                else:
                    fecha = datetime.now()
            except:
                fecha = datetime.now()
            
            evangelio = {
                'fecha': fecha,
                'año': fecha.year,
                'mes': fecha.month,
                'dia': fecha.day,
                'titulo': data.get('titulo', ''),
                'primera_lectura_ref': data.get('lectura', {}).get('referencia', ''),
                'primera_lectura_texto': data.get('lectura', {}).get('texto', ''),
                'salmo_ref': data.get('salmo', {}).get('referencia', '') if data.get('salmo') else '',
                'salmo_texto': data.get('salmo', {}).get('texto', '') if data.get('salmo') else '',
                'evangelio_ref': data.get('evangelio', {}).get('referencia', ''),
                'evangelio_texto': data.get('evangelio', {}).get('texto', '')
            }
            
            print(f"✅ Obtenido evangelio del {fecha.strftime('%d/%m/%Y')} desde JSON")
            return [evangelio]
            
        except Exception as e:
            print(f"❌ Error leyendo JSON: {e}")
            return []
    
    def obtener_evangelio_fecha(self, fecha):
        """Obtiene el evangelio de una fecha específica"""
        # Por ahora solo obtenemos desde el JSON existente
        return self.obtener_evangelio_desde_json()
    
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
    
    def guardar_en_csv(self, evangelios):
        """Guarda los evangelios en CSV, evitando duplicados"""
        # Cargar evangelios existentes
        evangelios_map = self.cargar_csv_existente()
        
        # Agregar nuevos evangelios (o actualizar existentes)
        nuevos = 0
        actualizados = 0
        for ev in evangelios:
            key = f"{ev['año']}-{ev['mes']}-{ev['dia']}"
            if key not in evangelios_map:
                evangelios_map[key] = ev
                nuevos += 1
            else:
                # Actualizar si el nuevo tiene más contenido
                ev_existente = evangelios_map[key]
                # Actualizar si el existente está vacío y el nuevo tiene contenido
                if ev['evangelio_texto'] and (not ev_existente.get('evangelio_texto') or len(ev_existente.get('evangelio_texto', '').strip()) == 0):
                    evangelios_map[key] = ev
                    actualizados += 1
                    print(f"  🔄 Actualizado evangelio del {ev['dia']}/{ev['mes']}/{ev['año']}")
        
        # Ordenar por fecha (más reciente primero)
        evangelios_ordenados = sorted(
            evangelios_map.values(),
            key=lambda x: (int(x['año']), int(x['mes']), int(x['dia'])),
            reverse=True
        )
        
        # Guardar en CSV
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['año', 'mes', 'dia', 'titulo', 'primera_lectura_ref', 
                         'primera_lectura_texto', 'salmo_ref', 'salmo_texto', 
                         'evangelio_ref', 'evangelio_texto']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for ev in evangelios_ordenados:
                writer.writerow({
                    'año': ev['año'],
                    'mes': ev['mes'],
                    'dia': ev['dia'],
                    'titulo': ev['titulo'],
                    'primera_lectura_ref': ev['primera_lectura_ref'],
                    'primera_lectura_texto': ev['primera_lectura_texto'],
                    'salmo_ref': ev['salmo_ref'],
                    'salmo_texto': ev['salmo_texto'],
                    'evangelio_ref': ev['evangelio_ref'],
                    'evangelio_texto': ev['evangelio_texto']
                })
        
        print(f"\n✅ CSV actualizado: {self.csv_path}")
        print(f"📊 Total de evangelios: {len(evangelios_ordenados)}")
        print(f"🆕 Nuevos evangelios agregados: {nuevos}")
        print(f"🔄 Evangelios actualizados: {actualizados}")
    
    def scrape_rango_fechas(self, fecha_inicio, fecha_fin):
        """Intenta obtener evangelios para un rango de fechas"""
        print(f"🔍 Intentando obtener evangelios de {fecha_inicio} a {fecha_fin}")
        print("ℹ️  NOTA: Vatican News RSS solo tiene evangelios recientes.")
        print("   Para fechas históricas, se necesitaría otra fuente.\n")
        
        # Por ahora solo obtenemos el RSS actual
        evangelios = self.obtener_evangelio_fecha(datetime.now())
        
        if evangelios:
            self.guardar_en_csv(evangelios)
        else:
            print("❌ No se pudieron obtener evangelios")

def main():
    scraper = EvangelioHistoricoScraper()
    
    print("=" * 60)
    print("🔍 SCRAPER DE EVANGELIOS HISTÓRICOS")
    print("=" * 60)
    print()
    
    # Primero intentar obtener del JSON (evangelio completo del día)
    print("📥 Obteniendo evangelio del día desde JSON...")
    evangelios_json = scraper.obtener_evangelio_desde_json()
    
    # Luego obtener del RSS (múltiples días pero a veces sin contenido completo)
    print("\n📥 Obteniendo evangelios del RSS de Vatican News...")
    evangelios_rss = []
    try:
        response = requests.get(scraper.base_url, headers=scraper.headers, timeout=10)
        response.raise_for_status()
        evangelios_rss = scraper.parse_rss_feed(response.text)
    except Exception as e:
        print(f"⚠️  No se pudo obtener RSS: {e}")
    
    # Combinar ambas fuentes
    todos_evangelios = evangelios_json + evangelios_rss
    
    if todos_evangelios:
        scraper.guardar_en_csv(todos_evangelios)
    else:
        print("\n⚠️  No se pudieron obtener evangelios.")
        print("ℹ️  Vatican News RSS solo tiene evangelios muy recientes.")
        print("   Para un archivo histórico completo, se necesitaría:")
        print("   1. Otra fuente de datos (ej: Evangelio Diario, EWTN)")
        print("   2. Ir agregando manualmente día a día")
        print("   3. Usar una API de liturgia católica")

if __name__ == '__main__':
    main()
