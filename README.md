# Calendario de Santos �️✨

Sitio web que muestra el santoral católico diario con información de santos desde Wikipedia y el evangelio del día.

## 📁 Estructura del Proyecto

```
calendario-santos/
├── main.py                    # Script principal de ejecución
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
│
├── scripts/                   # Scripts Python
│   ├── scraper_santos_wikipedia.py    # Scraper de santos
│   ├── scraper_evangelio.py           # Scraper de evangelio
│   ├── migrar_csv_etiquetas.py        # Migración de CSV
│   └── dedupe_santos.py               # Eliminar duplicados
│
├── web/                       # Archivos del sitio web
│   ├── index.html            # Página principal
│   ├── cita-biblica.html     # Página del evangelio
│   └── images/               # Imágenes de santos
│
├── data/                      # Archivos de datos
│   ├── santos.csv            # Base de datos de santos
│   ├── evangelio_hoy.json    # Evangelio del día
│   └── wikiproblematica.csv  # Días problemáticos
│
├── backups/                   # Backups automáticos
│   └── *.backup, *.bak       # Copias de seguridad
│
└── docs/                      # Documentación
    ├── ETIQUETAS_IMPLEMENTATION.md
    ├── GUIA_ACTUALIZACION.md
    └── ...
```

## 🚀 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/VANAFA/calendario-santos.git
cd calendario-santos
```

2. **Crear entorno virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

## 🎯 Uso del Sistema

### Modo Interactivo (Recomendado)

Ejecuta el script principal:
```bash
python3 main.py
```

Verás un menú con opciones:
1. Actualizar Evangelio del día
2. Actualizar Santos (todo el año)
3. Actualizar Santos (un día específico)
4. Actualizar todo
5. Salir

### Modo Línea de Comandos

```bash
# Actualizar solo evangelio
python3 main.py --evangelio

# Actualizar todos los santos (toma varias horas)
python3 main.py --santos

# Actualizar un día específico
python3 main.py --santos-dia 11 11  # 11 de noviembre

# Ver ayuda
python3 main.py --help
```

## � GitHub Pages

El sitio está configurado para desplegarse en GitHub Pages automáticamente.

### Estructura para GitHub Pages

Los archivos HTML se encuentran en la **raíz** del proyecto para que GitHub Pages pueda servirlos:
- `index.html` - Página principal (copia de `web/index.html`)
- `cita-biblica.html` - Página del evangelio (copia de `web/cita-biblica.html`)
- `images/` - Symlink a `web/images/`

### Sincronizar Cambios Web

Cuando modifiques archivos en `web/`, sincronízalos a la raíz:

```bash
./sync-web.sh
```

O manualmente:
```bash
cp web/index.html .
cp web/cita-biblica.html .
```

### Configuración de GitHub Pages

1. Ve a **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** → **/ (root)**
4. Save

Tu sitio estará en: `https://vanafa.github.io/calendario-santos/`

## �🏷️ Sistema de Etiquetas

Los santos pueden tener etiquetas especiales que afectan su prioridad:

| Etiqueta | Prioridad | Descripción |
|----------|-----------|-------------|
| `festividad` | 100 | Festividades litúrgicas importantes (Navidad, etc.) |
| `santo_argentino` | 80 | Santos argentinos o patronos de Argentina |
| `santo_scout` | 70 | Santos patronos del escultismo |
| (sin etiqueta) | 50 | Santos normales |

### Ejemplos de Santos con Etiquetas

- **San Martín de Tours** (11/11): `santo_argentino` - Patrono de Buenos Aires
- **San Jorge** (23/4): `santo_scout` - Patrono del escultismo mundial
- **Navidad** (25/12): `festividad` - Solemnidad

## 🚀 Cómo usar

### Ver la página web localmente

**IMPORTANTE**: La página necesita un servidor HTTP para cargar el CSV correctamente.

```bash
# 1. Ir al directorio del proyecto
cd "/home/vanafa/Documents/Calendario de santos"

# 2. Iniciar servidor HTTP local
python3 -m http.server 8000

# 3. Abrir en navegador
xdg-open http://localhost:8000/index.html
# O manualmente ir a: http://localhost:8000/index.html
```

### Poblar/actualizar datos con el scraper

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Ejecutar scraper
python3 scraper_santos.py

