# Guía para Actualizar el Calendario de Santos

Este archivo explica cómo mantener y actualizar el calendario de santos.

## 📋 Estructura del Proyecto

```
calendario-santos/
├── index.html          # Página principal
├── santos.csv          # Base de datos de santos
├── images/             # Carpeta de imágenes
│   ├── README.md
│   └── [imágenes de santos]
└── README.md
```

## 📝 Formato del Archivo CSV

El archivo `santos.csv` contiene toda la información de los santos con el siguiente formato:

```
mes,dia,nombre,descripcion,imagen,url_wikipedia,url_vatican
```

### Ejemplo:
```csv
1,23,Santa Emerenciana,Mártir romana...,santa_emerenciana.jpg,https://es.wikipedia.org/wiki/Emerenciana,https://www.vaticannews.va/es/santos/01/23.html
```

## 🔄 Cómo Agregar Nuevos Santos

### Opción 1: Manualmente

1. Abre `santos.csv` en un editor de texto
2. Agrega una nueva línea con el formato correcto
3. Si la descripción tiene comas, enciérrala entre comillas
4. Guarda el archivo

### Opción 2: Desde Vatican News

Visita: https://www.vaticannews.va/es/santos/MM/DD.html  
(Reemplaza MM con el mes y DD con el día, ej: 01/23 para 23 de enero)

Copia la información del santo y agrégala al CSV

## 🖼️ Agregar Imágenes

1. Descarga la imagen del santo desde:
   - Wikimedia Commons
   - Vatican News
   - Wikipedia

2. Guárdala en la carpeta `images/` con el nombre especificado en el CSV

3. Formatos recomendados: JPG, PNG
4. Tamaño recomendado: 300x300px o superior

## ✅ Verificar Cambios

1. Abre `index.html` en tu navegador
2. Usa el selector de fecha para probar el día agregado
3. Verifica que:
   - El nombre del santo aparezca correctamente
   - La descripción se vea bien
   - La imagen se cargue (si existe)
   - Los enlaces funcionen

## 🚀 Publicar Cambios en GitHub

```bash
cd "/home/vanafa/Documents/Calendario de santos"
git add .
git commit -m "Agregar santos del día X"
git push origin main
```

Los cambios aparecerán automáticamente en GitHub Pages en unos minutos.

## 🎯 Objetivo: Calendario Completo

Para tener un calendario completo del año, necesitas agregar datos para los 365 días.

**Progreso actual:** ~25 días cubiertos

### Estrategia sugerida:

1. **Ir a Vatican News** día por día
2. **Copiar la información** de cada santo
3. **Agregar al CSV** siguiendo el formato
4. **Descargar imágenes** opcionales
5. **Commit regular** cada 10-20 días agregados

## 📚 Recursos Útiles

- Vatican News Santos: https://www.vaticannews.va/es/santos.html
- Wikipedia Santoral: https://es.wikipedia.org/wiki/Santoral_católico
- Calendario de Santos: https://calendariodesantos.com

## ⚡ Tips

- Usa comillas dobles `"` para descripciones con comas
- Los nombres de imagen no deben tener espacios (usa guiones bajos)
- Mantén descripciones entre 200-400 caracteres
- Verifica que las URLs no tengan espacios
- Guarda el CSV con codificación UTF-8

## 🆘 Solución de Problemas

**Problema:** No aparece el santo del día  
**Solución:** Verifica que la fecha esté en formato M-D (sin ceros iniciales)

**Problema:** La imagen no se carga  
**Solución:** Verifica que el nombre del archivo coincida exactamente con el CSV

**Problema:** La descripción se corta  
**Solución:** Asegúrate de encerrar textos con comas entre comillas

**Problema:** Caracteres extraños (á, é, í, ñ)  
**Solución:** Guarda el CSV con codificación UTF-8
