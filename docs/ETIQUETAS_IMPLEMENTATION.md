# Sistema de Etiquetas Especiales para Santos
## Implementación completada ✅

### Características Agregadas

#### 1. **Etiquetas Especiales**
Se agregaron tres tipos de etiquetas:

- **`santo_argentino`**: Santos nacidos en Argentina o patronos de Argentina
  - Prioridad: **80**
  - Ejemplos: San Martín de Tours, Ceferino Namuncurá, José Gabriel Brochero
  - Fuente: Wikipedia - Anexo:Santos y beatos de Argentina

- **`festividad`**: Festividades litúrgicas importantes
  - Prioridad: **100** (máxima)
  - Ejemplos: Navidad (25/12), Inmaculada Concepción (8/12), Todos los Santos (1/11)
  - Incluye: Solemnidades y fiestas del calendario litúrgico

- **`santo_scout`**: Santos patronos del escultismo
  - Prioridad: **70**
  - Ejemplos: San Jorge (patrono mundial), San Pablo de la Cruz (scouts argentinos)

#### 2. **Nueva Columna en CSV**
Se agregó la columna `etiquetas` en `santos.csv`:
```
mes,dia,nombre,prioridad,descripcion,imagen,url_wikipedia,etiquetas,oracion
```

Las etiquetas se separan por comas si un santo tiene múltiples:
```
11,11,San Martín de Tours,80,"...",,"...",santo_argentino,
4,23,San Jorge,70,"...",,"...",santo_scout,
12,25,Natividad del Señor,100,"...",,"...",festividad,
```

#### 3. **Prioridades Automáticas**
El scraper ahora asigna prioridades automáticamente:
- Festividades: **100**
- Santos argentinos: **80**
- Santos scouts: **70**
- Santos normales: **50** (default)

#### 4. **Fuentes de Datos**

**Santos Argentinos:**
- URL: https://es.wikipedia.org/wiki/Anexo:Santos_y_beatos_de_Argentina
- Scrapea automáticamente la tabla de Wikipedia
- Total cargados: ~62 santos + 5 patronos

**Patronos Argentinos Especiales:**
Agregados manualmente por su importancia cultural:
- San Martín de Tours (Patrono de Buenos Aires)
- Nuestra Señora de Luján (Patrona de Argentina)
- San Cayetano (Gran devoción argentina)
- San Expedito (Devoción popular)
- Santa Rosa de Lima (Primera santa de América)

**Festividades Importantes:**
Lista hardcodeada de solemnidades:
- Navidad (25/12)
- Inmaculada Concepción (8/12)
- Asunción de María (15/8)
- Todos los Santos (1/11)
- San José (19/3)
- San Pedro y San Pablo (29/6)
- Santiago Apóstol (25/7)
- San Juan Bautista (24/6)

**Santos Scouts:**
Lista hardcodeada:
- San Jorge (Patrono del escultismo mundial)
- San Pablo de la Cruz (Patrono scouts argentinos)
- Madre María Ana Mogas (Patrono guías argentinas)

### Uso

#### Ejecutar el Scraper con Etiquetas
```bash
python3 scraper_santos_wikipedia.py
```

El scraper automáticamente:
1. Carga las etiquetas especiales de Wikipedia
2. Procesa cada santo del día
3. Detecta si tiene etiquetas especiales
4. Asigna prioridad según etiquetas
5. Guarda en CSV con campo `etiquetas`

#### Migrar CSV Existente
Si ya tienes un `santos.csv` sin la columna `etiquetas`:
```bash
python3 migrar_csv_etiquetas.py
```

Este script:
- Crea backup `santos_backup.csv`
- Agrega columna `etiquetas` vacía
- Reescribe el CSV con nuevo formato

### Ejemplos de Output

```
🏷️  Cargando etiquetas especiales desde Wikipedia...
  ✅ Cargados 62 santos argentinos
  ✅ Cargadas 8 festividades importantes
  ✅ Cargados 3 santos scouts
  ✅ Agregados 5 patronos/santos con devoción argentina

📅 Procesando 11/11...
  🔍 Procesando: San Martín de Tours
    ✅ Tiene Wikipedia: https://es.wikipedia.org/wiki/Mart%C3%ADn_de_Tours
    🏷️  Etiquetas: Santo Argentino | Prioridad: 80
    ✅ Completado
```

### Verificación

```bash
# Ver San Martín de Tours con etiquetas
grep "San Martín de Tours" santos.csv

# Resultado:
# 11,11,San Martín de Tours,80,"...",,"...",santo_argentino,

# Ver todos los santos argentinos
grep "santo_argentino" santos.csv | cut -d',' -f3

# Ver todas las festividades
grep "festividad" santos.csv | cut -d',' -f3

# Ver santos scouts
grep "santo_scout" santos.csv | cut -d',' -f3
```

### Próximos Pasos

1. **Ejecutar scraper completo** para todo el año:
   ```bash
   python3 scraper_santos_wikipedia.py
   ```

2. **Revisar frontend** para mostrar las etiquetas visualmente (badges, colores, etc.)

3. **Agregar más categorías** si es necesario:
   - Santos doctores de la Iglesia
   - Santos fundadores
   - Santos mártires
   - Santos carmelitas, dominicos, jesuitas, etc.

### Archivos Modificados

- ✅ `scraper_santos_wikipedia.py` - Lógica de etiquetas
- ✅ `migrar_csv_etiquetas.py` - Script de migración
- ✅ `santos.csv` - Ahora incluye columna `etiquetas`
- ✅ `santos_backup.csv` - Backup del CSV original
