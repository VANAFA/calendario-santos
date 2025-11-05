# 🕊️ Script Automatizado para Obtener Santos

Este script descarga automáticamente toda la información de los santos del año.

## 📋 Requisitos

- Python 3.6 o superior
- pip (gestor de paquetes de Python)

## ⚙️ Instalación

### 1. Instalar dependencias

```bash
cd "/home/vanafa/Documents/Calendario de santos"
pip3 install -r requirements.txt
```

O instala manualmente:

```bash
pip3 install beautifulsoup4 requests
```

## 🚀 Uso

### Ejecutar el script:

```bash
python3 scraper_santos.py
```

### Opciones disponibles:

**Opción 1: TODO el año (365 días)**
- Procesa todos los días del calendario
- Tiempo estimado: 2-3 horas
- Recomendado: ejecutar de noche

**Opción 2: Un mes específico**
- Procesa solo un mes (ej: Enero)
- Tiempo estimado: 15-20 minutos

**Opción 3: Rango de fechas**
- Procesa desde una fecha hasta otra
- Útil para actualizar días específicos

**Opción 4: Desde hoy hasta fin de año**
- Procesa desde el día actual hasta el 31 de diciembre
- Útil para ir actualizando progresivamente

## 📊 Qué hace el script:

1. ✅ Accede a calendariodesantos.com día por día
2. ✅ Extrae los nombres de los santos
3. ✅ Busca cada santo en Wikipedia
4. ✅ Obtiene el resumen/descripción
5. ✅ Descarga la imagen del santo
6. ✅ Intenta extraer oraciones
7. ✅ Genera el archivo `santos.csv` actualizado
8. ✅ Guarda las imágenes en la carpeta `images/`

## 📁 Archivos generados:

- `santos.csv` - Base de datos completa
- `images/` - Carpeta con todas las imágenes descargadas

## ⚠️ Consideraciones:

- **Tiempo**: El proceso completo puede tardar 2-3 horas para los 365 días
- **Internet**: Necesitas conexión estable a internet
- **Paciencia**: El script hace pausas para no saturar los servidores
- **Errores**: Algunos santos pueden no tener información en Wikipedia

## 💡 Tips:

### Para ejecutar en segundo plano:

```bash
nohup python3 scraper_santos.py > scraper.log 2>&1 &
```

Luego puedes ver el progreso con:

```bash
tail -f scraper.log
```

### Para procesar solo un mes (más rápido para probar):

```bash
python3 scraper_santos.py
# Selecciona opción 2
# Ingresa mes: 1 (para enero)
```

### Para continuar si se interrumpe:

El script no elimina datos previos, así que si tienes que detenerlo:
1. Nota hasta qué fecha llegó
2. Vuelve a ejecutarlo
3. Usa opción 3 (rango de fechas)
4. Empieza desde donde se detuvo

## 🔧 Solución de problemas:

**Error: "ModuleNotFoundError: No module named 'bs4'"**
```bash
pip3 install beautifulsoup4
```

**Error: "ModuleNotFoundError: No module named 'requests'"**
```bash
pip3 install requests
```

**Error: "Permission denied"**
```bash
chmod +x scraper_santos.py
```

**El script no encuentra santos en calendariodesantos.com**
- El sitio puede haber cambiado su estructura
- Revisa manualmente la página web
- Ajusta los selectores CSS en el script si es necesario

## 📝 Ejemplo de ejecución:

```bash
$ python3 scraper_santos.py

============================================================
   SCRAPER DE CALENDARIO DE SANTOS
============================================================

Opciones:
1. Procesar TODO el año (365 días)
2. Procesar un mes específico
3. Procesar un rango de fechas
4. Procesar desde hoy hasta fin de año

Selecciona una opción (1-4): 2
Mes (1-12): 1

🕊️  Iniciando scraper de santos...
📅 Procesando desde 1/1 hasta 1/31

📆 Mes 01
  Obteniendo santos para 01/01...
    Procesando: Santa María, Madre de Dios
    ✅ Imagen descargada: maria_madre_dios.jpg
    Procesando: San Basilio el Grande
    ✅ Imagen descargada: basilio_grande.jpg
...
✅ CSV generado: santos.csv
✅ Total de santos: 47

🎉 ¡Listo! Ya puedes usar el nuevo santos.csv en tu página web.
```

## 🎯 Después de ejecutar:

1. Verifica que `santos.csv` tenga los datos
2. Revisa la carpeta `images/` con las imágenes
3. Actualiza el archivo `index.html` si es necesario
4. Sube los cambios a GitHub:

```bash
git add .
git commit -m "Actualizar calendario de santos"
git push origin main
```

## ⏱️ Tiempos estimados:

- 1 mes: ~15-20 minutos
- 3 meses: ~1 hora
- Todo el año: ~2-3 horas

## 🆘 Ayuda:

Si tienes problemas, verifica:
1. ¿Python 3 instalado? → `python3 --version`
2. ¿Dependencias instaladas? → `pip3 list | grep beautifulsoup`
3. ¿Conexión a internet? → `ping google.com`
4. ¿Permisos de escritura? → `ls -la`
