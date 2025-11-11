# 📁 Nueva Estructura del Proyecto - Guía Completa

## ✅ Cambios Realizados

### 1. Reorganización de Archivos

Se creó una estructura profesional de carpetas:

```
calendario-santos/
│
├── 🐍 Scripts Python
│   scripts/
│   ├── scraper_santos_wikipedia.py    # Scraper principal de santos
│   ├── scraper_evangelio.py           # Scraper de evangelio
│   ├── migrar_csv_etiquetas.py        # Utilidad de migración
│   └── dedupe_santos.py               # Eliminar duplicados
│
├── 🌐 Archivos Web
│   web/
│   ├── index.html                     # Página principal del calendario
│   ├── cita-biblica.html              # Página del evangelio
│   └── images/                        # Imágenes de santos (1000+ archivos)
│
├── 📊 Datos
│   data/
│   ├── santos.csv                     # Base de datos principal (1681 santos)
│   ├── evangelio_hoy.json             # Evangelio del día actual
│   └── wikiproblematica.csv           # Log de días con problemas
│
├── 💾 Backups
│   backups/
│   └── *.backup, *.bak                # Copias automáticas de seguridad
│
├── 📚 Documentación
│   docs/
│   ├── ETIQUETAS_IMPLEMENTATION.md    # Sistema de etiquetas
│   ├── GUIA_ACTUALIZACION.md          # Guía de actualización
│   ├── INSTRUCCIONES_SCRAPER.md       # Manual del scraper
│   └── ...
│
├── 🚀 Archivos Principales
│   ├── main.py                        # Script principal (NUEVO)
│   ├── inicio.sh                      # Script de inicio rápido (NUEVO)
│   ├── requirements.txt               # Dependencias Python
│   ├── README.md                      # Documentación principal
│   └── .gitignore                     # Ignorar archivos innecesarios
│
└── 🗑️ Archivos Eliminados
    ├── ❌ migrate_priorities.py       # Obsoleto
    ├── ❌ recalcular_datos.py        # Obsoleto
    ├── ❌ remove_vatican_column.py   # Obsoleto
    ├── ❌ test_google_images.py      # Obsoleto
    ├── ❌ test_scraper_completo.py   # Obsoleto
    └── ❌ test_wikipedia_completo.py # Obsoleto
```

### 2. Actualización de Rutas

Todos los scripts ahora usan **rutas absolutas** calculadas automáticamente:

```python
# Antes (rutas relativas - causaban errores)
archivo_csv = "santos.csv"
directorio_imagenes = "images"

# Ahora (rutas absolutas - funciona desde cualquier lugar)
directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
archivo_csv = os.path.join(directorio_base, "data", "santos.csv")
directorio_imagenes = os.path.join(directorio_base, "web", "images")
```

### 3. Nuevo Script Principal: main.py

Centraliza todas las operaciones en un solo lugar:

#### Uso Interactivo:
```bash
python3 main.py
```

Muestra un menú con opciones:
```
🗓️  CALENDARIO DE SANTOS - SISTEMA DE ACTUALIZACIÓN
====================================================================
Opciones disponibles:
  1. Actualizar Evangelio del día
  2. Actualizar Santos (todo el año)
  3. Actualizar Santos (un día específico)
  4. Actualizar todo (evangelio + santos)
  5. Salir
====================================================================
```

#### Uso por Línea de Comandos:
```bash
# Solo evangelio
python3 main.py --evangelio

# Todos los santos (toma horas)
python3 main.py --santos

# Un día específico
python3 main.py --santos-dia 11 11

# Ayuda
python3 main.py --help
```

### 4. Script de Inicio Rápido

```bash
# Opción 1: Usar el script de inicio (recomendado)
./inicio.sh

# Opción 2: Activar manualmente
source venv/bin/activate
python3 main.py
```

El script `inicio.sh`:
- ✅ Activa automáticamente el entorno virtual
- ✅ Instala dependencias faltantes
- ✅ Ejecuta main.py con los argumentos dados

