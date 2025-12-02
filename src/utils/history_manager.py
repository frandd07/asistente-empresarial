from datetime import datetime
import os

def guardar_presupuesto_en_historial(presupuesto_dict: dict, archivo_path: str = "data/customer_history.md") -> dict:
    """
    Guarda un presupuesto o factura desde un diccionario a un archivo markdown de historial.
    
    Args:
        presupuesto_dict: Diccionario con los datos del presupuesto/factura, incluyendo un campo 'estado' opcional.
        archivo_path: Ruta al archivo de historial.
        
    Returns:
        Un diccionario indicando el resultado de la operación.
    """
    try:
        # Extraer datos del diccionario
        cliente = presupuesto_dict.get("cliente", {})
        detalles = presupuesto_dict.get("detalles_trabajo", {})
        presupuesto = presupuesto_dict.get("presupuesto", {})
        
        nombre = cliente.get("nombre", "No especificado")
        nif = cliente.get("nif", "No especificado")
        direccion = cliente.get("direccion", "No especificada")
        email = cliente.get("email", "No especificado")
        
        superficie = detalles.get("area_m2", "No especificada")
        tipo_pintura = detalles.get("tipo_pintura", "No especificada")
        tipo_trabajo = detalles.get("tipo_trabajo", "No especificado")
        
        coste_total = presupuesto.get("total_con_iva", "No especificado")
        estado_documento = presupuesto_dict.get("estado", "Presupuestado") # Nuevo campo de estado
        presupuesto_numero = presupuesto_dict.get("presupuesto_numero", "N/A")
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Crear la entrada de historial en formato Markdown
        entrada = f"""
---
## Documento: {estado_documento} #{presupuesto_numero}

- **Fecha**: {fecha_actual}
- **Cliente**: {nombre}
- **NIF/CIF**: {nif}
- **Dirección**: {direccion}
- **Email**: {email}
- **Trabajo**: {tipo_trabajo.title()} con pintura {tipo_pintura.lower()}
- **Superficie**: {superficie} m²
- **Coste Total (IVA incl.)**: {coste_total} €
- **Estado**: {estado_documento}
"""

        # Asegurarse de que el directorio existe
        os.makedirs(os.path.dirname(archivo_path), exist_ok=True)

        # Añadir la entrada al archivo de historial
        with open(archivo_path, "a", encoding="utf-8") as f:
            f.write(entrada)

        mensaje_exito = f"✅ Documento [{estado_documento} #{presupuesto_numero}] para {nombre} guardado en el historial."
        print(mensaje_exito)
        return {"estado": "éxito", "mensaje": mensaje_exito}

    except Exception as e:
        mensaje_error = f"❌ Error al guardar en el historial: {str(e)}"
        print(mensaje_error)
        return {"estado": "error", "error": mensaje_error}
