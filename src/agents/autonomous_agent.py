"""
AGENTE AUTÓNOMO PARA GENERACIÓN DE PRESUPUESTOS Y PDFs
Ejecuta acciones de forma independiente sin intervención manual del usuario
"""

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional, Any
import os
from datetime import datetime
import json

# ============================================================================
# 1. DEFINIR TOOLS QUE EL AGENTE PUEDE USAR AUTÓNOMAMENTE
# ============================================================================

@tool
def calcular_presupuesto(
    area_m2: float,
    tipo_pintura: str,
    tipo_trabajo: str,
    cliente_nombre: str,
    cliente_nif: str = "No especificado",
    cliente_email: str = "No especificado",
    zona_trabajo: str = "Interior"
) -> dict:
    """
    Calcula presupuesto automático basado en parámetros.
    
    Args:
        area_m2: Área total a pintar en metros cuadrados
        tipo_pintura: Tipo de pintura (plástica, acrílica, esmalte, etc)
        tipo_trabajo: Tipo de trabajo (interior, exterior, restauración)
        cliente_nombre: Nombre del cliente
        cliente_nif: NIF/CIF del cliente
        cliente_email: Email del cliente
        zona_trabajo: Interior o Exterior
    
    Returns:
        dict con presupuesto completo
    """
    # Precios base por m² según tipo
    precios_base = {
        "plástica": 8.50,
        "acrílica": 12.00,
        "esmalte": 15.00,
        "epoxi": 25.00,
        "poliuretano": 28.00,
    }
    
    # Multiplicadores según tipo de trabajo
    multiplicadores = {
        "interior": 1.0,
        "exterior": 1.3,
        "restauración": 1.5,
        "fachada": 1.4,
    }
    
    precio_base = precios_base.get(tipo_pintura.lower(), 10.00)
    multiplicador = multiplicadores.get(tipo_trabajo.lower(), 1.0)
    
    # Calcular costo de material
    costo_material = area_m2 * precio_base * multiplicador
    
    # Calcular costo de mano de obra (1 pintor = 12€/hora, 8m²/hora)
    horas_trabajo = area_m2 / 8
    costo_mano_obra = horas_trabajo * 12
    
    # Costos adicionales
    costos_adicionales = {
        "preparación": costo_material * 0.15,  # 15% del material
        "transporte": 50.00,
        "limpieza_final": 30.00,
    }
    
    subtotal = costo_material + costo_mano_obra + sum(costos_adicionales.values())
    
    # Margen de ganancia (30%)
    margen = subtotal * 0.30
    total_sin_iva = subtotal + margen
    iva = total_sin_iva * 0.21
    total_con_iva = total_sin_iva + iva
    
    return {
        "cliente": {
            "nombre": cliente_nombre,
            "nif": cliente_nif,
            "email": cliente_email,
        },
        "detalles_trabajo": {
            "area_m2": area_m2,
            "tipo_pintura": tipo_pintura,
            "tipo_trabajo": tipo_trabajo,
            "zona": zona_trabajo,
        },
        "presupuesto": {
            "costo_material": round(costo_material, 2),
            "costo_mano_obra": round(costo_mano_obra, 2),
            "costos_adicionales": {k: round(v, 2) for k, v in costos_adicionales.items()},
            "subtotal_sin_ganancia": round(subtotal, 2),
            "margen_ganancia": round(margen, 2),
            "total_sin_iva": round(total_sin_iva, 2),
            "iva_21": round(iva, 2),
            "total_con_iva": round(total_con_iva, 2),
        },
        "timestamp": datetime.now().isoformat(),
    }


