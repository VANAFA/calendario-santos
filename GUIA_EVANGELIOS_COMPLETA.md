# 🎯 GUÍA COMPLETA: Sistema de Evangelios con Selector de Fechas

## ✅ ¿Qué tienes ahora?

1. **📅 Selector de fechas completo** - Puedes elegir CUALQUIER día/mes/año
2. **📊 Base de datos de 365 días** - Todos los días del 2025 están en el CSV
3. **✅ 10 evangelios con contenido** - Del 3 al 13 de noviembre 2025
4. **📭 355 espacios vacíos (placeholders)** - Listos para ser llenados

## 🔄 Cómo funciona el sistema

### 1. Estructura del CSV

```csv
año,mes,dia,titulo,primera_lectura_ref,primera_lectura_texto,salmo_ref,salmo_texto,evangelio_ref,evangelio_texto
2025,11,13,"Evangelio del 13/11/2025","Sabiduría...","En aquel tiempo...","Salmo 23...","..."","Lucas 17...","Jesús..."
2025,11,14,"Evangelio del 14/11/2025","","","","","",""  ← VACÍO (placeholder)
```

### 2. Flujo de datos

```
Vatican News RSS (últimos ~15 días)
    ↓
scraper_evangelios_masivo.py
    ↓
data/evangelios.csv (365 días)
    ↓
cita-biblica.html (web interface)
    ↓
Usuario selecciona fecha
```

## 🚀 Comandos Principales

### Actualizar evangelios disponibles

```bash
# Descarga todos los evangelios disponibles en Vatican News (últimos 15 días)
python3 scripts/scraper_evangelios_masivo.py
```

### Crear estructura para un año completo

```bash
# Crea placeholders para todos los días del año
python3 scripts/crear_estructura_año.py 2026
```

### Menú interactivo

```bash
python3 main.py
# Opción 1: Evangelio del día (solo hoy)
# Opción 2: Todos los evangelios disponibles (últimos 15 días)
```

## 📈 Estrategia de Llenado

### Opción A: Acumulación Gradual (Recomendado ⭐)

**Configura un cron job para ejecutar diariamente:**

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta todos los días a las 6:00 AM):
0 6 * * * cd "/home/vanafa/Documents/Calendario de santos" && source venv/bin/activate && python3 scripts/scraper_evangelios_masivo.py >> logs/evangelios.log 2>&1
```

**Resultado:**
- Día 1: Tienes los últimos 15 días
- Mes 1: Tienes ~30 días
- Mes 3: Tienes ~90 días
- Año 1: Tienes los 365 días completos! 🎉

### Opción B: Carga Manual Periódica

```bash
# Ejecuta manualmente cada semana
python3 scripts/scraper_evangelios_masivo.py
```

## 🌐 Uso de la Interfaz Web

### Abrir en navegador

```bash
# Opción 1: Desde raíz
firefox cita-biblica.html

# Opción 2: Desde carpeta web
firefox web/cita-biblica.html
```

### Funciones disponibles

- **📅 Selector de fecha**: Click para abrir calendario
- **⬅️ Anterior**: Retrocede un día
- **➡️ Siguiente**: Avanza un día  
- **📅 Hoy**: Vuelve a la fecha actual

### Mensajes que verás

#### ✅ Evangelio con contenido
```
✝️ Evangelio del día 13 de noviembre de 2025
📜 Primera Lectura: [referencia]
[texto completo]
...
```

#### 📅 Fecha futura (sin contenido)
```
📅 Fecha Futura
ℹ️ El evangelio del [fecha] aún no está disponible.
Los evangelios se publican día a día...
```

#### 📜 Fecha pasada (placeholder vacío)
```
📜 Evangelio Histórico
El evangelio del [fecha] no ha sido cargado todavía.
📊 Estado actual: 10/365 evangelios cargados (2.7%)

