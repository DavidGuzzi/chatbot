#!/usr/bin/env python3
"""
Script para generar tabla maestro de tiendas
"""

import csv
import random

def generate_maestro_tiendas():
    # Leer IDs únicos de tiendas del CSV existente
    unique_stores = set()
    with open('tiendas_detalle.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            unique_stores.add(row['tienda_id'])
    
    unique_stores = sorted(list(unique_stores))
    
    # Nombres aleatorios para tiendas
    nombres_tiendas = [
        'Plaza Central', 'Mall Norte', 'Centro Comercial Sur', 'Tienda Principal',
        'Galería Este', 'Megastore Oeste', 'Local Premium', 'Shopping Boulevard',
        'Centro Urbano', 'Plaza Mayor', 'Mall Ejecutivo', 'Tienda Express',
        'Galería Moderna', 'Centro Elite', 'Plaza VIP', 'Mall Excellence',
        'Tienda Flagship', 'Centro Premium', 'Plaza Business', 'Mall Innovation'
    ]
    
    # Generar datos del maestro
    random.seed(42)  # Para reproducibilidad
    
    with open('maestro_tiendas.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['tienda_id', 'nombre_tienda', 'fecha_apertura', 'gerente'])
        
        # Datos
        for i, store_id in enumerate(unique_stores):
            # Nombre consistente pero único
            nombre_idx = i % len(nombres_tiendas)
            nombre = f'{nombres_tiendas[nombre_idx]} {store_id[-3:]}'
            
            # Fecha aleatoria en 2020
            mes = random.randint(1, 12)
            dia = random.randint(1, 28)
            fecha = f'2020-{mes:02d}-{dia:02d}'
            
            # Gerente aleatorio
            gerente = f'Gerente_{random.randint(1000, 9999)}'
            
            writer.writerow([store_id, nombre, fecha, gerente])
    
    print(f'✅ Generado maestro_tiendas.csv con {len(unique_stores)} tiendas')
    
    # Mostrar primeras 5 filas
    print('\nPrimeras 5 filas:')
    with open('maestro_tiendas.csv', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:6]):  # Header + 5 filas
            print(f"{i}: {line.strip()}")

if __name__ == "__main__":
    generate_maestro_tiendas()