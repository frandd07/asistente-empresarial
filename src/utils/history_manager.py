from datetime import datetime
import os

def guardar_presupuesto_en_historial(presupuesto_dict: dict, archivo_path: str = "data/customer_history.md") -> dict:
    """
    Guarda un presupuesto (desde un diccionario) como una nueva entrada en el historial de clientes.
    """
    try:
        # Extraer datos del diccionario
        cliente = presupuesto_dict.get("cliente", {})
        nombre = cliente.get("nombre", "No especificado")
        nif = cliente.get("nif", "No especificado")
        direccion = cliente.get("direccion", "No especificada")
        email = cliente.get("email", "No especificado")

        detalles = presupuesto_dict.get("detalles_trabajo", {})
        superficie = detalles.get("area_m2", "No especificado")
        tipo_pintura = detalles.get("tipo_pintura", "No especificado")
        tipo_trabajo = detalles.get("tipo_trabajo", "No especificado")
        zona = detalles.get("zona", "No especificado")

        presupuesto = presupuesto_dict.get("presupuesto", {})
        coste_total = presupuesto.get("total_con_iva", "No especificado")

        # El estado se añade dinámicamente en app.py antes de llamar a esta función
        estado = presupuesto_dict.get("estado", "Presupuesto") 
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Formatear la entrada para el historial
        entrada = f"""
## {estado} - {nombre} ({fecha_actual})

**Cliente:** {nombre}
**NIF/CIF:** {nif}
**Email:** {email}
**Dirección:** {direccion}

**Detalles del trabajo:**
- Área: {superficie} m²
- Tipo de trabajo: {tipo_trabajo}
- Tipo de pintura: {tipo_pintura}
- Zona: {zona}

**Total con IVA:** €{coste_total}
**Estado actual:** {estado}

---
"""

        # Asegurar que el directorio data/ existe
        os.makedirs(os.path.dirname(archivo_path), exist_ok=True)

        # Escribir la entrada en el archivo de historial
        with open(archivo_path, "a", encoding="utf-8") as f:
            f.write(entrada)

        print(f"✅ Historial guardado para el cliente: {nombre}")
        
        return {
            "estado": "éxito",
            "mensaje": f"Historial guardado correctamente para {nombre}"
        }

    except Exception as e:
        print(f"❌ Error al guardar en el historial: {e}")
        return {
            "estado": "error",
            "error": str(e)
        }