💡 Cómo obtenerlo:
• Vatican News solo tiene los últimos ~15 días
• Ejecuta el scraper diariamente...
```

## 📊 Verificar Estado

### Ver estadísticas

```bash
python3 << 'EOF'
import csv

with open('data/evangelios.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    total = 0
    con_contenido = 0
    
    for row in reader:
        total += 1
        if row.get('evangelio_texto', '').strip() and len(row['evangelio_texto']) > 100:
            con_contenido += 1
    
    print(f"Total: {con_contenido}/{total} evangelios ({con_contenido/total*100:.1f}%)")
EOF
```

### Ver últimos evangelios cargados

```bash
head -15 data/evangelios.csv | tail -10 | cut -d',' -f1-4
```

## 🔧 Mantenimiento

### Backup del CSV

```bash
# Crear backup antes de cambios importantes
cp data/evangelios.csv data/evangelios_backup_$(date +%Y%m%d).csv
```

### Limpiar y reconstruir

```bash
# 1. Backup del CSV actual
cp data/evangelios.csv data/evangelios_backup.csv

# 2. Crear estructura nueva
python3 scripts/crear_estructura_año.py 2025

# 3. Actualizar con datos disponibles
python3 scripts/scraper_evangelios_masivo.py

# 4. Si algo salió mal, restaurar
# cp data/evangelios_backup.csv data/evangelios.csv
```

## 🐛 Solución de Problemas

### "No se carga ningún evangelio"

```bash
# 1. Verificar que el CSV existe
ls -lh data/evangelios.csv

# 2. Ver primeras líneas del CSV
head -5 data/evangelios.csv

# 3. Verificar permisos
chmod 644 data/evangelios.csv

# 4. Recargar página con Ctrl+Shift+R (vaciar caché)
```

### "Todos los evangelios aparecen vacíos"

```bash
# Actualizar desde Vatican News
python3 scripts/scraper_evangelios_masivo.py

# Verificar que se agregaron
python3 -c "import csv; print(sum(1 for r in csv.DictReader(open('data/evangelios.csv')) if len(r.get('evangelio_texto',''))>100))"
```

### "Error al cargar CSV en el navegador"

- Abre la consola del navegador (F12)
- Busca errores en la pestaña "Console"
- Verifica que la ruta del CSV sea correcta:
  - Raíz: `fetch('data/evangelios.csv')`
  - Web: `fetch('../data/evangelios.csv')`

## 📝 Próximos Pasos

### Para 2026

```bash
# Crear estructura para 2026
python3 scripts/crear_estructura_año.py 2026

# Resultado: Tendrás 365 días de 2025 + 365 días de 2026 = 730 días
```

### Para años anteriores (2024, 2023...)

Vatican News no tiene evangelios históricos, pero puedes:

1. **Opción A**: Dejar placeholders vacíos
2. **Opción B**: Buscar otra fuente (Aciprensa, USCCB, etc.)
3. **Opción C**: Cargar manualmente desde un leccionario PDF

## 🎓 Resumen Ejecutivo

**Para el usuario final:**
- ✅ Puede elegir CUALQUIER fecha (1 ene - 31 dic)
- ✅ Si tiene contenido, lo verá inmediatamente
- ✅ Si está vacío, verá mensaje explicativo

**Para ti (mantenimiento):**
- ✅ Ejecuta `scraper_evangelios_masivo.py` diariamente (manual o cron)
- ✅ Los espacios vacíos se llenan automáticamente
- ✅ En 1 año tendrás base de datos completa

**Estado actual:**
- 📊 10/365 evangelios (2.7%)
- 📅 Rango: 3-13 noviembre 2025
- 🎯 Meta: 365/365 (100%) en ~12 meses

## 🎉 ¡Listo!

Tu sistema ya está funcionando. El usuario puede:
1. Abrir `cita-biblica.html`
2. Seleccionar CUALQUIER fecha
3. Ver el evangelio (si está disponible) o mensaje informativo (si no lo está)

Los evangelios se irán llenando automáticamente día a día! 📖✨