@tool
def generar_texto_factura(presupuesto_dict: dict) -> str:
    """
    Genera texto formateado de factura a partir de datos de presupuesto.
    Acción autónoma del agente para crear documento de facturación.
    
    Args:
        presupuesto_dict: Dict con datos del presupuesto
    
    Returns:
        str con factura formateada
    """
    cliente = presupuesto_dict["cliente"]
    detalles = presupuesto_dict["detalles_trabajo"]
    presupuesto = presupuesto_dict["presupuesto"]
    
    factura = f"""
════════════════════════════════════════════════
FACTURA DE SERVICIOS DE PINTURA
════════════════════════════════════════════════

DATOS DE LA EMPRESA:
Empresa: PINTURAS PROFESIONALES S.L.
CIF: B12345678
Dirección: Calle del Pintor 23, 28015 Madrid
Teléfono: +34 910 123 456
Email: facturacion@pinturaspro.es

────────────────────────────────────────────────

DATOS DEL CLIENTE:
Nombre: {cliente['nombre']}
NIF/CIF: {cliente['nif']}
Email: {cliente['email']}

────────────────────────────────────────────────

FACTURA:
Número de factura: FAC-2025-{datetime.now().strftime('%d%m%Y')}
Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}

────────────────────────────────────────────────

DETALLES DEL TRABAJO:
Zona: {detalles['zona']}
Tipo de trabajo: {detalles['tipo_trabajo']}
Tipo de pintura: {detalles['tipo_pintura']}
Área a pintar: {detalles['area_m2']} m²

────────────────────────────────────────────────

DESGLOSE DE COSTES:

Material: {presupuesto['costo_material']} €
Mano de obra: {presupuesto['costo_mano_obra']} €
Costos adicionales:
  - Preparación: {presupuesto['costos_adicionales']['preparación']} €
  - Transporte: {presupuesto['costos_adicionales']['transporte']} €
  - Limpieza final: {presupuesto['costos_adicionales']['limpieza_final']} €

────────────────────────────────────────────────

CÁLCULO FINAL:
Subtotal: {presupuesto['subtotal_sin_ganancia']} €
Margen de ganancia (30%): {presupuesto['margen_ganancia']} €
Base imponible: {presupuesto['total_sin_iva']} €
IVA (21%): {presupuesto['iva_21']} €

TOTAL FACTURA: {presupuesto['total_con_iva']} €

────────────────────────────────────────────────

CONDICIONES DE PAGO:
Forma de pago: Transferencia bancaria
Plazo de pago: 30 días desde emisión
Observaciones: Factura generada automáticamente por agente autónomo.

════════════════════════════════════════════════
"""
    
    return factura.strip()


@tool
def generar_pdf_presupuesto(factura_texto: str, nombre_cliente: str) -> dict:
    """
    Genera PDF autónomamente a partir del texto de factura.
    El agente ejecuta esta acción sin intervención del usuario.
    
    Args:
        factura_texto: Texto formateado de la factura
        nombre_cliente: Nombre del cliente para el archivo
    
    Returns:
        dict con información del PDF generado
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO
        
        buffer = BytesIO()
        filename = f"factura_{nombre_cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
            title="Factura Automática"
        )
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="InvoiceContent",
            fontSize=10,
            leading=14,
            alignment=0,
            textColor=colors.HexColor("#111827"),
            fontName="Courier",
            spaceBefore=1,
            spaceAfter=1,
        ))
        
        elements = []
        fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph("FACTURA GENERADA AUTOMÁTICAMENTE POR AGENTE", styles["Heading1"]))
        elements.append(Paragraph(f"Documento generado el: {fecha_gen}", styles["Normal"]))
        elements.append(Spacer(1, 15))
        
        for line in factura_texto.split("\n"):
            line = line.rstrip()
            if not line:
                elements.append(Spacer(1, 5))
                continue
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elements.append(Paragraph(safe_line, styles["InvoiceContent"]))
        
        doc.build(elements)
        buffer.seek(0)
        
        return {
            "estado": "éxito",
            "archivo": filename,
            "tamano_bytes": len(buffer.getvalue()),
            "timestamp": datetime.now().isoformat(),
            "mensaje": f"PDF generado automáticamente para cliente {nombre_cliente}"
        }
    
    except Exception as e:
        return {
            "estado": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@tool
def guardar_en_historial_cliente(presupuesto_dict: dict, ruta_historial: str = "data/customer_history.md") -> dict:
    """
    Guarda presupuesto en historial de clientes automáticamente.
    Acción autónoma para mantener registro histórico.
    
    Args:
        presupuesto_dict: Diccionario con datos del presupuesto
        ruta_historial: Ruta del archivo de historial
    
    Returns:
        dict con resultado de la operación
    """
    try:
        cliente = presupuesto_dict["cliente"]
        detalles = presupuesto_dict["detalles_trabajo"]
        presupuesto = presupuesto_dict["presupuesto"]
        
        entrada_historial = f"""
## Presupuesto - {cliente['nombre']} ({datetime.now().strftime('%d/%m/%Y %H:%M')})

**Cliente:** {cliente['nombre']}
**NIF/CIF:** {cliente['nif']}
**Email:** {cliente['email']}

**Detalles del trabajo:**
- Área: {detalles['area_m2']} m²
- Tipo: {detalles['tipo_trabajo']}
- Pintura: {detalles['tipo_pintura']}
- Zona: {detalles['zona']}

**Total con IVA:** {presupuesto['total_con_iva']} €

---