# 3. Elegir opción:
#    1 = Todo el año (1-2 horas) ⭐ RECOMENDADO
#    2 = Un mes específico (10-15 min)
#    3 = Rango de fechas personalizado
```

**Características del scraper optimizado:**
- ✅ **Incremental**: Salta santos ya existentes automáticamente
- ✅ **Seguro**: Puedes interrumpir (Ctrl+C) y reiniciar sin perder progreso
- ✅ **Rápido**: 2x más rápido con delays reducidos y conexiones reutilizables
- ✅ **Completo**: Extrae nombre, descripción, imagen, oración, links Wikipedia/Vatican

## 📁 Estructura del proyecto

```

## ✨ Características

- 🗓️ **Selector de fecha sin año**: Elige mes y día para ver los santos de cualquier fecha
- � **Múltiples santos por día**: Muestra todos los santos celebrados en una fecha
- 📖 **Descripción completa**: Resumen de la vida y obra del santo (Wikipedia)
- 🖼️ **Imágenes**: Fotos de los santos (local → Wikipedia → placeholder)
- 🔗 **Enlaces**: Links directos a Wikipedia y Vatican News
- 🙏 **Oraciones**: Oraciones asociadas a cada santo (cuando disponible)
- 📱 **Responsive**: Se adapta a móviles, tablets y desktop
- 🎨 **Interfaz moderna**: Diseño limpio con gradientes y tarjetas

## 📊 Estado actual

- ✅ Frontend funcionando correctamente
- ✅ CSV con ~1000+ santos (principalmente noviembre)
- ✅ Scraper optimizado y listo para uso
- ⏳ Pendiente: Completar todo el año (ejecutar scraper opción 1)

## 🔧 Tecnologías

- **Frontend**: HTML5, CSS3, JavaScript Vanilla
- **Backend/Scraper**: Python 3 (BeautifulSoup, Requests)
- **Datos**: CSV local (generado por scraper automático)
- **Fuentes**: calendariodesantos.com + Wikipedia API
- **Hosting**: GitHub Pages (configurado en repo)

## Cómo Publicar en GitHub Pages

### Paso 1: Crear un Repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón "+" en la esquina superior derecha y selecciona "New repository"
3. Nombra tu repositorio (por ejemplo: "calendario-santos")
4. Marca la casilla "Public"
5. Haz clic en "Create repository"

### Paso 2: Subir los Archivos

Opción A - Usando Git (recomendado):

```bash
cd "/home/vanafa/Documents/Calendario de santos"
git init
git add .
git commit -m "Primera versión del calendario de santos"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/calendario-santos.git
git push -u origin main
```

Opción B - Usando la interfaz web de GitHub:

1. En tu repositorio, haz clic en "uploading an existing file"
2. Arrastra el archivo `index.html` a la página
3. Haz clic en "Commit changes"

### Paso 3: Activar GitHub Pages

1. En tu repositorio, ve a "Settings" (Configuración)
2. En el menú lateral, haz clic en "Pages"
3. En "Source" (Fuente), selecciona la rama "main" y la carpeta "/ (root)"
4. Haz clic en "Save" (Guardar)
5. Espera unos minutos y tu sitio estará disponible en: `https://TU_USUARIO.github.io/calendario-santos/`

## Fuentes de Datos

La página intenta obtener información de:

1. **API de Religion.ar**: API pública con información de santos católicos
2. **Wikipedia API**: Como fuente alternativa para obtener información actualizada
3. **Calendario predefinido**: Fallback con santos populares si las APIs no están disponibles

## Personalización

Puedes personalizar:

- **Colores**: Modifica los valores en la sección `<style>` del archivo HTML
- **Fuentes**: Cambia `font-family` en el CSS
- **Tamaño de texto**: Ajusta los valores `font-size`

## Tecnologías Utilizadas

- HTML5
- CSS3 (con gradientes y animaciones)
- JavaScript (Vanilla JS)
- APIs públicas (Wikipedia y Religion.ar)

## Alternativas de Hosting Gratuito

Si no quieres usar GitHub Pages, también puedes usar:

- **Netlify**: [netlify.com](https://www.netlify.com) - Arrastra y suelta tu carpeta
- **Vercel**: [vercel.com](https://vercel.com) - Similar a Netlify
- **Cloudflare Pages**: [pages.cloudflare.com](https://pages.cloudflare.com)
- **Render**: [render.com](https://render.com)

## Licencia

Libre uso para proyectos personales y educativos.
