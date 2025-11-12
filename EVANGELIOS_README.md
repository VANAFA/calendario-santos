# 📖 Calendario de Santos - Sistema de Evangelios

## ¿Cómo funciona?

Este sistema descarga evangelios automáticamente desde **Vatican News** y los almacena en un CSV para que puedas **seleccionar cualquier fecha** y ver su evangelio.

## 🚀 Uso Rápido

### Actualizar evangelios disponibles

```bash
# Desde la raíz del proyecto
python3 scripts/scraper_evangelios_masivo.py
```

Este scraper descarga **todos los evangelios disponibles** en Vatican News (últimos ~15 días) y los agrega al CSV.

### O usar el menú principal

```bash
python3 main.py
```

Selecciona la opción **2** para actualizar evangelios masivamente.

## 📅 Limitación de Vatican News

Vatican News RSS solo tiene evangelios de los **últimos 15 días aproximadamente**. Por eso:

1. **Debes ejecutar el scraper diariamente** para ir acumulando evangelios
2. Con el tiempo tendrás una base de datos completa
3. Los evangelios nuevos se agregan automáticamente

## ⚙️ Configuración de Cron Job (Actualización Automática)

Para que los evangelios se actualicen solos cada día:

```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecuta todos los días a las 6:00 AM):
0 6 * * * cd /home/vanafa/Documents/Calendario\ de\ santos && source venv/bin/activate && python3 scripts/scraper_evangelios_masivo.py >> logs/evangelios.log 2>&1
```

## 📂 Archivos Importantes

- **`data/evangelios.csv`** - Base de datos de evangelios
- **`data/evangelio_hoy.json`** - Evangelio del día actual (generado por `main.py --evangelio`)
- **`scripts/scraper_evangelios_masivo.py`** - Descarga todos los evangelios disponibles
- **`scripts/scraper_evangelio.py`** - Descarga solo el evangelio de hoy
- **`cita-biblica.html`** - Página web con selector de fechas

## 🌐 Visualización

Abre `cita-biblica.html` en tu navegador y podrás:

- Ver el evangelio del día
- Seleccionar cualquier fecha con el calendario
- Navegar entre días con botones ⬅️ Anterior / ➡️ Siguiente
- Volver a hoy con 📅 Hoy

## 🔄 Alternativas para Evangelios Históricos

Vatican News solo tiene los últimos días. Si necesitas evangelios de fechas pasadas, tienes estas opciones:

### Opción 1: Esperar y acumular (Recomendado)
Ejecuta el scraper diariamente y en unos meses tendrás todo el año.

### Opción 2: Otras fuentes (No probadas aún)
- **Aciprensa**: `scripts/scraper_evangelios_aciprensa.py`
- **USCCB**: `scripts/scraper_evangelios_usccb.py`
- **Evangelizo.org**: `scripts/scraper_evangelios_evangelizo.py`

Estos scrapers están creados pero pueden necesitar ajustes según la estructura HTML de cada sitio.

## 📊 Verificar Estado Actual

```bash
# Ver cuántos evangelios tienes
python3 << 'EOF'
import csv

with open('data/evangelios.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    total = 0
    con_contenido = 0
    
    for row in reader:
        total += 1
        ev = row.get('evangelio_texto', '').strip()
        if ev and len(ev) > 100:
            con_contenido += 1
            print(f"✅ {row['dia']}/{row['mes']}/{row['año']}")
    
    print(f"\nTotal: {con_contenido}/{total} evangelios con contenido completo")
EOF
```

## 🛠️ Desarrollo

### Estructura del CSV

```csv
año,mes,dia,titulo,primera_lectura_ref,primera_lectura_texto,salmo_ref,salmo_texto,evangelio_ref,evangelio_texto
2025,11,12,"Evangelio del día 12/11/2025","Lectura del libro...","En aquel tiempo...","Salmo 23","El Señor es mi pastor...","Evangelio según san Lucas","Jesús..."
```

### Agregar más fuentes

Si encuentras otra fuente confiable con evangelios:

1. Crea un nuevo scraper en `scripts/scraper_evangelios_NOMBRE.py`
2. Sigue el mismo formato de salida que los otros scrapers
3. Usa la misma estructura de CSV

## 📝 Notas

- El selector de fechas muestra **fechas futuras vacías** (normal, aún no existen)
- Vatican News publica el evangelio cada día a las ~00:00 hora de Roma
- Si ves un error 404, significa que esa fecha no está disponible en la fuente

## 🐛 Problemas Comunes

### "El evangelio aparece vacío"
- Refresca la página (Ctrl + Shift + R)
- Verifica que el CSV tiene contenido: `head -20 data/evangelios.csv`
- Ejecuta el scraper masivo de nuevo

### "No se descargan evangelios antiguos"
- Vatican News solo tiene los últimos ~15 días
- Debes ejecutar diariamente para acumular

### "Fecha futura sin evangelio"
- Normal, esas fechas aún no han sido publicadas
- Se cargarán cuando llegue la fecha

## 📞 Ayuda

Si necesitas ayuda o encuentras un bug, revisa:
1. Los logs de ejecución del scraper
2. El contenido del CSV: `cat data/evangelios.csv | grep "2025,11,12"`
3. La consola del navegador (F12) para errores de JavaScript
