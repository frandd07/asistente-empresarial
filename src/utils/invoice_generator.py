from langchain_openai import ChatOpenAI
import os


def generate_invoice_from_budget(budget_text: str) -> str:
    """
    Genera el texto de una factura profesional a partir del texto de un presupuesto.
    """
    prompt = f"""Eres un asistente experto en facturación para una empresa de pinturas en España.

TU TAREA:
A partir del siguiente PRESUPUESTO APROBADO, genera una FACTURA COMPLETA y PROFESIONAL lista para entregar al cliente.

REQUISITOS OBLIGATORIOS:
1. Usa los datos reales de:
   - Cliente (nombre, NIF/CIF, dirección, email si está)
   - Empresa: PINTURAS PROFESIONALES S.L., CIF B12345678, Calle del Pintor 23, 28015 Madrid, Teléfono +34 910 123 456
2. Copia el IMPORTE TOTAL del presupuesto como base para la factura (no inventes otro).
3. Calcula y muestra:
   - Base imponible (total sin IVA)
   - IVA al 21%
   - Total factura con IVA
4. Incluye:
   - Número de factura con formato FAC-2025-XXX (elige un número de 3 dígitos)
   - Fecha de emisión (usa la fecha de hoy si no se indica otra)
   - Forma de pago (por defecto: transferencia bancaria, 30 días)
5. No incluyas explicaciones, ni código, ni variables sin rellenar. Solo la factura final en texto.

FORMATO DE SALIDA:

════════════════════════════════════════════════
                 FACTURA
════════════════════════════════════════════════

DATOS DE LA EMPRESA:
Empresa: PINTURAS PROFESIONALES S.L.
CIF: B12345678
Dirección: Calle del Pintor 23, 28015 Madrid
Teléfono: +34 910 123 456
Email: facturacion@pinturaspro.es

────────────────────────────────────────────────

DATOS DEL CLIENTE:
Nombre: [NOMBRE CLIENTE]
NIF/CIF: [NIF]
Dirección: [DIRECCIÓN]
Email: [EMAIL O "No especificado"]

────────────────────────────────────────────────

FACTURA:
Número de factura: FAC-2025-XXX
Fecha de emisión: [DD/MM/AAAA]
Referencia presupuesto: [si aparece en el texto, si no "No especificada"]

────────────────────────────────────────────────

CONCEPTOS:

1. Descripción: [Texto breve del servicio de pintura]
   Base imponible: [IMPORTE SIN IVA] €
   IVA (21%): [IMPORTE IVA] €
   Total línea: [IMPORTE CON IVA] €

────────────────────────────────────────────────

TOTALES:

Base imponible: [IMPORTE SIN IVA] €
IVA (21%): [IMPORTE IVA] €
TOTAL FACTURA: [IMPORTE CON IVA] €

────────────────────────────────────────────────

CONDICIONES DE PAGO:
Forma de pago: Transferencia bancaria
Plazo de pago: 30 días desde la fecha de emisión
Observaciones: Factura generada automáticamente a partir de presupuesto aprobado.

════════════════════════════════════════════════

A continuación tienes el PRESUPUESTO APROBADO. Usa SOLO estos datos para la factura:

{budget_text}
"""

    llm = ChatOpenAI(
        model="deepseek/deepseek-chat",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
    )

    resp = llm.invoke(prompt)
    return resp.content.strip()
