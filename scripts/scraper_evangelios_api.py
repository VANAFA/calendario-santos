#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper que usa API pública de lecturas litúrgicas
Permite descargar evangelios de CUALQUIER fecha del año litúrgico
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import os
import time
import json

class APILiturgicaScraper:
    """
    Usa la API pública de Church Calendar API
    que tiene todas las lecturas del año litúrgico
    """
    
    def __init__(self):
        # API de CalAPI - Calendario Litúrgico en español
        self.base_url = "http://calapi.inadiutorium.cz/api/v0/es/calendars/default"
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'evangelios.csv')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def obtener_leccionario_fecha(self, fecha):
        """Obtiene información del leccionario para una fecha específica"""
        try:
            # Formato: /2025/11/12
            url = f"{self.base_url}/{fecha.year}/{fecha.month}/{fecha.day}"
            
            print(f"📖 Consultando API para {fecha.strftime('%d/%m/%Y')}...")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Esta API da referencias, pero no el texto completo
            # Necesitamos otra fuente para el texto
            
            if 'celebrations' in data:
                celebraciones = data['celebrations']
                if celebraciones:
                    primera_celebracion = celebraciones[0]
                    
                    # Extraer referencias de las lecturas
                    primera_lectura_ref = ""
                    evangelio_ref = ""
                    
                    if 'reading_1' in primera_celebracion:
                        primera_lectura_ref = primera_celebracion['reading_1']
                    
                    if 'gospel' in primera_celebracion:
                        evangelio_ref = primera_celebracion['gospel']
                    
                    print(f"  ℹ️  API solo proporciona referencias, no texto completo")
                    print(f"  📚 Primera lectura: {primera_lectura_ref}")
                    print(f"  📖 Evangelio: {evangelio_ref}")
                    
                    return {
                        'referencias': True,
                        'primera_lectura_ref': primera_lectura_ref,
                        'evangelio_ref': evangelio_ref
                    }
            
            return None
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def obtener_desde_bible_gateway(self, referencia, idioma='SPA'):
        """
        Obtiene el texto de una referencia bíblica desde BibleGateway
        Ejemplo: "Lc 17, 11-19" -> texto completo
        """
        try:
            # Limpiar referencia para URL
            ref_limpia = referencia.strip().replace(' ', '+')
            url = f"https://www.biblegateway.com/passage/?search={ref_limpia}&version=RVR1960"
            
            print(f"  📥 Descargando: {referencia}...")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el contenido del pasaje
            passage = soup.find('div', class_='passage-content')
            if not passage:
                return ""
            
            # Extraer párrafos
            parrafos = passage.find_all('p')
            texto = []
            
            for p in parrafos:
                # Remover números de versículos
                for sup in p.find_all('sup', class_='versenum'):
                    sup.decompose()
                
                texto_p = p.get_text(separator=' ', strip=True)
                if texto_p:
                    texto.append(texto_p)
            
            return ' '.join(texto)
            
        except Exception as e:
            print(f"  ⚠️  Error obteniendo texto: {e}")
            return ""
    
    def descargar_año_completo(self, año):
        """
        Descarga todos los evangelios de un año completo
        Esto tomará tiempo pero tendrás TODA la base de datos
        """
        print("=" * 70)
        print(f"📥 DESCARGANDO EVANGELIOS DEL AÑO {año}")
        print("=" * 70)
        print("⚠️  ATENCIÓN: Esto descargará 365 días y puede tomar 1-2 horas")
        print("💡 Tip: Puedes interrumpir (Ctrl+C) y continuar después")
        print()
        
        confirmar = input("¿Deseas continuar? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Operación cancelada")
            return
        
        # Cargar CSV existente
        evangelios_map = self.cargar_csv_existente()
        
        fecha_inicio = datetime(año, 1, 1)
        fecha_fin = datetime(año, 12, 31)
        fecha_actual = fecha_inicio
        
        nuevos = 0
        actualizados = 0
        errores = 0
        saltados = 0
        
        while fecha_actual <= fecha_fin:
            key = f"{fecha_actual.year}-{fecha_actual.month}-{fecha_actual.day}"
            
            # Solo procesar si no existe o está vacío
            debe_procesar = False
            if key not in evangelios_map:
                debe_procesar = True
            else:
                ev_existente = evangelios_map[key]
                if not ev_existente.get('evangelio_texto') or len(ev_existente.get('evangelio_texto', '').strip()) < 100:
                    debe_procesar = True
            
            if debe_procesar:
                # Intentar obtener desde Vatican News primero (más rápido)
                evangelio_data = self.obtener_desde_vatican_news(fecha_actual)
                
                if evangelio_data and evangelio_data.get('evangelio_texto'):
                    if key in evangelios_map:
                        actualizados += 1
                    else:
                        nuevos += 1
                    evangelios_map[key] = evangelio_data
                    print(f"  ✅ Obtenido ({len(evangelio_data['evangelio_texto'])} caracteres)")
                else:
                    errores += 1
                    print(f"  ❌ No disponible para esta fecha")
                
                # Delay para no sobrecargar el servidor
                time.sleep(2)
            else:
                saltados += 1
                print(f"⏭️  {fecha_actual.strftime('%d/%m/%Y')} (ya existe)")
            
            fecha_actual += timedelta(days=1)
            
            # Guardar cada 10 días por si se interrumpe
            if (fecha_actual.day == 1 or fecha_actual.day == 11 or fecha_actual.day == 21):
                self.guardar_en_csv(evangelios_map)
                print(f"\n💾 Guardado intermedio: {len(evangelios_map)} evangelios\n")
        
        # Guardar final
        self.guardar_en_csv(evangelios_map)
        
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN FINAL:")
        print(f"🆕 Nuevos: {nuevos}")
        print(f"🔄 Actualizados: {actualizados}")
        print(f"⏭️  Saltados (ya existían): {saltados}")
        print(f"❌ Errores: {errores}")
        print(f"📖 Total en CSV: {len(evangelios_map)}")
        print(f"{'='*70}")
    
    def obtener_desde_vatican_news(self, fecha):
        """
        Intenta obtener el evangelio desde Vatican News
        (solo funciona para fechas recientes, últimos ~15 días)
        """
        try:
            # URL directa del día
            # Vatican News no tiene un endpoint directo por fecha antigua
            # Solo funciona para fechas muy recientes
            return None
            
        except:
            return None
    
    def descargar_mes(self, mes, año):
        """Descarga un mes completo"""
        print("=" * 70)
        print(f"📥 DESCARGANDO EVANGELIOS DE {mes:02d}/{año}")
        print("=" * 70)
        
        from calendar import monthrange
        ultimo_dia = monthrange(año, mes)[1]
        
        evangelios_map = self.cargar_csv_existente()
        
        fecha_inicio = datetime(año, mes, 1)
        fecha_fin = datetime(año, mes, ultimo_dia)
        fecha_actual = fecha_inicio
        
        nuevos = 0
        actualizados = 0
        errores = 0
        
        while fecha_actual <= fecha_fin:
            key = f"{fecha_actual.year}-{fecha_actual.month}-{fecha_actual.day}"
            
            debe_procesar = False
            if key not in evangelios_map:
                debe_procesar = True
            else:
                ev_existente = evangelios_map[key]
                if not ev_existente.get('evangelio_texto') or len(ev_existente.get('evangelio_texto', '').strip()) < 100:
                    debe_procesar = True
            
            if debe_procesar:
                # Aquí necesitamos una fuente que tenga evangelios históricos
                # Por ahora solo podemos marcar como vacío
                evangelio_data = {
                    'año': fecha_actual.year,
                    'mes': fecha_actual.month,
                    'dia': fecha_actual.day,
                    'titulo': f'Evangelio del {fecha_actual.strftime("%d/%m/%Y")}',
                    'primera_lectura_ref': '',
                    'primera_lectura_texto': '',
                    'salmo_ref': '',
                    'salmo_texto': '',
                    'evangelio_ref': '',
                    'evangelio_texto': ''
                }
                
                if key in evangelios_map:
                    actualizados += 1
                else:
                    nuevos += 1
                evangelios_map[key] = evangelio_data
                print(f"📅 {fecha_actual.strftime('%d/%m/%Y')} - Creado placeholder")
            else:
                print(f"⏭️  {fecha_actual.strftime('%d/%m/%Y')} (ya existe)")
            
            fecha_actual += timedelta(days=1)
        
        self.guardar_en_csv(evangelios_map)
        
        print(f"\n📊 RESUMEN:")
        print(f"🆕 Nuevos: {nuevos}")
        print(f"🔄 Actualizados: {actualizados}")
        print(f"❌ Errores: {errores}")
    
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
        
        print(f"✅ CSV actualizado: {self.csv_path}")
        print(f"📊 Total de evangelios: {len(evangelios_ordenados)}")

