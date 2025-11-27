from datetime import datetime
import re
import os


def guardar_presupuesto_en_historial(presupuesto_text: str, archivo_path: str = "data/customer_history.md") -> bool:
    """
    Guarda el presupuesto limpio como nueva entrada en el historial de clientes.

    Se apoya en regex sobre el texto final del presupuesto (ya formateado para el cliente),
    sin llamar a ningún modelo de IA adicional.
    """

    try:
        # Nombre cliente
        m = re.search(r"Nombre:\s*(.+?)(?:\n|$)", presupuesto_text)
        nombre = m.group(1).strip() if m else "No especificado"

        # NIF/CIF
        m = re.search(r"NIF/CIF:\s*(.+?)(?:\n|$)", presupuesto_text)
        nif = m.group(1).strip() if m else "No especificado"

        # Teléfono
        m = re.search(r"Tel[eé]fono:\s*(.+?)(?:\n|$)", presupuesto_text)
        telefono = m.group(1).strip() if m else "No especificado"

        # Dirección
        m = re.search(r"Direcci[oó]n del trabajo:\s*(.+?)(?:\n|$)", presupuesto_text)
        direccion = m.group(1).strip() if m else "No especificado"

        # Email
        m = re.search(r"Email:\s*(.+?)(?:\n|$)", presupuesto_text)
        email = m.group(1).strip() if m else "No especificado"

        # Superficie
        m = re.search(r"Superficie total:\s*([\d.,]+)\s*m²", presupuesto_text)
        superficie = m.group(1).replace(",", ".") if m else "No especificado"

        # Tipo de pintura
        m = re.search(r"Tipo de pintura:\s*(.+?)(?:\n|$)", presupuesto_text)
        tipo_pintura = m.group(1).strip() if m else "No especificado"

        # Complejidad (solo como observación extra)
        m = re.search(r"Complejidad:\s*(.+?)(?:\n|$)", presupuesto_text)
        complejidad = m.group(1).strip() if m else "No especificado"

        # Coste total
        m = re.search(r"TOTAL PRESUPUESTO:\s*([\d.,]+)\s*€", presupuesto_text)
        coste_total = m.group(1).replace(",", ".") if m else "No especificado"

        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        entrada = f"""

## Cliente: {nombre}
- **NIF/CIF**: {nif}
- **Teléfono**: {telefono}
- **Dirección**: {direccion}
- **Email**: {email}
- **Fecha**: {fecha_actual}
- **Trabajo**: Pintura {tipo_pintura.lower()}
- **Superficie**: {superficie} m²
- **Pintura utilizada**: {tipo_pintura}
- **Cantidad**: [Estimado según presupuesto]
- **Coste total**: {coste_total}€
- **Observaciones**: Presupuesto generado automáticamente. Complejidad: {complejidad}
"""

        # Asegurar que existe el directorio data/
        os.makedirs(os.path.dirname(archivo_path), exist_ok=True)

        with open(archivo_path, "a", encoding="utf-8") as f:
            f.write(entrada)

        print(f"✅ Cliente guardado en historial: {nombre}")
        return True

    except Exception as e:
        print(f"❌ Error guardando en historial: {e}")
        return False
