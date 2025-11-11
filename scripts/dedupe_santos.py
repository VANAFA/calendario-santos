#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elimina filas duplicadas en santos.csv manteniendo la primera aparición.
Clave: mes-dia-nombre
"""
import csv
import os
from collections import OrderedDict

# Rutas relativas al directorio raíz del proyecto
directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(directorio_base, "data", "santos.csv")
backup_path = os.path.join(directorio_base, "backups", "santos.csv.bak")

rows = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for r in reader:
        if not any(cell.strip() for cell in r):
            continue
        rows.append(r)

seen = set()
unique = []
for r in rows:
    # Asegurar que hay al menos 3 columnas
    if len(r) < 3:
        continue
    try:
        mes = r[0].strip()
        dia = r[1].strip()
        nombre = r[2].strip()
    except Exception:
        continue
    key = f"{mes}-{dia}-{nombre}"
    if key in seen:
        continue
    seen.add(key)
    unique.append(r)

# Hacer backup
import shutil
shutil.copyfile(csv_path, backup_path)

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for r in unique:
        writer.writerow(r)

print(f"Hecho. {len(rows)} filas leídas, {len(unique)} filas únicas escritas. Backup en {backup_path}.")
