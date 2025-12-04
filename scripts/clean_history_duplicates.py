"""
Script para limpiar entradas duplicadas en customer_history.md.
Mantiene solo la entrada más reciente (con el estado más avanzado) para cada cliente/obra.
"""

import re
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    """Convierte una fecha en formato 'DD/MM/YYYY HH:MM' a objeto datetime."""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
    except:
        return datetime.min

def extract_entries(content):
    """Extrae todas las entradas del historial."""
    # Patrón para encontrar cada entrada completa
    pattern = r'## (.+?) - (.+?) \((.+?)\)\s*\n\s*\*\*Cliente:\*\* (.+?)\s*\n\s*\*\*NIF/CIF:\*\* (.+?)\s*\n\s*\*\*Email:\*\* (.+?)\s*\n\s*\*\*Dirección:\*\* (.+?)\s*\n\s*\*\*Detalles del trabajo:\*\*\s*\n\s*- Área: (.+?) m²\s*\n\s*- Tipo de trabajo: (.+?)\s*\n\s*- Tipo de pintura: (.+?)\s*\n\s*- Zona: (.+?)\s*\n\s*\*\*Total con IVA:\*\* €(.+?)\s*\n\s*\*\*Estado actual:\*\* (.+?)\s*\n\s*---'
    
    matches = re.finditer(pattern, content, re.DOTALL)
    entries = []
    
    for match in matches:
        entry = {
            'estado': match.group(1),
            'nombre': match.group(2),
            'fecha_str': match.group(3),
            'fecha': parse_date(match.group(3)),
            'cliente': match.group(4),
            'nif': match.group(5),
            'email': match.group(6),
            'direccion': match.group(7),
            'area': match.group(8),
            'tipo_trabajo': match.group(9),
            'tipo_pintura': match.group(10),
            'zona': match.group(11),
            'total': match.group(12),
            'estado_actual': match.group(13),
            'texto_completo': match.group(0)
        }
        entries.append(entry)
    
    return entries

def create_unique_key(entry):
    """Crea una clave única para identificar la misma obra."""
    return f"{entry['nif']}|{entry['area']}|{entry['tipo_trabajo']}|{entry['tipo_pintura']}|{entry['zona']}"

def clean_duplicates(file_path="data/customer_history.md"):
    """Limpia entradas duplicadas manteniendo solo la más reciente."""
    
    print("=" * 70)
    print("LIMPIEZA DE ENTRADAS DUPLICADAS EN HISTORIAL DE CLIENTES")
    print("=" * 70)
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer todas las entradas
    entries = extract_entries(content)
    print(f"\n📊 Total de entradas encontradas: {len(entries)}")
    
    # Agrupar por clave única
    grouped = defaultdict(list)
    for entry in entries:
        key = create_unique_key(entry)
        grouped[key].append(entry)
    
    # Encontrar duplicados
    duplicates_found = sum(1 for entries_list in grouped.values() if len(entries_list) > 1)
    print(f"🔍 Obras con entradas duplicadas: {duplicates_found}")
    
    if duplicates_found == 0:
        print("\n✅ No se encontraron duplicados. El historial está limpio.")
        return
    
    # Para cada grupo, mantener solo la entrada más reciente
    unique_entries = []
    estados_prioridad = {
        'Factura Pagada': 3,
        'Facturado y Pendiente de Pago': 2,
        'Presupuestado': 1
    }
    
    print("\n📋 Procesando duplicados:")
    for key, entries_list in grouped.items():
        if len(entries_list) > 1:
            print(f"\n   Cliente: {entries_list[0]['nombre']} - {entries_list[0]['tipo_trabajo']}")
            print(f"   Encontradas {len(entries_list)} entradas:")
            
            for entry in entries_list:
                print(f"      - {entry['estado']} ({entry['fecha_str']})")
            
            # Ordenar por fecha (más reciente primero) y por prioridad de estado
            entries_list.sort(
                key=lambda e: (
                    e['fecha'],
                    estados_prioridad.get(e['estado_actual'], 0)
                ),
                reverse=True
            )
            
            # Mantener solo la primera (más reciente)
            unique_entries.append(entries_list[0])
            print(f"   ✅ Manteniendo: {entries_list[0]['estado']} ({entries_list[0]['fecha_str']})")
        else:
            unique_entries.append(entries_list[0])
    
    # Reconstruir el archivo
    new_content = "\n"
    for entry in unique_entries:
        new_content += entry['texto_completo'] + "\n"
    
    # Guardar el archivo limpio
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n" + "=" * 70)
    print(f"✅ LIMPIEZA COMPLETADA")
    print(f"   Entradas originales: {len(entries)}")
    print(f"   Entradas después de limpieza: {len(unique_entries)}")
    print(f"   Entradas eliminadas: {len(entries) - len(unique_entries)}")
    print("=" * 70)

if __name__ == "__main__":
    clean_duplicates()