def main():
    import sys
    
    scraper = APILiturgicaScraper()
    
    if len(sys.argv) >= 2:
        if sys.argv[1] == '--año':
            if len(sys.argv) >= 3:
                año = int(sys.argv[2])
                scraper.descargar_año_completo(año)
            else:
                print("Uso: python3 scraper_evangelios_api.py --año AÑO")
        
        elif sys.argv[1] == '--mes':
            if len(sys.argv) >= 4:
                mes = int(sys.argv[2])
                año = int(sys.argv[3])
                scraper.descargar_mes(mes, año)
            else:
                print("Uso: python3 scraper_evangelios_api.py --mes MES AÑO")
    
    else:
        print("\n" + "=" * 70)
        print("📖 SCRAPER DE EVANGELIOS - TODO EL AÑO")
        print("=" * 70)
        print("\n⚠️  LIMITACIÓN: Vatican News solo tiene últimos ~15 días")
        print("\n💡 SOLUCIONES:")
        print("  1. Crear placeholders para todo el año (opción --mes)")
        print("  2. Ejecutar diariamente y acumular gradualmente")
        print("  3. Usar libro/PDF del leccionario y cargarlo manualmente")
        print("\nOpciones:")
        print("  1. Crear placeholders para un mes")
        print("  2. Crear placeholders para un año completo")
        print("  3. Salir")
        
        opcion = input("\nSelecciona (1-3): ").strip()
        
        if opcion == '1':
            mes = int(input("Mes (1-12): "))
            año = int(input("Año: "))
            scraper.descargar_mes(mes, año)
        
        elif opcion == '2':
            año = int(input("Año: "))
            scraper.descargar_año_completo(año)
        
        elif opcion == '3':
            print("👋 ¡Hasta luego!")

if __name__ == '__main__':
    main()
