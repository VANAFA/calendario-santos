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
        self.rss_url = "https://www.vaticannews.va/content/vaticannews/es/evangelio-de-hoy.rss.xml"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def obtener_evangelio_del_dia(self):
        """
        Obtiene el evangelio del día desde el RSS de Vatican News
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
