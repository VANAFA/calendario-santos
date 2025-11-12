#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper del Calendario de Santos - Versión Wikipedia
=====================================================
Este script extrae información de santos directamente desde Wikipedia.
Scrapea las páginas de cada día del año (ejemplo: https://es.wikipedia.org/wiki/4_de_noviembre)
y extrae los santos desde la sección "Santoral católico".

Para cada santo:
- Si tiene enlace a Wikipedia: descarga imagen y descripción
- Si NO tiene enlace: solo guarda el nombre (sin imagen ni botón Wikipedia)

Días sin santoral se registran en wikiproblematica.csv

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

class SantosWikipediaScraper:
    def __init__(self, descargar_imagenes=False):
        """
        Inicializa el scraper basado en Wikipedia
        
        Args:
            descargar_imagenes (bool): Si True, descarga imágenes desde Wikipedia.
                                       Si False, salta la descarga de imágenes.
                                       Default: False
        """
        self.descargar_imagenes = descargar_imagenes
        # Rutas relativas al directorio raíz del proyecto
        self.directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.directorio_imagenes = os.path.join(self.directorio_base, "web", "images")
        self.archivo_csv = os.path.join(self.directorio_base, "data", "santos.csv")
        self.archivo_problemas = os.path.join(self.directorio_base, "data", "wikiproblematica.csv")
        self.santos_existentes = {}
        
        # Headers para simular un navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Session reutilizable para requests
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Crear directorio de imágenes si no existe
        if not os.path.exists(self.directorio_imagenes):
            os.makedirs(self.directorio_imagenes)
        
        # Cargar santos existentes
        self._cargar_santos_existentes()
        
        # Inicializar archivo de problemas si no existe
        self._inicializar_archivo_problemas()
        
        # Cargar etiquetas especiales desde Wikipedia
        self.santos_argentinos = {}
        self.festividades_importantes = {}
        self.santos_scouts = {}
        self._cargar_etiquetas_especiales()
    
    def _cargar_santos_existentes(self):
        """Carga los santos ya procesados desde el CSV existente"""
        if os.path.exists(self.archivo_csv):
            try:
                with open(self.archivo_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        clave = f"{row['mes']}-{row['dia']}-{row['nombre']}"
                        self.santos_existentes[clave] = row
                print(f"✅ Cargados {len(self.santos_existentes)} santos existentes del CSV")
            except Exception as e:
                print(f"⚠️ Error al cargar santos existentes: {e}")
                self.santos_existentes = {}
    
    def _inicializar_archivo_problemas(self):
        """Inicializa el archivo de días problemáticos si no existe"""
        if not os.path.exists(self.archivo_problemas):
            with open(self.archivo_problemas, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['mes', 'dia', 'url', 'problema'])
    
    def _cargar_etiquetas_especiales(self):
        """Carga etiquetas especiales desde páginas de Wikipedia"""
        print("🏷️  Cargando etiquetas especiales desde Wikipedia...")
        
        # 1. Santos Argentinos
        try:
            url_arg = "https://es.wikipedia.org/wiki/Anexo:Santos_y_beatos_de_Argentina"
            response = self.session.get(url_arg, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tablas con santos argentinos
            for table in soup.find_all('table', class_='wikitable'):
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Extraer nombre (primera o segunda columna)
                        nombre_cell = cells[0] if cells[0].get_text(strip=True) else cells[1]
                        link = nombre_cell.find('a')
                        if link:
                            nombre = link.get_text(strip=True)
                            # Normalizar nombre
                            nombre_normalizado = self._normalizar_nombre_para_busqueda(nombre)
                            self.santos_argentinos[nombre_normalizado] = True
            
            print(f"  ✅ Cargados {len(self.santos_argentinos)} santos argentinos")
        except Exception as e:
            print(f"  ⚠️ Error cargando santos argentinos: {e}")
        
        # 2. Festividades Importantes
        try:
            # Festividades litúrgicas importantes
            festividades_conocidas = {
                'navidad': {'mes': 12, 'dia': 25, 'prioridad': 100},
                'inmaculada concepción': {'mes': 12, 'dia': 8, 'prioridad': 100},
                'asunción de maría': {'mes': 8, 'dia': 15, 'prioridad': 100},
                'todos los santos': {'mes': 11, 'dia': 1, 'prioridad': 100},
                'pentecostés': {'prioridad': 100},
                'corpus christi': {'prioridad': 100},
                'sagrado corazón': {'prioridad': 90},
                'san josé': {'mes': 3, 'dia': 19, 'prioridad': 95},
                'san pedro y san pablo': {'mes': 6, 'dia': 29, 'prioridad': 95},
                'santiago apóstol': {'mes': 7, 'dia': 25, 'prioridad': 95},
                'san juan bautista': {'mes': 6, 'dia': 24, 'prioridad': 95},
            }
            
            for festividad, info in festividades_conocidas.items():
                if 'mes' in info and 'dia' in info:
                    clave = f"{info['mes']}-{info['dia']}"
                    self.festividades_importantes[clave] = {
                        'nombre': festividad,
                        'prioridad': info['prioridad']
                    }
            
            print(f"  ✅ Cargadas {len(self.festividades_importantes)} festividades importantes")
        except Exception as e:
            print(f"  ⚠️ Error cargando festividades: {e}")
        
        # 3. Santos Scouts (Argentina)
        try:
            # Santos patronos del escultismo
            santos_scouts_conocidos = [
                'San Jorge',  # Patrono del escultismo mundial
                'San Pablo de la Cruz',  # Patrono scouts argentinos
                'Madre María Ana Mogas',  # Patrono guías argentinas
            ]
            
            for santo in santos_scouts_conocidos:
                nombre_normalizado = self._normalizar_nombre_para_busqueda(santo)
                self.santos_scouts[nombre_normalizado] = True
            
            print(f"  ✅ Cargados {len(self.santos_scouts)} santos scouts")
        except Exception as e:
            print(f"  ⚠️ Error cargando santos scouts: {e}")
        
        # 4. Patronos y Santos Argentinos (sin haber nacido en Argentina)
        try:
            # Santos patronos de Argentina o con especial devoción
            patronos_argentinos = [
                'San Martín de Tours',  # Patrono de Buenos Aires y Argentina
                'Nuestra Señora de Luján',  # Patrona de Argentina
                'San Cayetano',  # Gran devoción en Argentina
                'San Expedito',  # Gran devoción popular argentina
                'Santa Rosa de Lima',  # Primera santa de América
            ]
            
            # Agregar patronos a la lista de santos argentinos
            for santo in patronos_argentinos:
                nombre_normalizado = self._normalizar_nombre_para_busqueda(santo)
                self.santos_argentinos[nombre_normalizado] = True
            
            print(f"  ✅ Agregados {len(patronos_argentinos)} patronos/santos con devoción argentina")
        except Exception as e:
            print(f"  ⚠️ Error cargando patronos argentinos: {e}")
    
    def _normalizar_nombre_para_busqueda(self, nombre):
        """Normaliza un nombre para búsqueda en diccionarios"""
        # Remover prefijos
        nombre = re.sub(r'^(San|Santa|Santo|Beato|Beata|Bienaventurada?|Santos?|Madre)\s+', '', nombre, flags=re.IGNORECASE)
        # Convertir a minúsculas y quitar acentos
        nombre = nombre.lower()
        nombre = re.sub(r'[áàäâ]', 'a', nombre)
        nombre = re.sub(r'[éèëê]', 'e', nombre)
        nombre = re.sub(r'[íìïî]', 'i', nombre)
        nombre = re.sub(r'[óòöô]', 'o', nombre)
        nombre = re.sub(r'[úùüû]', 'u', nombre)
        nombre = re.sub(r'[ñ]', 'n', nombre)
        nombre = nombre.strip()
        return nombre
    
    def _determinar_etiquetas_y_prioridad(self, nombre, mes, dia):
        """
        Determina las etiquetas especiales y prioridad para un santo
        
        Returns:
            tuple: (etiquetas_str, prioridad)
        """
        etiquetas = []
        prioridad = 50  # Prioridad por defecto
        
        # Normalizar nombre para búsqueda
        nombre_busqueda = self._normalizar_nombre_para_busqueda(nombre)
        clave_dia = f"{mes}-{dia}"
        
        # Verificar si es festividad importante
        if clave_dia in self.festividades_importantes:
            etiquetas.append('festividad')
            prioridad = max(prioridad, self.festividades_importantes[clave_dia]['prioridad'])
        
        # Verificar si es santo argentino
        if nombre_busqueda in self.santos_argentinos:
            etiquetas.append('santo_argentino')
            prioridad = max(prioridad, 80)
        
        # Verificar si es santo scout
        if nombre_busqueda in self.santos_scouts:
            etiquetas.append('santo_scout')
            prioridad = max(prioridad, 70)
        
        # Convertir lista de etiquetas a string separado por comas
        etiquetas_str = ','.join(etiquetas) if etiquetas else ''
        
        return etiquetas_str, prioridad
    
    def _registrar_problema(self, mes, dia, problema):
        """Registra un día problemático en el CSV"""
        url = self._construir_url_dia(mes, dia)
        with open(self.archivo_problemas, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([mes, dia, url, problema])
        print(f"  ⚠️ Registrado en {self.archivo_problemas}: {problema}")
    
    def _construir_url_dia(self, mes, dia):
        """Construye la URL de Wikipedia para un día específico"""
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        mes_nombre = meses[mes - 1]
        return f"https://es.wikipedia.org/wiki/{dia}_de_{mes_nombre}"
    
    def _santo_ya_procesado(self, mes, dia, nombre):
        """Verifica si un santo ya fue procesado"""
        clave = f"{mes}-{dia}-{nombre}"
        return clave in self.santos_existentes
    
    def limpiar_nombre_archivo(self, nombre):
        """Convierte el nombre del santo en un nombre de archivo válido"""
        # Remover prefijos
        nombre = re.sub(r'^(San|Santa|Santo|Beato|Beata|Bienaventurada?|Santos?)\s+', '', nombre, flags=re.IGNORECASE)
        
        # Convertir a minúsculas y reemplazar caracteres especiales
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
        
        return nombre[:50]
    
    def extraer_santoral_del_dia(self, mes, dia):
        """
        Extrae los santos del día desde la página de Wikipedia
        
        Returns:
            list: Lista de diccionarios con 'nombre' y 'url_wikipedia' (puede ser None)
        """
        url = self._construir_url_dia(mes, dia)
        print(f"📅 Procesando {dia:02d}/{mes:02d}...")
        print(f"  🔗 URL: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la sección "Santoral católico"
            santoral_encontrado = False
            santoral_heading = None
            
            # Buscar en todos los encabezados h2 y h3
            for heading in soup.find_all(['h2', 'h3']):
                texto_heading = heading.get_text(strip=True)
                if 'Santoral' in texto_heading and 'católico' in texto_heading:
                    santoral_encontrado = True
                    santoral_heading = heading
                    break
            
            if not santoral_encontrado:
                self._registrar_problema(mes, dia, "No se encontró sección 'Santoral católico'")
                return []
            
            print(f"  ✅ Encontrada sección: {santoral_heading.get_text(strip=True)}")
            
            # Obtener el contenido después del encabezado hasta el siguiente encabezado
            santos = []
            
            # Buscar el elemento padre del heading (puede ser un div o la estructura directa)
            parent = santoral_heading.parent
            
            # Encontrar todas las listas después del heading
            # Buscar en el nivel del heading o en sus hermanos
            listas = []
            current = santoral_heading.find_next_sibling()
            
            while current and current.name not in ['h2', 'h3']:
                if current.name in ['ul', 'ol']:
                    listas.append(current)
                # También buscar listas dentro de divs
                elif current.name in ['div', 'figure']:
                    listas.extend(current.find_all(['ul', 'ol'], recursive=False))
                
                current = current.find_next_sibling()
            
            # Si no encontramos listas como hermanos, buscar en todo el contenido siguiente
            if not listas:
                # Buscar desde el heading hacia adelante en todo el HTML
                next_heading = santoral_heading.find_next(['h2', 'h3'])
                if next_heading:
                    # Buscar todas las listas entre el heading actual y el siguiente
                    for ul in santoral_heading.find_all_next(['ul', 'ol']):
                        # Verificar que la lista esté antes del siguiente heading
                        if next_heading and ul.sourceline and next_heading.sourceline:
                            if ul.sourceline < next_heading.sourceline:
                                listas.append(ul)
                        else:
                            listas.append(ul)
                        
                        # Limitar a las primeras 2 listas encontradas
                        if len(listas) >= 2:
                            break
            
            # Procesar las listas encontradas
            for lista in listas:
                items = lista.find_all('li', recursive=False)
                for item in items:
                    # Extraer el nombre del santo y su enlace si existe
                    enlaces = item.find_all('a')
                    
                    # Filtrar enlaces válidos (que apunten a artículos, no a años)
                    enlace_valido = None
                    for enlace in enlaces:
                        href = enlace.get('href', '')
                        if href.startswith('/wiki/') and not re.match(r'/wiki/\d{3,4}$', href):
                            enlace_valido = enlace
                            break
                    
                    if enlace_valido:
                        # Tiene enlace a Wikipedia
                        nombre_santo = enlace_valido.get_text(strip=True)
                        url_wikipedia = 'https://es.wikipedia.org' + enlace_valido['href']
                        
                        # Limpiar el nombre (remover información entre paréntesis al final)
                        nombre_santo = re.sub(r'\s*\([^)]*\)\s*$', '', nombre_santo)
                        
                        # Agregar espacio después de prefijos si está pegado
                        nombre_santo = re.sub(r'^(San|Santa|Santo|Beato|Beata|Santos)([A-Z])', r'\1 \2', nombre_santo)
                        
                        santos.append({
                            'nombre': nombre_santo,
                            'url_wikipedia': url_wikipedia
                        })
                    else:
                        # No tiene enlace, solo texto
                        texto = item.get_text(strip=True)
                        # Limpiar el texto (tomar solo el nombre antes de comas, paréntesis, etc.)
                        # Remover fechas y referencias
                        texto = re.sub(r'\(\d{3,4}[-–]\d{0,4}\)', '', texto)
                        texto = re.sub(r'\[.*?\]', '', texto)
                        nombre_santo = re.split(r'[,(]', texto)[0].strip()
                        
                        # Agregar espacio después de prefijos si está pegado
                        nombre_santo = re.sub(r'^(San|Santa|Santo|Beato|Beata|Santos)([A-Z])', r'\1 \2', nombre_santo)
                        
                        # Remover prefijos "San", "Santa" duplicados
                        nombre_santo = re.sub(r'^(San|Santa|Santo|Beato|Beata)\s+(San|Santa|Santo)', r'\1', nombre_santo, flags=re.IGNORECASE)
                        
                        if nombre_santo and len(nombre_santo) > 2:
                            santos.append({
                                'nombre': nombre_santo,
                                'url_wikipedia': None
                            })
            
            if not santos:
                self._registrar_problema(mes, dia, "Sección encontrada pero sin santos listados")
            else:
                print(f"  ✅ Encontrados {len(santos)} santo(s)")
            
            return santos
            
        except Exception as e:
            print(f"  ⚠️ Error obteniendo santos del {dia:02d}/{mes:02d}: {e}")
            self._registrar_problema(mes, dia, f"Error: {str(e)}")
            return []
    
    def obtener_info_wikipedia(self, url_wikipedia):
        """
        Obtiene descripción e imagen desde la página de Wikipedia del santo
        
        Returns:
            dict: {'descripcion': str, 'url_imagen': str} o None si hay error
        """
        try:
            response = self.session.get(url_wikipedia, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer descripción (primer párrafo del contenido)
            descripcion = ""
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                # Buscar el primer párrafo con contenido sustancial
                for p in content_div.find_all('p', recursive=False):
                    texto = p.get_text(strip=True)
                    
                    # Filtrar textos no deseados
                    if len(texto) < 50:  # Muy corto
                        continue
                    if 'creativecommons.org' in texto.lower():  # Licencias CC
                        continue
                    if 'PDMCreative Commons' in texto:  # Metadata de imágenes
                        continue
                    if texto.startswith('http://') or texto.startswith('https://'):  # URLs sueltas
                        continue
                    
                    descripcion = texto[:400]  # Limitar a 400 caracteres
                    break
            
            # Extraer URL de imagen (buscar en infobox)
            url_imagen = ""
            infobox = soup.find('table', class_='infobox')
            if infobox:
                img = infobox.find('img')
                if img and img.get('src'):
                    src = img['src']
                    
                    # Filtrar imágenes no deseadas
                    imagenes_excluidas = [
                        'Edit-clear.svg',  # Icono de edición
                        'Blue_pencil.svg',  # Lápiz azul de edición
                        'Nuvola_apps_kedit.svg',  # Otro icono de edición
                        'Question_book',  # Icono de pregunta
                        'Ambox',  # Iconos de aviso
                        'Red_question_mark',  # Marca de pregunta roja
                        'Emblem-question',  # Emblema de pregunta
                        'Gtk-dialog-question',  # Diálogo de pregunta
                        'Icon-round-Question_mark',  # Icono de interrogación
                        'Replacement_character.svg',  # Carácter de reemplazo
                        'No_image',  # Sin imagen
                        'Sin_foto.svg',  # Sin foto
                        'User-avatar',  # Avatar genérico
                        'Gnome-stock_person',  # Icono de persona
                    ]
                    
                    # Verificar si la imagen es un icono de sistema
                    es_icono_sistema = any(excl.lower() in src.lower() for excl in imagenes_excluidas)
                    
                    if not es_icono_sistema:
                        url_imagen = 'https:' + src if src.startswith('//') else src
                    else:
                        print(f"  ⚠️ Imagen filtrada (icono de sistema): {src.split('/')[-1]}")
            
            return {
                'descripcion': descripcion,
                'url_imagen': url_imagen
            }
            
        except Exception as e:
            print(f"  ⚠️ Error obteniendo info de Wikipedia: {e}")
            return None
    
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
            
            print(f"  📥 Imagen descargada: {nombre_completo}")
            return nombre_completo
            
        except Exception as e:
            print(f"  ⚠️ Error descargando imagen: {e}")
            return ""
    
    def _normalizar_nombre_santo(self, nombre):
        """
        Normaliza el nombre del santo asegurando que tenga el prefijo correcto
        
        Args:
            nombre: nombre del santo (puede tener o no el prefijo)
        
        Returns:
            str: nombre normalizado con prefijo "San/Santa/Beato/Beata/Santos"
        """
        # Ya tiene prefijo correcto, retornar tal cual
        if re.match(r'^(San|Santa|Santo|Beato|Beata|Santos|Santas|Bienaventurado|Bienaventurada)\s+', nombre, re.IGNORECASE):
            return nombre
        
        nombre_lower = nombre.lower()
        
        # Si tiene "y" es plural (ej: "Vidal y Agrícola")
        if ' y ' in nombre_lower:
            return f"Santos {nombre}"
        
        # Si contiene palabras clave de beato/venerable
        if any(word in nombre_lower for word in ['beato', 'beata', 'venerable', 'siervo de dios', 'sierva de dios']):
            # Ya tiene indicación de beato en el nombre mismo
            if nombre_lower.startswith(('beato', 'beata', 'venerable')):
                return nombre
            # Determinar género
            if self._es_nombre_femenino(nombre):
                return f"Beata {nombre}"
            else:
                return f"Beato {nombre}"
        
        # Es un santo regular, agregar San/Santa según género
        if self._es_nombre_femenino(nombre):
            return f"Santa {nombre}"
        else:
            return f"San {nombre}"
    
    def _es_nombre_femenino(self, nombre):
        """
        Determina si un nombre de santo es femenino
        
        Args:
            nombre: nombre del santo sin prefijo
        
        Returns:
            bool: True si es femenino, False si es masculino
        """
        nombre_lower = nombre.lower()
        
        # Lista de nombres comunes femeninos
        nombres_femeninos = ['maría', 'teresa', 'isabel', 'francisca', 'elena', 'ángela', 'catalina', 
                            'lucía', 'rosa', 'ana', 'margarita', 'mónica', 'cecilia', 'inés', 'clara', 
                            'beatriz', 'gertrudis', 'brígida', 'águeda', 'apolonia', 'dorotea', 
                            'escolástica', 'felicidad', 'perpetua', 'úrsula', 'victoria', 'zita', 
                            'marina', 'modesta', 'apolonia', 'virginia', 'regina', 'julia', 'juana']
        
        # Nombres masculinos que terminan en 'a' (excepciones)
        nombres_masculinos_con_a = ['cosme', 'damián', 'nicolás', 'tomás', 'lucas', 'matías', 'elías', 
                                    'isaías', 'jeremías', 'jonas', 'judas', 'vidal', 'agrícola', 
                                    'nicandro', 'pierio', 'amancio', 'perpetuo', 'emerico', 'félix']
        
        # Primero verificar si está en la lista de masculinos con 'a'
        primera_palabra = nombre_lower.split()[0] if nombre_lower.split() else nombre_lower
        if any(masc in primera_palabra for masc in nombres_masculinos_con_a):
            return False
        
        # Verificar si contiene algún nombre femenino
        if any(fem in nombre_lower for fem in nombres_femeninos):
            return True
        
        # Si termina en 'a' pero no es una excepción conocida, probablemente es femenino
        if nombre_lower.endswith('a'):
            return True
        
        # Por defecto, masculino
        return False
    
    def procesar_santo(self, mes, dia, santo_info):
        """
        Procesa un santo individual
        
        Args:
            mes: número del mes
            dia: número del día
            santo_info: dict con 'nombre' y 'url_wikipedia' (puede ser None)
        
        Returns:
            dict: Datos del santo para el CSV o None si ya fue procesado
        """
        nombre = santo_info['nombre']
        url_wikipedia = santo_info['url_wikipedia']
        
        # Normalizar el nombre (agregar San/Santa/Beato si no lo tiene)
        nombre_normalizado = self._normalizar_nombre_santo(nombre)
        
        # Verificar si ya fue procesado (con nombre normalizado)
        if self._santo_ya_procesado(mes, dia, nombre_normalizado):
            print(f"  ⏭️  Saltando (ya existe): {nombre_normalizado}")
            return None
        
        print(f"  🔍 Procesando: {nombre_normalizado}")
        
        descripcion = ""
        imagen = ""
        
        # Si tiene URL de Wikipedia, obtener info adicional
        if url_wikipedia:
            print(f"    ✅ Tiene Wikipedia: {url_wikipedia}")
            info_wiki = self.obtener_info_wikipedia(url_wikipedia)
            
            if info_wiki:
                descripcion = info_wiki['descripcion']
                
                # Descargar imagen si está activado
                if self.descargar_imagenes and info_wiki['url_imagen']:
                    nombre_archivo = self.limpiar_nombre_archivo(nombre)
                    imagen = self.descargar_imagen(info_wiki['url_imagen'], nombre_archivo)
        else:
            print(f"    ⚠️ Sin Wikipedia (no habrá imagen ni botón)")
            url_wikipedia = ""  # Asegurar que sea string vacío
        
        # Determinar etiquetas y prioridad
        etiquetas, prioridad = self._determinar_etiquetas_y_prioridad(nombre_normalizado, mes, dia)
        
        # Mostrar etiquetas si las tiene
        if etiquetas:
            etiquetas_display = etiquetas.replace(',', ', ').replace('_', ' ').title()
            print(f"    🏷️  Etiquetas: {etiquetas_display} | Prioridad: {prioridad}")
        
        resultado = {
            'mes': mes,
            'dia': dia,
            'nombre': nombre_normalizado,  # Usar nombre normalizado
            'prioridad': prioridad,  # Prioridad calculada según etiquetas
            'descripcion': descripcion,
            'imagen': imagen,
            'url_wikipedia': url_wikipedia if url_wikipedia else "",
            'etiquetas': etiquetas,  # Nueva columna
            'oracion': ""  # Vacío por ahora
        }
        
        print(f"    ✅ Completado")
        time.sleep(0.5)  # Pausa para no saturar Wikipedia
        
        return resultado
    
    def _limpiar_santos_del_dia(self, mes, dia):
        """
        Elimina todos los santos de un día específico del CSV y sus imágenes
        
        Args:
            mes: número del mes
            dia: número del día
        """
        print(f"  🗑️  Eliminando santos existentes del {dia:02d}/{mes:02d}...")
        
        # Leer el CSV actual
        santos_filtrados = []
        santos_eliminados = []
        imagenes_a_eliminar = []
        
        if os.path.exists(self.archivo_csv):
            with open(self.archivo_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['mes']) == mes and int(row['dia']) == dia:
                        santos_eliminados.append(row['nombre'])
                        if row.get('imagen'):
                            imagenes_a_eliminar.append(row['imagen'])
                    else:
                        santos_filtrados.append(row)
        
        # Reescribir el CSV sin los santos del día
        if santos_filtrados:
            with open(self.archivo_csv, 'w', newline='', encoding='utf-8') as f:
                campos = ['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'etiquetas', 'oracion']
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                # Asegurar que todos los registros tengan el campo etiquetas
                for santo in santos_filtrados:
                    if 'etiquetas' not in santo:
                        santo['etiquetas'] = ''
                writer.writerows(santos_filtrados)
        
        # Eliminar imágenes asociadas
        for imagen in imagenes_a_eliminar:
            ruta_imagen = os.path.join(self.directorio_imagenes, imagen)
            if os.path.exists(ruta_imagen):
                try:
                    os.remove(ruta_imagen)
                    print(f"    🗑️  Imagen eliminada: {imagen}")
                except Exception as e:
                    print(f"    ⚠️  Error eliminando imagen {imagen}: {e}")
        
        # Actualizar el diccionario de santos existentes
        claves_a_eliminar = [f"{mes}-{dia}-{nombre}" for nombre in santos_eliminados]
        for clave in claves_a_eliminar:
            if clave in self.santos_existentes:
                del self.santos_existentes[clave]
        
        print(f"    ✅ Eliminados {len(santos_eliminados)} santos y {len(imagenes_a_eliminar)} imágenes")
    
    def procesar_dia(self, mes, dia, eliminar_existentes=None):
        """
        Procesa un día completo y retorna los datos
        
        Args:
            mes: número del mes
            dia: número del día
            eliminar_existentes: None (preguntar), True (eliminar), False (mantener)
        """
        # Verificar si ya hay santos para este día
        santos_existentes_dia = [s for s in self.santos_existentes.values() 
                                 if int(s['mes']) == mes and int(s['dia']) == dia]
        
        if santos_existentes_dia:
            if eliminar_existentes is None:
                # Preguntar al usuario
                print(f"  ⚠️  Ya existen {len(santos_existentes_dia)} santos para el {dia:02d}/{mes:02d}")
                respuesta = input("  ❓ ¿Eliminar datos viejos y recalcular? (s/N): ").strip().lower()
                eliminar_existentes = (respuesta == 's')
            
            if eliminar_existentes:
                self._limpiar_santos_del_dia(mes, dia)
            else:
                print(f"  ℹ️  Manteniendo datos existentes, solo se agregarán santos nuevos")
        
        santos_info = self.extraer_santoral_del_dia(mes, dia)
        
        if not santos_info:
            return []
        
        resultados = []
        for santo_info in santos_info:
            resultado = self.procesar_santo(mes, dia, santo_info)
            if resultado:
                resultados.append(resultado)
        
        print()
        return resultados
    
    def generar_csv(self, datos):
        """Genera el archivo CSV con todos los datos"""
        print("📝 Actualizando archivo CSV...")
        
        archivo_existe = os.path.exists(self.archivo_csv)
        
        with open(self.archivo_csv, 'a' if archivo_existe else 'w', newline='', encoding='utf-8') as f:
            campos = ['mes', 'dia', 'nombre', 'prioridad', 'descripcion', 'imagen', 'url_wikipedia', 'etiquetas', 'oracion']
            writer = csv.DictWriter(f, fieldnames=campos)
            
            if not archivo_existe:
                writer.writeheader()
            
            for dato in datos:
                # Asegurar que etiquetas existe
                if 'etiquetas' not in dato:
                    dato['etiquetas'] = ''
                writer.writerow(dato)
                clave = f"{dato['mes']}-{dato['dia']}-{dato['nombre']}"
                self.santos_existentes[clave] = dato
        
        print(f"✅ Archivo {self.archivo_csv} actualizado con {len(datos)} santos nuevos\n")
    
    def ejecutar(self, mes_inicio=1, dia_inicio=1, mes_fin=12, dia_fin=31, eliminar_existentes=None):
        """
        Ejecuta el scraping para el rango de fechas especificado
        
        Args:
            mes_inicio: mes inicial
            dia_inicio: día inicial
            mes_fin: mes final
            dia_fin: día final
            eliminar_existentes: None (preguntar), True (eliminar siempre), False (nunca eliminar)
        """
        print("=" * 60)
        print("🔥 SCRAPER DE CALENDARIO DE SANTOS (Wikipedia)")
        print("=" * 60)
        print(f"📅 Procesando desde {dia_inicio:02d}/{mes_inicio:02d} hasta {dia_fin:02d}/{mes_fin:02d}")
        print(f"📥 Descarga de imágenes: {'✅ ACTIVADA' if self.descargar_imagenes else '❌ DESACTIVADA'}")
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
            
            for dia in range(inicio, fin + 1):
                datos = self.procesar_dia(mes, dia, eliminar_existentes=eliminar_existentes)
                todos_los_datos.extend(datos)
        
        # Generar CSV
        if todos_los_datos:
            self.generar_csv(todos_los_datos)
        
        print("=" * 60)
        print("🎉 PROCESO COMPLETADO")
        print("=" * 60)
        print(f"✅ Santos procesados: {len(todos_los_datos)}")
        print(f"✅ Archivo CSV: {self.archivo_csv}")
        if self.descargar_imagenes:
            print(f"✅ Imágenes descargadas en: {self.directorio_imagenes}/")
        print(f"⚠️  Problemas registrados en: {self.archivo_problemas}")
        print("=" * 60)


def menu():
    """Menú interactivo"""
    print("\n" + "=" * 60)
    print("🔥 SCRAPER DE CALENDARIO DE SANTOS (Wikipedia)")
    print("=" * 60)
    print("\nOpciones disponibles:")
    print("  1️⃣  Procesar todo el año (365 días)")
    print("  2️⃣  Procesar un mes específico")
    print("  3️⃣  Procesar un rango de fechas")
    print("  4️⃣  Procesar un día específico")
    print("  0️⃣  Salir")
    print("=" * 60)
    
    opcion = input("\n👉 Selecciona una opción: ").strip()
    
    # Preguntar si desea descargar imágenes
    descargar = input("👉 ¿Descargar imágenes? (s/N): ").strip().lower()
    descargar_imagenes = descargar == 's'
    
    scraper = SantosWikipediaScraper(descargar_imagenes=descargar_imagenes)
    
    if opcion == "1":
        print("\n🚀 Procesando todo el año...")
        scraper.ejecutar(1, 1, 12, 31)
    
    elif opcion == "2":
        mes = int(input("👉 Mes (1-12): ").strip())
        dias_por_mes = {
            1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        ultimo_dia = dias_por_mes[mes]
        print(f"\n🚀 Procesando mes {mes}...")
        scraper.ejecutar(mes, 1, mes, ultimo_dia)
    
    elif opcion == "3":
        print("Fecha de inicio:")
        mes_inicio = int(input("  👉 Mes (1-12): ").strip())
        dia_inicio = int(input("  👉 Día (1-31): ").strip())
        print("Fecha de fin:")
        mes_fin = int(input("  👉 Mes (1-12): ").strip())
        dia_fin = int(input("  👉 Día (1-31): ").strip())
        print(f"\n🚀 Procesando desde {dia_inicio:02d}/{mes_inicio:02d} hasta {dia_fin:02d}/{mes_fin:02d}...")
        scraper.ejecutar(mes_inicio, dia_inicio, mes_fin, dia_fin)
    
    elif opcion == "4":
        mes = int(input("👉 Mes (1-12): ").strip())
        dia = int(input("👉 Día (1-31): ").strip())
        print(f"\n🚀 Procesando {dia:02d}/{mes:02d}...")
        scraper.ejecutar(mes, dia, mes, dia)
    
    elif opcion == "0":
        print("\n👋 ¡Hasta luego!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Opción no válida\n")


if __name__ == "__main__":
    menu()