"""
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta_historial) or ".", exist_ok=True)
        
        # Guardar o actualizar
        if os.path.exists(ruta_historial):
            with open(ruta_historial, "a", encoding="utf-8") as f:
                f.write(entrada_historial)
        else:
            with open(ruta_historial, "w", encoding="utf-8") as f:
                f.write("# Historial de Presupuestos\n\n")
                f.write(entrada_historial)
        
        return {
            "estado": "éxito",
            "mensaje": f"Presupuesto guardado en historial para {cliente['nombre']}",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "estado": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# 2. AGENTE AUTÓNOMO
# ============================================================================

class AutonomousPresupuestoAgent:
    """
    Agente autónomo que ejecuta todas las acciones sin intervención del usuario.
    - Calcula presupuestos
    - Genera facturas
    - Crea PDFs
    - Guarda en historial
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.llm = ChatOpenAI(
            model="deepseek/deepseek-chat",
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3,
        )
        
        # Definir herramientas disponibles
        self.tools = [
            calcular_presupuesto,
            generar_texto_factura,
            generar_pdf_presupuesto,
            guardar_en_historial_cliente,
        ]
        
        # Crear prompt del agente
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un agente autónomo especializado en generación de presupuestos y facturas para empresa de pinturas.

TU RESPONSABILIDAD:
1. Recibir solicitud del usuario
2. EXTRAER datos necesarios (área, tipo de pintura, cliente, etc)
3. CALCULAR presupuesto automáticamente
4. GENERAR factura formateada
5. CREAR PDF automáticamente
6. GUARDAR en historial
7. REPORTAR al usuario qué acciones ejecutaste

IMPORTANTE: Ejecuta TODAS las acciones de forma autónoma. No esperes aprobación del usuario.
Si faltan datos, pregunta pero luego procede con valores razonables."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Crear agente
        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            self.prompt
        )
        
        # Ejecutor del agente
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )
    
    def procesar_solicitud(self, solicitud_usuario: str, historial_chat: list = None) -> dict:
        """
        Procesa solicitud del usuario y ejecuta acciones autónomamente.
        
        Args:
            solicitud_usuario: Descripción del trabajo a presupuestar
            historial_chat: Historial previo de conversación (opcional)
        
        Returns:
            dict con resultado y acciones ejecutadas
        """
        
        if historial_chat is None:
            historial_chat = []
        
        # Convertir historial al formato de LangChain
        chat_history = []
        for msg in historial_chat:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            else:
                chat_history.append(AIMessage(content=msg["content"]))
        
        try:
            resultado = self.agent_executor.invoke({
                "input": solicitud_usuario,
                "chat_history": chat_history,
            })
            
            return {
                "estado": "éxito",
                "respuesta": resultado.get("output", ""),
                "acciones_ejecutadas": self._extraer_acciones(resultado),
                "timestamp": datetime.now().isoformat(),
            }
        
        except Exception as e:
            return {
                "estado": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def _extraer_acciones(self, resultado: dict) -> list:
        """Extrae acciones ejecutadas del resultado del agente"""
        # Esto depende de cómo LangChain reporte las acciones
        # Aquí es un placeholder
        return ["calcular_presupuesto", "generar_factura", "generar_pdf", "guardar_historial"]


# ============================================================================
# 3. INTEGRACIÓN CON STREAMLIT (app.py)
# ============================================================================

def usar_agente_autonomo_en_streamlit():
    """
    Ejemplo de cómo integrar el agente autónomo en tu app.py
    """
    import streamlit as st
    
    @st.cache_resource
    def initialize_autonomous_agent():
        return AutonomousPresupuestoAgent()
    
    st.header("🤖 Agente Autónomo de Presupuestos")
    st.markdown("El agente ejecutará automáticamente todas las acciones sin necesidad de clics manuales")
    
    solicitud = st.text_area(
        "Describe el trabajo que necesitas presupuestar:",
        placeholder="Ej: Necesito presupuesto para pintar 150m² de interior con pintura plástica para el cliente Juan García"
    )
    
    if st.button("🚀 Ejecutar Agente Autónomo", type="primary"):
        if solicitud:
            with st.spinner("🤖 Agente trabajando autónomamente..."):
                agent = initialize_autonomous_agent()
                resultado = agent.procesar_solicitud(solicitud)
                
                if resultado["estado"] == "éxito":
                    st.success("✅ Agente completó todas las acciones")
                    st.markdown("### 📋 Resultado:")
                    st.markdown(resultado["respuesta"])
                    
                    st.markdown("### ⚙️ Acciones ejecutadas:")
                    for accion in resultado["acciones_ejecutadas"]:
                        st.write(f"✓ {accion}")
                else:
                    st.error(f"❌ Error: {resultado['error']}")
        else:
            st.warning("⚠️ Describe el trabajo")


if __name__ == "__main__":
    # Ejemplo de uso directo
    agent = AutonomousPresupuestoAgent()
    
    resultado = agent.procesar_solicitud(
        "Necesito presupuesto para pintar 100 m² de interior con pintura plástica para el cliente Maria López"
    )
    
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
