# 📖 Evangelio del Día - Vatican News

Este sistema obtiene automáticamente las lecturas del día (Primera Lectura, Salmo y Evangelio) desde Vatican News.

## 🚀 Uso

### Actualización manual

Para actualizar el evangelio del día manualmente:

```bash
./actualizar_evangelio.sh
```

O directamente con Python:

```bash
source venv/bin/activate
python3 scraper_evangelio.py
```

### Actualización automática

Para actualizar el evangelio automáticamente cada día, puedes configurar un cron job:

```bash
# Editar crontab
crontab -e

# Agregar esta línea para actualizar a las 6:00 AM cada día
0 6 * * * cd /home/vanafa/Documents/Calendario\ de\ santos && ./actualizar_evangelio.sh >> evangelio_cron.log 2>&1
```

## 📋 Estructura de datos

El scraper genera un archivo `evangelio_hoy.json` con la siguiente estructura:

```json
{
  "fecha": "05 de noviembre de 2025",
  "fecha_publicacion": "Tue, 05 Nov 2025 00:00:00 GMT",
  "timestamp": "2025-11-05T15:48:55.804460",
  "titulo": "Evangelio y palabra del día 05 noviembre 2025",
  "lectura": {
    "tipo": "lectura",
    "referencia": "Lectura de la carta del apóstol san Pablo...",
    "titulo": "",
    "texto": "Contenido de la primera lectura..."
  },
  "salmo": {
    "tipo": "salmo",
    "referencia": "Salmo...",
    "titulo": "",
    "texto": "Contenido del salmo..."
  },
  "evangelio": {
    "tipo": "evangelio",
    "referencia": "Lectura del santo evangelio según...",
    "titulo": "",
    "texto": "Contenido del evangelio..."
  },
  "exito": true
}
```

## 🌐 Fuente

Los datos se obtienen del feed RSS oficial de Vatican News:
https://www.vaticannews.va/content/vaticannews/es/evangelio-de-hoy.rss.xml

## 🔧 Dependencias

- Python 3.x
- requests
- beautifulsoup4

Todas las dependencias están en el archivo `requirements.txt`.

## 📱 Integración con la web

La página `cita-biblica.html` carga automáticamente los datos desde `evangelio_hoy.json` y muestra:

- Primera Lectura (si está disponible)
- Salmo Responsorial (si está disponible)
- Evangelio del día (siempre presente)

### 🆕 Nuevas funcionalidades (Nov 2025):

✅ **Detección automática de fecha**: La página verifica si el evangelio es del día actual
✅ **Advertencia de actualización**: Muestra una alerta si los datos no son de hoy
✅ **Cache-busting**: Evita que el navegador use datos viejos en cache
✅ **Botón de actualización**: Guía al usuario si necesita actualizar los datos

## ⏰ Actualización Automática Recomendada

### GitHub Actions (RECOMENDADO para GitHub Pages)

Crea el archivo `.github/workflows/update-evangelio.yml`:

```yaml
name: Actualizar Evangelio del Día

on:
  schedule:
    # Ejecutar diariamente a las 6:00 AM UTC
    - cron: '0 6 * * *'
  workflow_dispatch: # Permite ejecución manual

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout código
      uses: actions/checkout@v3
      
    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
        
    - name: Instalar dependencias
      run: |
        pip install requests beautifulsoup4
        
    - name: Actualizar evangelio
      run: |
        python3 scraper_evangelio.py
        
    - name: Commit y Push si hay cambios
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add evangelio_hoy.json
        git diff --quiet && git diff --staged --quiet || (git commit -m "🔄 Actualizar evangelio del día [$(date +'%Y-%m-%d')]" && git push)
```

Esto actualizará el evangelio automáticamente cada día cuando esté en GitHub Pages.