## 🚀 Guía de Uso Rápida

### Primera Vez

```bash
# 1. Clonar repositorio
git clone https://github.com/VANAFA/calendario-santos.git
cd calendario-santos

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python3 main.py
```

### Uso Diario

```bash
# Actualizar solo el evangelio del día
./inicio.sh --evangelio

# Actualizar un santo específico
./inicio.sh --santos-dia 12 8  # 8 de diciembre
```

### Desarrollo Web

```bash
# Servidor local para probar la web
cd web
python3 -m http.server 8080

# Abrir en navegador
firefox http://localhost:8080
```

## 📊 Sistema de Etiquetas

Los santos ahora tienen etiquetas automáticas:

| Etiqueta | Prioridad | Ejemplos |
|----------|-----------|----------|
| `festividad` | 100 | Navidad (25/12), Inmaculada (8/12) |
| `santo_argentino` | 80 | San Martín de Tours, Ceferino Namuncurá |
| `santo_scout` | 70 | San Jorge (23/4), San Pablo de la Cruz |
| (ninguna) | 50 | Santos normales |

### Cómo Funciona

1. **Al ejecutar el scraper**, se cargan automáticamente:
   - 62 santos argentinos desde Wikipedia
   - 5 patronos argentinos (San Martín de Tours, etc.)
   - 8 festividades litúrgicas importantes
   - 3 santos scouts

2. **Cada santo se analiza** para determinar si corresponde a alguna categoría

3. **Se asigna prioridad automática** según sus etiquetas

4. **Se guarda en el CSV** con la columna `etiquetas`

## 🔧 Mantenimiento

### Eliminar Duplicados

```bash
cd scripts
python3 dedupe_santos.py
```

### Migrar CSV (agregar columna etiquetas)

```bash
cd scripts
python3 migrar_csv_etiquetas.py
```

### Logs y Problemas

Los días problemáticos se registran en:
```
data/wikiproblematica.csv
```

Ejemplo:
```csv
mes,dia,url,problema
11,11,https://es.wikipedia.org/wiki/11_de_noviembre,"Sección encontrada pero sin santos listados"
```

## 🎯 Próximos Pasos

### 1. Actualizar Todo el Año

```bash
python3 main.py --santos
```

⚠️ **Advertencia**: Esto toma varias horas (365 días × 0.5s por santo)

### 2. Actualizar Frontend

El frontend (`web/index.html`) ya está listo para mostrar etiquetas, pero podrías agregar:
- Badges visuales para cada etiqueta
- Filtros por categoría
- Buscador por etiquetas

### 3. Automatizar Actualizaciones

Crear un cron job para actualizar el evangelio diariamente:

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar a las 6 AM cada día)
0 6 * * * cd /ruta/al/proyecto && ./inicio.sh --evangelio
```

## 📝 Notas Importantes

1. **Backups Automáticos**: Cada vez que se edita `santos.csv`, se crea un backup en `backups/`

2. **Git Ignore**: Los backups están en `.gitignore`, no se subirán a GitHub

3. **Imágenes**: Las 1000+ imágenes en `web/images/` ocupan ~60MB

4. **CSV**: `data/santos.csv` tiene 1681 santos (puede crecer al scrapear todo el año)

## 🐛 Solución de Problemas

### Error: "No module named 'bs4'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Permission denied: inicio.sh"
```bash
chmod +x inicio.sh
```

### Error: "FileNotFoundError: santos.csv"
Verifica que estés ejecutando desde el directorio raíz:
```bash
cd /ruta/al/proyecto
python3 main.py
```

### El scraper no encuentra imágenes
Verifica que `descargar_imagenes=True`:
```python
scraper = SantosWikipediaScraper(descargar_imagenes=True)
```

## 📞 Soporte

Para reportar problemas o sugerir mejoras:
- GitHub Issues: https://github.com/VANAFA/calendario-santos/issues
- Documentación adicional en `docs/`

---

**Última actualización**: 11 de Noviembre de 2025
**Versión**: 2.0 (Nueva Estructura)
