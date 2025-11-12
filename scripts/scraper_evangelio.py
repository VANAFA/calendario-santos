#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper para obtener el Evangelio del Día desde Vatican News (RSS)
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import warnings
from bs4 import XMLParsedAsHTMLWarning

# Suprimir warning de XML parseado como HTML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

class EvangelioScraper:
    def __init__(self):
        # Página HTML directa en vez de RSS
        self.url = "https://www.vaticannews.va/es/evangelio-de-hoy.html"
        self.rss_url = "https://www.vaticannews.va/content/vaticannews/es/evangelio-de-hoy.rss.xml"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Rutas relativas al directorio raíz del proyecto
        import os
        self.directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def obtener_evangelio_del_dia(self):
        """
        Obtiene el evangelio del día - primero intenta desde página HTML, luego RSS
        """
        # Intentar primero desde la página HTML (tiene contenido completo)
        resultado = self._obtener_desde_html()
        if resultado and resultado.get('exito'):
            return resultado
        
        # Si falla, intentar desde RSS
        print("⚠️ Página HTML falló, intentando RSS...")
        return self._obtener_desde_rss()
    
    def _obtener_desde_html(self):
        """Obtiene el evangelio desde la página HTML de Vatican News"""
        try:
            print("🔍 Obteniendo evangelio del día desde Vatican News (página HTML)...")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            resultado = {
                'fecha': datetime.now().strftime('%d de %B de %Y'),
                'timestamp': datetime.now().isoformat(),
                'titulo': 'Evangelio del día',
                'lectura': None,
                'salmo': None,
                'evangelio': None,
                'exito': False
            }
            
            # Buscar el contenedor principal del evangelio
            contenido = soup.find('div', class_='section__content')
            if not contenido:
                contenido = soup.find('article')
            if not contenido:
                contenido = soup.find('div', {'id': 'content'})
            
            if not contenido:
                print("❌ No se encontró el contenedor de contenido")
                return None
            
            # Extraer todos los párrafos
            parrafos = contenido.find_all(['p', 'div'], recursive=True)
            
            seccion_actual = None
            primera_lectura_ref = ""
            primera_lectura_texto = []
            salmo_ref = ""
            salmo_texto = []
            evangelio_ref = ""
            evangelio_texto = []
            
            for elemento in parrafos:
                texto = elemento.get_text(separator=' ', strip=True)
                if not texto or len(texto) < 5:
                    continue
                
                texto_lower = texto.lower()
                
                # Detectar secciones
                if 'primera lectura' in texto_lower or 'lectura del libro' in texto_lower or 'lectura de la carta' in texto_lower:
                    seccion_actual = 'lectura'
                    if len(texto) < 100:  # Es solo el título
                        primera_lectura_ref = texto
                    continue
                elif 'salmo' in texto_lower and len(texto) < 50:
                    seccion_actual = 'salmo'
                    salmo_ref = texto
                    continue
                elif 'evangelio' in texto_lower or 'santo evangelio según' in texto_lower:
                    seccion_actual = 'evangelio'
                    if len(texto) < 100:  # Es solo el título
                        evangelio_ref = texto
                    continue
                
                # Agregar contenido a la sección actual
                if seccion_actual == 'lectura' and len(texto) > 30:
                    primera_lectura_texto.append(texto)
                elif seccion_actual == 'salmo' and len(texto) > 20:
                    salmo_texto.append(texto)
                elif seccion_actual == 'evangelio' and len(texto) > 30:
                    evangelio_texto.append(texto)
            
            # Construir resultado
            if primera_lectura_texto:
                resultado['lectura'] = {
                    'referencia': primera_lectura_ref,
                    'texto': ' '.join(primera_lectura_texto)
                }
            
            if salmo_texto:
                resultado['salmo'] = {
                    'referencia': salmo_ref,
                    'texto': ' '.join(salmo_texto)
                }
            
            if evangelio_texto:
                resultado['evangelio'] = {
                    'referencia': evangelio_ref,
                    'texto': ' '.join(evangelio_texto)
                }
            
            if resultado['evangelio'] or resultado['lectura']:
                resultado['exito'] = True
                print("✅ Evangelio obtenido exitosamente desde página HTML")
            else:
                print("⚠️ No se encontraron secciones del evangelio")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al obtener desde HTML: {e}")
            return None
    
    def _obtener_desde_rss(self):
        """
        Obtiene el evangelio del día desde el RSS de Vatican News (fallback)
        """
        try:
            print("🔍 Obteniendo evangelio del día desde Vatican News RSS...")
            response = requests.get(self.rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Usar html.parser en lugar de xml
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Obtener el primer item (evangelio más reciente)
            item = soup.find('item')
            
            if not item:
                print("❌ No se encontró ningún item en el RSS")
                return self._resultado_error("No se encontró contenido en el RSS")
            
            # Extraer datos básicos
            titulo = item.find('title').get_text(strip=True) if item.find('title') else ""
            fecha_pub = item.find('pubDate').get_text(strip=True) if item.find('pubDate') else ""
            descripcion = item.find('description').get_text(strip=True) if item.find('description') else ""
            
            # El contenido completo está en description (puede estar en CDATA)
            contenido_html = descripcion
            
            # Parsear el HTML dentro del RSS
            contenido_soup = BeautifulSoup(contenido_html, 'html.parser')
            
            resultado = {
                'fecha': self._formatear_fecha(fecha_pub),
                'fecha_publicacion': fecha_pub,
                'timestamp': datetime.now().isoformat(),
                'titulo': titulo,
                'lectura': None,
                'salmo': None,
                'evangelio': None,
                'exito': False
            }
            
            # Extraer todas las secciones del contenido
            texto_completo = contenido_soup.get_text(separator='\n', strip=True)
            
            # Dividir por secciones usando patrones
            secciones = self._dividir_secciones(texto_completo)
            
            if secciones:
                resultado.update(secciones)
                resultado['exito'] = True
                print("✅ Evangelio obtenido exitosamente del RSS")
            else:
                # Guardar todo el contenido si no pudimos dividirlo
                resultado['contenido_completo'] = texto_completo
                resultado['exito'] = True
                print("⚠️ Contenido obtenido pero no dividido en secciones")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al obtener evangelio: {e}")
            return self._resultado_error(str(e))
    
    def _formatear_fecha(self, fecha_rss):
        """Convierte la fecha del RSS a formato legible"""
        try:
            # Fecha RSS: "Wed, 05 Nov 2025 00:00:00 GMT"
            from datetime import datetime
            dt = datetime.strptime(fecha_rss, "%a, %d %b %Y %H:%M:%S %Z")
            
            meses = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }
            
            return f"{dt.day} de {meses[dt.month]} de {dt.year}"
        except:
            return datetime.now().strftime('%d de %B de %Y')
    
    def _dividir_secciones(self, texto):
        """Divide el texto en secciones: lectura, salmo, evangelio"""
        secciones = {}
        
        # El RSS tiene una estructura más simple, vamos a buscar por patrones específicos
        lineas = texto.split('\n')
        
        seccion_actual = None
        contenido_actual = []
        referencia_actual = ""
        
        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()
            
            # Detectar inicio de Primera Lectura
            if 'Lectura de la carta' in linea or 'Lectura del libro' in linea or 'PRIMERA LECTURA' in linea:
                if seccion_actual and contenido_actual:
                    secciones[seccion_actual] = {
                        'tipo': seccion_actual,
                        'referencia': referencia_actual,
                        'titulo': lineas[i+1].strip() if i+1 < len(lineas) else '',
                        'texto': '\n\n'.join(contenido_actual)
                    }
                seccion_actual = 'lectura'
                contenido_actual = []
                referencia_actual = linea
                i += 1  # Saltar a la siguiente línea (la referencia bíblica)
                if i < len(lineas):
                    titulo_ref = lineas[i].strip()
                    i += 1
                continue
            
            # Detectar inicio de Salmo
            elif 'SALMO' in linea.upper() and 'Salmo' in linea:
                if seccion_actual and contenido_actual:
                    secciones[seccion_actual] = {
                        'tipo': seccion_actual,
                        'referencia': referencia_actual,
                        'titulo': '',
                        'texto': '\n\n'.join(contenido_actual)
                    }
                seccion_actual = 'salmo'
                contenido_actual = []
                referencia_actual = linea
                i += 1
                continue
            
            # Detectar inicio de Evangelio
            elif 'Lectura del santo evangelio' in linea or 'EVANGELIO' in linea:
                if seccion_actual and contenido_actual:
                    secciones[seccion_actual] = {
                        'tipo': seccion_actual,
                        'referencia': referencia_actual,
                        'titulo': '',
                        'texto': '\n\n'.join(contenido_actual)
                    }
                seccion_actual = 'evangelio'
                contenido_actual = []
                referencia_actual = linea
                i += 1  # Saltar a la siguiente línea (la referencia bíblica)
                if i < len(lineas):
                    titulo_ref = lineas[i].strip()
                    i += 1
                continue
            
            # Agregar contenido a la sección actual
            elif seccion_actual and linea and len(linea) > 10:
                contenido_actual.append(linea)
            
            i += 1
        
        # Agregar la última sección
        if seccion_actual and contenido_actual:
            secciones[seccion_actual] = {
                'tipo': seccion_actual,
                'referencia': referencia_actual,
                'titulo': '',
                'texto': '\n\n'.join(contenido_actual)
            }
        
        return secciones if secciones else None
    
    def _parsear_seccion(self, texto, tipo):
        """Parsea una sección individual"""
        lineas = texto.split('\n')
        lineas = [l.strip() for l in lineas if l.strip()]
        
        referencia = ""
        titulo = ""
        contenido_lineas = []
        
        for i, linea in enumerate(lineas):
            # La primera línea suele ser el título/referencia
            if i == 0 and len(linea) < 100:
                referencia = linea
            elif i == 1 and len(linea) < 100 and not linea.endswith('.'):
                titulo = linea
            else:
                contenido_lineas.append(linea)
        
        return {
            'tipo': tipo,
            'referencia': referencia,
            'titulo': titulo,
            'texto': '\n\n'.join(contenido_lineas)
        }
    
    def _resultado_error(self, mensaje):
        """Retorna un resultado de error"""
        return {
            'fecha': datetime.now().strftime('%d de %B de %Y'),
            'timestamp': datetime.now().isoformat(),
            'error': mensaje,
            'exito': False
        }
    
    def guardar_json(self, datos, archivo='evangelio_hoy.json'):
        """Guarda los datos en un archivo JSON"""
        try:
            import os
            # Si no se especifica ruta completa, usar directorio data
            if not os.path.isabs(archivo):
                archivo = os.path.join(self.directorio_base, "data", archivo)
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            print(f"💾 Datos guardados en {archivo}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar JSON: {e}")
            return False


def main():
    scraper = EvangelioScraper()
    datos = scraper.obtener_evangelio_del_dia()
    
    print("\n📊 Resultado:")
    print(f"Fecha: {datos.get('fecha', 'N/A')}")
    print(f"Éxito: {datos.get('exito', False)}")
    
    if datos.get('lectura'):
        print(f"\n📖 Primera Lectura:")
        print(f"  Referencia: {datos['lectura'].get('referencia', 'N/A')}")
        print(f"  Texto: {datos['lectura'].get('texto', 'N/A')[:150]}...")
    
    if datos.get('evangelio'):
        print(f"\n✝️ Evangelio:")
        print(f"  Referencia: {datos['evangelio'].get('referencia', 'N/A')}")
        print(f"  Texto: {datos['evangelio'].get('texto', 'N/A')[:150]}...")
    
    # Guardar en JSON
    scraper.guardar_json(datos)
    
    print("\n✅ Proceso completado")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
