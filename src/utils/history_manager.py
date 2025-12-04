from datetime import datetime
import os
import re

def guardar_presupuesto_en_historial(presupuesto_dict: dict, archivo_path: str = "data/customer_history.md") -> dict:
    """
    Guarda o actualiza un presupuesto en el historial de clientes.
    Si ya existe una entrada para el mismo cliente y trabajo, la actualiza.
    Si no existe, crea una nueva entrada.
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
        estado = presupuesto_dict.get("estado", "Presupuestado") 
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Asegurar que el directorio data/ existe
        os.makedirs(os.path.dirname(archivo_path), exist_ok=True)

        # Leer el archivo existente si existe
        contenido_existente = ""
        if os.path.exists(archivo_path):
            with open(archivo_path, "r", encoding="utf-8") as f:
                contenido_existente = f.read()

        # Buscar si ya existe una entrada para este cliente y trabajo
        # Patrón para buscar entradas del mismo cliente (NIF) con los mismos detalles de trabajo
        patron_entrada = rf"## .*? - {re.escape(nombre)} \(.*?\).*?\*\*NIF/CIF:\*\* {re.escape(nif)}.*?- Área: {re.escape(str(superficie))} m²\s*- Tipo de trabajo: {re.escape(tipo_trabajo)}\s*- Tipo de pintura: {re.escape(tipo_pintura)}\s*- Zona: {re.escape(zona)}.*?---"
        
        # Buscar coincidencia
        coincidencia = re.search(patron_entrada, contenido_existente, re.DOTALL)

        if coincidencia:
            # Ya existe una entrada para este cliente y trabajo -> ACTUALIZAR
            entrada_vieja = coincidencia.group(0)
            
            # Formatear la entrada actualizada
            entrada_nueva = f"""## {estado} - {nombre} ({fecha_actual})

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

---"""

            # Reemplazar la entrada vieja con la nueva
            contenido_actualizado = contenido_existente.replace(entrada_vieja, entrada_nueva)
            
            with open(archivo_path, "w", encoding="utf-8") as f:
                f.write(contenido_actualizado)

            print(f"✅ Historial actualizado para el cliente: {nombre} (Estado: {estado})")
            
            return {
                "estado": "éxito",
                "mensaje": f"Historial actualizado correctamente para {nombre} - {estado}"
            }
        else:
            # No existe -> CREAR NUEVA ENTRADA
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

            # Escribir la entrada en el archivo de historial
            with open(archivo_path, "a", encoding="utf-8") as f:
                f.write(entrada)

            print(f"✅ Nueva entrada en historial creada para el cliente: {nombre}")
            
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