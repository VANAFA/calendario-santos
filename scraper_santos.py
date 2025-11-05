#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper del Calendario de Santos
=================================
Este script extrae información de todos los santos del año desde
calendariodesantos.com y Wikipedia, generando un archivo CSV completo
con imágenes descargadas localmente.

Autor: Sistema automatizado
Fecha: Noviembre 2025
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import time
from datetime import datetime
import sys

class SantosCalendarioScraper:
    def __init__(self):
        self.directorio_imagenes = "images"
        self.archivo_csv = "santos.csv"
        self.pagina_cache = None
        self.santos_extraidos = {}
        self.santos_existentes = set()  # Cache de santos ya procesados
        
        # Headers para simular un navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Session reutilizable para requests (más rápido)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Crear directorio de imágenes si no existe
        if not os.path.exists(self.directorio_imagenes):
            os.makedirs(self.directorio_imagenes)
        
        # Cargar santos existentes del CSV
        self._cargar_santos_existentes()
    
    def _cargar_santos_existentes(self):
        """Carga la lista de santos ya procesados desde el CSV existente"""
        if os.path.exists(self.archivo_csv):
            try:
                with open(self.archivo_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Crear una clave única: mes-dia-nombre
                        clave = f"{row['mes']}-{row['dia']}-{row['nombre']}"
                        self.santos_existentes.add(clave)
                print(f"📋 Cargados {len(self.santos_existentes)} santos existentes del CSV\n")
            except Exception as e:
                print(f"⚠️ No se pudo cargar CSV existente: {e}\n")
    
    def _santo_ya_procesado(self, mes, dia, nombre):
        """Verifica si un santo ya fue procesado"""
        clave = f"{mes}-{dia}-{nombre}"
        return clave in self.santos_existentes
    
    def limpiar_nombre_archivo(self, nombre):
        """Convierte el nombre del santo en un nombre de archivo válido"""
        # Remover prefijos como "San", "Santa", "Santo", "Beato", etc.
        nombre = re.sub(r'^(San|Santa|Santo|Beato|Beata|Bienaventurada?|Nuestra Señora|Madre)\s+', '', nombre, flags=re.IGNORECASE)
        
        # Convertir a minúsculas y reemplazar espacios y caracteres especiales
        nombre = nombre.lower()
        nombre = re.sub(r'[áàäâ]', 'a', nombre)
        nombre = re.sub(r'[éèëê]', 'e', nombre)
        nombre = re.sub(r'[íìïî]', 'i', nombre)
        nombre = re.sub(r'[óòöô]', 'o', nombre)
        nombre = re.sub(r'[úùüû]', 'u', nombre)
        nombre = re.sub(r'[ñ]', 'n', nombre)
        nombre = re.sub(r'[^a-z0-9]', '_', nombre)
        nombre = re.sub(r'_+', '_', nombre)
        nombre = nombre.strip('_')
        
        return nombre[:50]  # Limitar longitud
    
    def obtener_santos_del_dia(self, mes, dia):
        """Obtiene los santos del día desde calendariodesantos.com"""
        # Convertir número de mes a nombre en español
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        mes_nombre = meses[mes - 1]
        
        # URL del día específico
        url = f"https://calendariodesantos.com/santoral/{mes_nombre}/{dia}/"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            santos = []
            
            # Buscar todos los enlaces que apunten a subpáginas de santos
            # Formato: /santoral/enero/31/san-juan-bosco
            enlaces = soup.find_all('a', href=True)
            
            for enlace in enlaces:
                href = enlace['href']
                # Verificar si es un enlace a un santo específico
                if f'/santoral/{mes_nombre}/{dia}/' in href and href.count('/') >= 5:
                    # Extraer el nombre del santo desde el texto del enlace
                    nombre = enlace.get_text(strip=True)
                    if nombre and len(nombre) > 2:
                        santos.append({
                            'nombre': nombre,
                            'url': href if href.startswith('http') else 'https://calendariodesantos.com' + href
                        })
            
            return santos
            
        except Exception as e:
            print(f"  ⚠️ Error obteniendo santos del {dia:02d}/{mes:02d}: {e}")
            return []

    def obtener_santos_del_mes(self, mes):
        """Obtiene todos los santos listados en la página mensual /santoral/<mes>.

        Retorna una lista de diccionarios con claves: 'mes', 'dia', 'nombre', 'url'
        """
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        mes_nombre = meses[mes - 1]
        url = f"https://calendariodesantos.com/santoral/{mes_nombre}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            santos = []

            # Cada ítem de día parece estar en un <li class="py-6"> según el HTML de ejemplo
            items_dia = soup.find_all('li', class_=lambda c: c and 'py-6' in c)

            for item in items_dia:
                # Intentar extraer el número del día desde un encabezado dentro del item
                dia_header = None
                header = item.find(['h2', 'h3', 'h4'])
                if header:
                    texto = header.get_text(separator=' ', strip=True)
                    m = re.search(r"\b(\d{1,2})\b", texto)
                    if m:
                        dia_header = int(m.group(1))

                # Procesar cada enlace dentro del item
                enlaces = item.find_all('a', href=True)
                for enlace in enlaces:
                    href = enlace['href']
                    
                    # Filtrar solo enlaces que sean de santos específicos del mes
                    # (tienen formato /santoral/<mes>/<dia>/<nombre-santo>)
                    if not f'/{mes_nombre}/' in href:
                        continue
                    
                    # Verificar que tenga al menos 5 partes separadas por /
                    # (ej: /santoral/noviembre/03/san-martin-de-porres)
                    if href.count('/') < 4:
                        continue
                    
                    # Normalizar URL absoluta
                    url_abs = href if href.startswith('http') else 'https://calendariodesantos.com' + href

                    # Intentar extraer el día del href (acepta con o sin cero: /1/ o /01/)
                    dia = dia_header  # Usar el día del header como fallback
                    m2 = re.search(rf"/{mes_nombre}/(\d{{1,2}})/", href)
                    if m2:
                        dia = int(m2.group(1))  # int() normaliza '01' -> 1

                    nombre = enlace.get_text(strip=True)
                    # Filtrar enlaces que no sean de santos (ej. navegación, "Ver todos los santos")
                    if nombre and len(nombre) > 2 and dia is not None:
                        # Omitir enlaces genéricos como "Ver todos los santos del X de Mes"
                        if nombre.lower().startswith('ver todos'):
                            continue
                        if 'ver todos los santos' in nombre.lower():
                            continue
                        
                        santos.append({
                            'mes': mes,
                            'dia': dia,
                            'nombre': nombre,
                            'url': url_abs
                        })

            return santos

        except Exception as e:
            print(f"  ⚠️ Error obteniendo santos del mes {mes_nombre}: {e}")
            return []
    
    def extraer_info_de_pagina_santo(self, url_santo):
        """Extrae la descripción de la página individual del santo en calendariodesantos.com"""
        try:
            response = self.session.get(url_santo, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la descripción del santo
            # Probar diferentes selectores comunes
            descripcion = ""
            
            # Intentar encontrar el contenido principal
            selectores = [
                'article p', '.content p', '.entry-content p',
                'main p', '.post-content p', 'div.texto p'
            ]
            
            for selector in selectores:
                parrafos = soup.select(selector)
                if parrafos:
                    # Tomar los primeros párrafos
                    textos = []
                    for p in parrafos[:3]:  # Primeros 3 párrafos
                        texto = p.get_text(strip=True)
                        if len(texto) > 30:  # Filtrar párrafos muy cortos
                            textos.append(texto)
                    
                    if textos:
                        descripcion = ' '.join(textos)[:400]  # Limitar a 400 caracteres
                        break
            
            return descripcion
            
        except Exception as e:
            return ""

    def procesar_santo_info(self, mes, dia, nombre_santo, url_santo):
        """Procesa un solo santo dado su nombre y URL (viene del índice mensual o diario).

        Retorna un diccionario con el mismo formato que usa generar_csv.
        """
        # Verificar si ya fue procesado
        if self._santo_ya_procesado(mes, dia, nombre_santo):
            print(f"  ⏭️  Saltando (ya existe): {nombre_santo}")
            return None
        
        print(f"  🔍 Procesando: {nombre_santo} ({dia:02d}/{mes:02d})")

        # Obtener descripción desde calendariodesantos.com (si existe la subpágina)
        descripcion_calendario = self.extraer_info_de_pagina_santo(url_santo) if url_santo else ""

        # Buscar en Wikipedia para complementar info
        info_wiki = self.buscar_en_wikipedia(nombre_santo)

        # Usar descripción de calendario si existe, sino usar Wikipedia
        descripcion = descripcion_calendario if descripcion_calendario else (info_wiki['descripcion'] if info_wiki else '')

        # Extraer oración
        oracion = ""
        if info_wiki:
            oracion = self.extraer_oracion(info_wiki['titulo_pagina'])

        # Descargar imagen
        nombre_archivo_imagen = self.limpiar_nombre_archivo(nombre_santo)
        imagen_descargada = ""
        if info_wiki and info_wiki.get('url_imagen'):
            imagen_descargada = self.descargar_imagen(info_wiki['url_imagen'], nombre_archivo_imagen)

        # URL Wikipedia
        url_wikipedia = info_wiki['url_wikipedia'] if info_wiki else ""

        # URL Vatican News (mantener el esquema previo)
        url_vatican = f"https://www.vaticannews.va/es/santos/{mes:02d}/{dia:02d}.html"

        resultado = {
            'mes': mes,
            'dia': dia,
            'nombre': nombre_santo,
            'descripcion': descripcion,
            'imagen': imagen_descargada,
            'url_wikipedia': url_wikipedia,
            'url_vatican': url_vatican,
            'oracion': oracion
        }

        print(f"  ✅ Completado: {nombre_santo}")
        # Pausa ligera reducida para mayor velocidad
        time.sleep(0.5)
        return resultado
    
    def buscar_en_wikipedia(self, nombre_santo):
        """Busca información del santo en Wikipedia en español"""
        # Limpiar el nombre para la búsqueda
        nombre_busqueda = re.sub(r'^(San|Santa|Santo|Beato|Beata|Bienaventurada?)\s+', '', nombre_santo, flags=re.IGNORECASE)
        
        # API de Wikipedia en español
        url_api = "https://es.wikipedia.org/w/api.php"
        
        parametros_busqueda = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': nombre_busqueda + ' santo',
            'srlimit': 1
        }
        
        try:
            response = self.session.get(url_api, params=parametros_busqueda, timeout=8)
            response.raise_for_status()
            resultados = response.json()
            
            if resultados['query']['search']:
                titulo_pagina = resultados['query']['search'][0]['title']
                
                # Obtener el extracto y la imagen
                parametros_pagina = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'extracts|pageimages',
                    'exintro': True,
                    'explaintext': True,
                    'titles': titulo_pagina,
                    'pithumbsize': 300
                }
                
                response = self.session.get(url_api, params=parametros_pagina, timeout=8)
                response.raise_for_status()
                datos = response.json()
                
                pagina = next(iter(datos['query']['pages'].values()))
                
                descripcion = pagina.get('extract', '')[:400]  # Limitar a 400 caracteres
                url_wiki = f"https://es.wikipedia.org/wiki/{titulo_pagina.replace(' ', '_')}"
                url_imagen = pagina.get('thumbnail', {}).get('source', '')
                
                return {
                    'descripcion': descripcion,
                    'url_wikipedia': url_wiki,
                    'url_imagen': url_imagen,
                    'titulo_pagina': titulo_pagina
                }
            
            return None
            
        except Exception as e:
            print(f"  ⚠️ Error buscando en Wikipedia: {e}")
            return None
    
    def extraer_oracion(self, titulo_pagina):
        """Intenta extraer la oración del santo desde su página de Wikipedia"""
        url_api = "https://es.wikipedia.org/w/api.php"
        
        parametros = {
            'action': 'parse',
            'format': 'json',
            'page': titulo_pagina,
            'prop': 'wikitext'
        }
        
        try:
            response = self.session.get(url_api, params=parametros, timeout=8)
            response.raise_for_status()
            datos = response.json()
            
            if 'parse' in datos:
                wikitext = datos['parse']['wikitext']['*']
                
                # Buscar secciones de oración
                patrones = [
                    r'==\s*Oración\s*==\s*\n(.*?)(?:\n==|$)',
                    r'==\s*Plegaria\s*==\s*\n(.*?)(?:\n==|$)',
                    r'\[\[Oración\]\]\s*:\s*(.*?)(?:\n|$)'
                ]
                
                for patron in patrones:
                    match = re.search(patron, wikitext, re.IGNORECASE | re.DOTALL)
                    if match:
                        oracion = match.group(1).strip()
                        # Limpiar formato wiki
                        oracion = re.sub(r'\[\[.*?\|', '', oracion)
                        oracion = re.sub(r'\[\[(.*?)\]\]', r'\1', oracion)
                        oracion = re.sub(r'\{\{.*?\}\}', '', oracion)
                        oracion = re.sub(r"'''", '', oracion)
                        oracion = oracion.strip()
                        if len(oracion) > 20:
                            return oracion[:300]
            
            return ""
            
        except Exception as e:
            return ""
    
    def descargar_imagen(self, url_imagen, nombre_archivo):
        """Descarga una imagen desde una URL"""
        if not url_imagen:
            return ""
        
        try:
            response = self.session.get(url_imagen, timeout=10, stream=True)
            response.raise_for_status()
            
            # Determinar extensión
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                extension = '.jpg'
            elif 'png' in content_type:
                extension = '.png'
            else:
                extension = '.jpg'
            
            nombre_completo = nombre_archivo + extension
            ruta_completa = os.path.join(self.directorio_imagenes, nombre_completo)
            
            with open(ruta_completa, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return nombre_completo
            
        except Exception as e:
            print(f"  ⚠️ Error descargando imagen: {e}")
            return ""
    
    def procesar_dia(self, mes, dia):
        """Procesa un día completo y retorna los datos"""
        print(f"📅 Procesando {dia:02d}/{mes:02d}...")
        
        # Obtener santos del día (ahora retorna lista de diccionarios con nombre y url)
        santos = self.obtener_santos_del_dia(mes, dia)

        if not santos:
            print(f"  ⚠️ No se encontraron santos para el {dia:02d}/{mes:02d}")
            return []

        print(f"  ✅ Encontrados {len(santos)} santo(s)")
        resultados = []

        for santo_info in santos:
            nombre = santo_info.get('nombre')
            url = santo_info.get('url')
            resultado = self.procesar_santo_info(mes, dia, nombre, url)
            if resultado:  # Solo agregar si no fue None (ya existente)
                resultados.append(resultado)

        print()
        return resultados
    
    def generar_csv(self, datos):
        """Genera el archivo CSV con todos los datos (modo append para no perder datos existentes)"""
        print("📝 Generando archivo CSV...")
        
        # Determinar si el archivo existe
        archivo_existe = os.path.exists(self.archivo_csv)
        
        with open(self.archivo_csv, 'a' if archivo_existe else 'w', newline='', encoding='utf-8') as f:
            campos = ['mes', 'dia', 'nombre', 'descripcion', 'imagen', 'url_wikipedia', 'url_vatican', 'oracion']
            writer = csv.DictWriter(f, fieldnames=campos)
            
            # Solo escribir header si es archivo nuevo
            if not archivo_existe:
                writer.writeheader()
            
            for dato in datos:
                writer.writerow(dato)
                # Agregar al cache de existentes
                clave = f"{dato['mes']}-{dato['dia']}-{dato['nombre']}"
                self.santos_existentes.add(clave)
        
        print(f"✅ Archivo {self.archivo_csv} actualizado con {len(datos)} santos nuevos\n")
    
    def ejecutar(self, mes_inicio=1, dia_inicio=1, mes_fin=12, dia_fin=31):
        """Ejecuta el scraping para el rango de fechas especificado"""
        print("=" * 60)
        print("🔥 SCRAPER DE CALENDARIO DE SANTOS")
        print("=" * 60)
        print(f"📅 Procesando desde {dia_inicio:02d}/{mes_inicio:02d} hasta {dia_fin:02d}/{mes_fin:02d}")
        print("=" * 60)
        print()
        
        todos_los_datos = []
        
        # Días por mes
        dias_por_mes = {
            1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        
        for mes in range(mes_inicio, mes_fin + 1):
            inicio = dia_inicio if mes == mes_inicio else 1
            fin = dia_fin if mes == mes_fin else dias_por_mes[mes]

            # Si pedimos el mes completo, usar el parser de página mensual (más fiable)
            if inicio == 1 and fin == dias_por_mes[mes]:
                print(f"🔎 Obteniendo listado mensual para {mes:02d}...")
                santos_mes = self.obtener_santos_del_mes(mes)
                if not santos_mes:
                    print(f"  ⚠️ No se encontraron entradas en la página mensual para el mes {mes}")
                else:
                    print(f"  ✅ Encontrados {len(santos_mes)} enlaces en la página mensual")
                    for s in santos_mes:
                        dia = s.get('dia', 0) or 0
                        nombre = s.get('nombre')
                        url = s.get('url')
                        resultado = self.procesar_santo_info(mes, dia, nombre, url)
                        if resultado:  # Solo agregar si no fue None (ya existente)
                            todos_los_datos.append(resultado)

            else:
                for dia in range(inicio, fin + 1):
                    datos = self.procesar_dia(mes, dia)
                    todos_los_datos.extend(datos)
        
        # Generar CSV
        self.generar_csv(todos_los_datos)
        
        print("=" * 60)
        print("🎉 PROCESO COMPLETADO")
        print("=" * 60)
        print(f"✅ Santos procesados: {len(todos_los_datos)}")
        print(f"✅ Archivo CSV: {self.archivo_csv}")
        print(f"✅ Imágenes descargadas en: {self.directorio_imagenes}/")
        print("=" * 60)


def menu():
    """Menú interactivo"""
    print("\n" + "=" * 60)
    print("🔥 SCRAPER DE CALENDARIO DE SANTOS")
    print("=" * 60)
    print("\nOpciones disponibles:")
    print("  1️⃣  Procesar todo el año (365 días)")
    print("  2️⃣  Procesar un mes específico")
    print("  3️⃣  Procesar un rango de fechas")
    print("  4️⃣  Procesar desde hoy hasta fin de año")
    print("  0️⃣  Salir")
    print("=" * 60)
    
    opcion = input("\n👉 Selecciona una opción: ").strip()
    
    scraper = SantosCalendarioScraper()
    
    if opcion == "1":
        print("\n🚀 Procesando todo el año...")
        print("⏱️  Tiempo estimado: 2-3 horas\n")
        scraper.ejecutar(1, 1, 12, 31)
    
    elif opcion == "2":
        mes = int(input("👉 Mes (1-12): ").strip())
        # Calcular días correctos del mes
        dias_por_mes = {
            1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        ultimo_dia = dias_por_mes[mes]
        print(f"\n🚀 Procesando mes {mes}...")
        print("⏱️  Tiempo estimado: 15-20 minutos\n")
        scraper.ejecutar(mes, 1, mes, ultimo_dia)
    
    elif opcion == "3":
        print("Fecha de inicio:")
        mes_inicio = int(input("  👉 Mes (1-12): ").strip())
        dia_inicio = int(input("  👉 Día (1-31): ").strip())
        print("Fecha de fin:")
        mes_fin = int(input("  👉 Mes (1-12): ").strip())
        dia_fin = int(input("  👉 Día (1-31): ").strip())
        print(f"\n🚀 Procesando desde {dia_inicio:02d}/{mes_inicio:02d} hasta {dia_fin:02d}/{mes_fin:02d}...\n")
        scraper.ejecutar(mes_inicio, dia_inicio, mes_fin, dia_fin)
    
    elif opcion == "4":
        hoy = datetime.now()
        print(f"\n🚀 Procesando desde hoy ({hoy.day:02d}/{hoy.month:02d}) hasta fin de año...\n")
        scraper.ejecutar(hoy.month, hoy.day, 12, 31)
    
    elif opcion == "0":
        print("\n👋 ¡Hasta luego!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Opción no válida\n")


if __name__ == "__main__":
    menu()
