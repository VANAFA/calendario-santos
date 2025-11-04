# Santo del Día - Calendario de Santos

Una página web que muestra el santo del día con información actualizada de Wikipedia.

## Características

- ✨ Muestra la fecha actual en español
- 📅 Santo del día actualizado automáticamente
- 📖 Resumen del santo tomado de Wikipedia
- 🔗 Enlace directo a la página de Wikipedia del santo
- 📱 Diseño responsive (se adapta a móviles y tablets)
- 🎨 Interfaz moderna y atractiva

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
