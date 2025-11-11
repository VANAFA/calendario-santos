# 🔧 INSTRUCCIONES DE CONFIGURACIÓN

## Toggle de Imágenes

### Estado Actual
Por defecto, la descarga de imágenes está **DESACTIVADA** ⛔

### Para ACTIVAR la descarga de imágenes:

#### En el scraper principal (`scraper_santos.py`):

Busca la función `menu()` al final del archivo y cambia:

```python
# Líneas 741, 749, 758, 766
scraper = SantosCalendarioScraper()
```

Por:

```python
scraper = SantosCalendarioScraper(descargar_imagenes=True)
```

#### En el script de recalculación (`recalcular_datos.py`):

Busca al final del archivo y cambia:

```python
# Línea 83
recalcular_todos_los_datos(descargar_imagenes=False)
```

Por:

```python
recalcular_todos_los_datos(descargar_imagenes=True)
```

---

## Etiqueta "Festividad"

### Estado Actual
La etiqueta "✨ Festividad" está **DESACTIVADA** ⛔

### Comportamiento:
- Ya NO se muestra automáticamente para santos con prioridad 100
- Solo se muestran las etiquetas:
  - ⭐ Santo Patrono de Argentina (prioridad 90-95)
  - 🇦🇷 Santo Argentino (prioridad 85-89)

### Para agregar manualmente festividades:

Tendrás que editar el CSV directamente o modificar el código del frontend (`index.html`) para agregar casos específicos.

---

## Uso Recomendado

### Scraping sin imágenes (RÁPIDO):
```bash
cd "/home/vanafa/Documents/Calendario de santos"
source venv/bin/activate
python3 scraper_santos.py
# Seleccionar opción deseada
```
⏱️ Tiempo: ~30-60 minutos para todo el año

### Scraping con imágenes (LENTO):
1. Activar el toggle como se indica arriba
2. Ejecutar el scraper
⏱️ Tiempo: ~3-4 horas para todo el año

### Solo recalcular prioridades y Wikipedia:
```bash
cd "/home/vanafa/Documents/Calendario de santos"
source venv/bin/activate
python3 recalcular_datos.py
```
⏱️ Tiempo: ~1-2 horas para ~2663 santos

---

## Cambios Realizados

✅ Toggle de imágenes agregado al scraper  
✅ Toggle de imágenes agregado al script de recalculación  
✅ Etiqueta "Festividad" removida del frontend  
✅ Documentación agregada en el código  
✅ Comentarios actualizados  

---

## Archivos Modificados

1. `scraper_santos.py` - Toggle de imágenes agregado
2. `recalcular_datos.py` - Toggle de imágenes agregado
3. `index.html` - Etiqueta "Festividad" removida
4. `INSTRUCCIONES_TOGGLE.md` - Este archivo
