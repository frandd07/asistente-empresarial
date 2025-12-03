"""
AGENTE AUTÓNOMO PARA GENERACIÓN DE PRESUPUESTOS Y PDFs
Ejecuta acciones de forma independiente sin intervención manual del usuario
Ahora con PDFs profesionales usando xhtml2pdf (compatible Windows)
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

# ============ IMPORTS PARA xhtml2pdf (Compatible Windows) ============
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa  # ← Cambio a xhtml2pdf
from io import BytesIO
# =====================================================================

# ============================================================================
# 1. DEFINIR TOOLS QUE EL AGENTE PUEDE USAR AUTÓNOMAMENTE
# ============================================================================


def calcular_presupuesto(
    area_m2: float,
    tipo_pintura: str,
    tipo_trabajo: str,
    cliente_nombre: str,
    cliente_nif: str = "No especificado",
    cliente_email: str = "No especificado",
    cliente_direccion: str = "No especificada",
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
        cliente_direccion: Dirección del cliente
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
        "preparación": costo_material * 0.15,
        "transporte": 50.00,
        "limpieza_final": 30.00,
    }
    
    subtotal = costo_material + costo_mano_obra + sum(costos_adicionales.values())
    
    # No se aplica margen de ganancia por solicitud del usuario
    total_sin_iva = subtotal
    iva = total_sin_iva * 0.21
    total_con_iva = total_sin_iva + iva
    
    presupuesto_numero = f"PRES-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
        "presupuesto_numero": presupuesto_numero,
        "cliente": {
            "nombre": cliente_nombre,
            "nif": cliente_nif,
            "email": cliente_email,
            "direccion": cliente_direccion,
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
Dirección: {cliente['direccion']}

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

IVA (21%): {presupuesto['iva_21']} €

TOTAL FACTURA: {presupuesto['total_con_iva']} €

────────────────────────────────────────────────

CONDICIONES DE PAGO:
Forma de pago: Transferencia bancaria
Plazo de pago: 30 días desde emisión

════════════════════════════════════════════════
"""
    
    return factura.strip()


@tool
def generar_pdf_presupuesto(presupuesto_dict: dict) -> dict:
    """
    ⭐ Genera PDF de PRESUPUESTO con xhtml2pdf (compatible Windows) ⭐
    
    Args:
        presupuesto_dict: Diccionario completo del presupuesto
    
    Returns:
        dict con información del PDF generado
    """
    try:
        cliente = presupuesto_dict["cliente"]
        detalles = presupuesto_dict["detalles_trabajo"]
        presupuesto = presupuesto_dict["presupuesto"]
        
        # Configurar Jinja2
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('presupuesto_template.html.j2')
        
        # Datos
        presupuesto_numero = f"PRES-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        # Items
        items = [
            {
                "concepto": f"Pintura {detalles['tipo_pintura'].title()} - {detalles['tipo_trabajo'].title()}",
                "cantidad": f"{detalles['area_m2']} m²",
                "precio_unitario": f"€{presupuesto['costo_material'] / detalles['area_m2']:.2f}",
                "importe": f"€{presupuesto['costo_material']:.2f}"
            },
            {
                "concepto": "Mano de obra especializada",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costo_mano_obra']:.2f}",
                "importe": f"€{presupuesto['costo_mano_obra']:.2f}"
            },
            {
                "concepto": "Preparación y acabados",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['preparación']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['preparación']:.2f}"
            },
            {
                "concepto": "Transporte",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['transporte']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['transporte']:.2f}"
            },
            {
                "concepto": "Limpieza final",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}"
            }
        ]
        
        # Renderizar
        html_content = template.render(
            presupuesto_numero=presupuesto_numero,
            fecha=fecha_actual,
            cliente_nombre=cliente['nombre'],
            cliente_nif=cliente['nif'],
            cliente_direccion=cliente['direccion'],
            cliente_email=cliente['email'],
            items=items,
            subtotal=f"{presupuesto['subtotal_sin_ganancia']:.2f}",

            base_imponible=f"{presupuesto['total_sin_iva']:.2f}",
            iva=f"{presupuesto['iva_21']:.2f}",
            total=f"{presupuesto['total_con_iva']:.2f}"
        )
        
        # Generar PDF con xhtml2pdf
        nombre_archivo = f"presupuesto_{cliente['nombre'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("data/presupuestos", exist_ok=True)
        ruta_pdf = f"data/presupuestos/{nombre_archivo}"
        
        # Convertir HTML a PDF
        with open(ruta_pdf, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            raise Exception(f"Error generando PDF: {pisa_status.err}")
        
        return {
            "estado": "éxito",
            "archivo": nombre_archivo,
            "ruta_completa": ruta_pdf,
            "tamano_bytes": os.path.getsize(ruta_pdf),
            "timestamp": datetime.now().isoformat(),
            "mensaje": f"✅ Presupuesto PDF generado para {cliente['nombre']}"
        }
    
    except Exception as e:
        return {
            "estado": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@tool
def generar_pdf_factura(presupuesto_dict: dict) -> dict:
    """
    ⭐ Genera PDF de FACTURA con xhtml2pdf (compatible Windows) ⭐
    
    Args:
        presupuesto_dict: Diccionario completo del presupuesto
    
    Returns:
        dict con información del PDF generado
    """
    try:
        cliente = presupuesto_dict["cliente"]
        detalles = presupuesto_dict["detalles_trabajo"]
        presupuesto = presupuesto_dict["presupuesto"]
        
        # Configurar Jinja2
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('factura_template.html.j2')
        
        # Datos
        factura_numero = f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        # Items
        items = [
            {
                "concepto": f"Pintura {detalles['tipo_pintura'].title()} - {detalles['tipo_trabajo'].title()}",
                "cantidad": f"{detalles['area_m2']} m²",
                "precio_unitario": f"€{presupuesto['costo_material'] / detalles['area_m2']:.2f}",
                "importe": f"€{presupuesto['costo_material']:.2f}"
            },
            {
                "concepto": "Mano de obra especializada",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costo_mano_obra']:.2f}",
                "importe": f"€{presupuesto['costo_mano_obra']:.2f}"
            },
            {
                "concepto": "Preparación y acabados",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['preparación']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['preparación']:.2f}"
            },
            {
                "concepto": "Transporte",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['transporte']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['transporte']:.2f}"
            },
            {
                "concepto": "Limpieza final",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}"
            }
        ]
        
        # Renderizar
        html_content = template.render(
            factura_numero=factura_numero,
            fecha=fecha_actual,
            cliente_nombre=cliente['nombre'],
            cliente_nif=cliente['nif'],
            cliente_direccion=cliente['direccion'],
            cliente_email=cliente['email'],
            items=items,
            subtotal=f"{presupuesto['total_sin_iva']:.2f}",
            iva=f"{presupuesto['iva_21']:.2f}",
            total=f"{presupuesto['total_con_iva']:.2f}"
        )
        
        # Generar PDF con xhtml2pdf
        nombre_archivo = f"factura_{cliente['nombre'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("data/facturas", exist_ok=True)
        ruta_pdf = f"data/facturas/{nombre_archivo}"
        
        # Convertir HTML a PDF
        with open(ruta_pdf, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            raise Exception(f"Error generando PDF: {pisa_status.err}")
        
        return {
            "estado": "éxito",
            "archivo": nombre_archivo,
            "ruta_completa": ruta_pdf,
            "tamano_bytes": os.path.getsize(ruta_pdf),
            "timestamp": datetime.now().isoformat(),
            "mensaje": f"✅ Factura PDF generada para {cliente['nombre']}"
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
**Dirección:** {cliente['direccion']}

**Detalles del trabajo:**
- Área: {detalles['area_m2']} m²
- Tipo: {detalles['tipo_trabajo']}
- Pintura: {detalles['tipo_pintura']}
- Zona: {detalles['zona']}

**Total con IVA:** €{presupuesto['total_con_iva']}

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
            "mensaje": f"✅ Presupuesto guardado en historial para {cliente['nombre']}",
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
    
    Ahora con PDFs profesionales usando xhtml2pdf (compatible Windows):
    - Calcula presupuestos
    - Genera facturas
    - Crea PDFs profesionales con HTML/CSS
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
            generar_pdf_factura,
            guardar_en_historial_cliente,
        ]
        
        # Crear prompt del agente
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un agente autónomo especializado en generación de presupuestos y facturas para empresa de pinturas.

TU RESPONSABILIDAD:
1. Recibir solicitud del usuario
2. EXTRAER datos necesarios (área, tipo de pintura, cliente, NIF, email, dirección)
3. CALCULAR presupuesto automáticamente usando calcular_presupuesto
4. GENERAR factura formateada usando generar_texto_factura
5. CREAR PDF PROFESIONAL automáticamente usando generar_pdf_presupuesto o generar_pdf_factura
6. GUARDAR en historial usando guardar_en_historial_cliente
7. REPORTAR al usuario qué acciones ejecutaste y el resultado

IMPORTANTE: 
- Ejecuta TODAS las acciones de forma autónoma. No esperes aprobación del usuario.
- Si faltan datos del cliente, pregunta antes de proceder.
- Siempre intenta ejecutar las herramientas en orden.
- Reporta claramente el nombre del archivo PDF generado.

DATOS MÍNIMOS REQUERIDOS:
- Área en m²
- Tipo de pintura
- Nombre del cliente
- NIF del cliente (si no lo tiene, usa "Sin especificar")
- Email del cliente (opcional)
- Dirección del cliente (opcional)"""),
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
            max_iterations=10,
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
        acciones = []
        output = resultado.get("output", "").lower()
        
        if "calcular" in output or "presupuesto" in output:
            acciones.append("💰 Calcular Presupuesto")
        if "factura" in output or "generar" in output:
            acciones.append("📄 Generar Factura")
        if "pdf" in output:
            acciones.append("📋 Generar PDF Profesional")
        if "historial" in output or "guardado" in output:
            acciones.append("💾 Guardar En Historial Cliente")
        
        return acciones if acciones else ["⚙️ Procesamiento completado"]

# ============================================================================
# FUNCIONES AUXILIARES PARA STREAMLIT (sin @tool)
# ============================================================================

def generar_pdf_presupuesto_streamlit(presupuesto_dict: dict) -> dict:
    """
    Versión sin @tool para usar desde Streamlit.
    Genera PDF de PRESUPUESTO con xhtml2pdf.
    """
    try:
        cliente = presupuesto_dict["cliente"]
        detalles = presupuesto_dict["detalles_trabajo"]
        presupuesto = presupuesto_dict["presupuesto"]
        
        # Configurar Jinja2
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('presupuesto_template.html.j2')
        
        # Datos
        presupuesto_numero = f"PRES-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        # Items
        items = [
            {
                "concepto": f"Pintura {detalles['tipo_pintura'].title()} - {detalles['tipo_trabajo'].title()}",
                "cantidad": f"{detalles['area_m2']} m²",
                "precio_unitario": f"€{presupuesto['costo_material'] / detalles['area_m2']:.2f}",
                "importe": f"€{presupuesto['costo_material']:.2f}"
            },
            {
                "concepto": "Mano de obra especializada",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costo_mano_obra']:.2f}",
                "importe": f"€{presupuesto['costo_mano_obra']:.2f}"
            },
            {
                "concepto": "Preparación y acabados",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['preparación']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['preparación']:.2f}"
            },
            {
                "concepto": "Transporte",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['transporte']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['transporte']:.2f}"
            },
            {
                "concepto": "Limpieza final",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}"
            }
        ]
        
        # Renderizar
        html_content = template.render(
            presupuesto_numero=presupuesto_numero,
            fecha=fecha_actual,
            cliente_nombre=cliente['nombre'],
            cliente_nif=cliente['nif'],
            cliente_direccion=cliente['direccion'],
            cliente_email=cliente['email'],
            items=items,
            subtotal=f"{presupuesto['subtotal_sin_ganancia']:.2f}",

            base_imponible=f"{presupuesto['total_sin_iva']:.2f}",
            iva=f"{presupuesto['iva_21']:.2f}",
            total=f"{presupuesto['total_con_iva']:.2f}"
        )
        
        # Generar PDF con xhtml2pdf
        nombre_archivo = f"presupuesto_{cliente['nombre'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("data/presupuestos", exist_ok=True)
        ruta_pdf = f"data/presupuestos/{nombre_archivo}"
        
        # Convertir HTML a PDF
        with open(ruta_pdf, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            raise Exception(f"Error generando PDF: {pisa_status.err}")
        
        return {
            "estado": "éxito",
            "archivo": nombre_archivo,
            "ruta_completa": ruta_pdf,
            "tamano_bytes": os.path.getsize(ruta_pdf),
            "timestamp": datetime.now().isoformat(),
            "mensaje": f"✅ Presupuesto PDF generado para {cliente['nombre']}"
        }
    
    except Exception as e:
        return {
            "estado": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def generar_pdf_factura_streamlit(presupuesto_dict: dict) -> dict:
    """
    Versión sin @tool para usar desde Streamlit.
    Genera PDF de FACTURA con xhtml2pdf.
    """
    try:
        cliente = presupuesto_dict["cliente"]
        detalles = presupuesto_dict["detalles_trabajo"]
        presupuesto = presupuesto_dict["presupuesto"]
        
        # Configurar Jinja2
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('factura_template.html.j2')
        
        # Datos
        factura_numero = f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        # Items
        items = [
            {
                "concepto": f"Pintura {detalles['tipo_pintura'].title()} - {detalles['tipo_trabajo'].title()}",
                "cantidad": f"{detalles['area_m2']} m²",
                "precio_unitario": f"€{presupuesto['costo_material'] / detalles['area_m2']:.2f}",
                "importe": f"€{presupuesto['costo_material']:.2f}"
            },
            {
                "concepto": "Mano de obra especializada",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costo_mano_obra']:.2f}",
                "importe": f"€{presupuesto['costo_mano_obra']:.2f}"
            },
            {
                "concepto": "Preparación y acabados",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['preparación']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['preparación']:.2f}"
            },
            {
                "concepto": "Transporte",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['transporte']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['transporte']:.2f}"
            },
            {
                "concepto": "Limpieza final",
                "cantidad": "1",
                "precio_unitario": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}",
                "importe": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}"
            }
        ]
        
        # Renderizar
        html_content = template.render(
            factura_numero=factura_numero,
            fecha=fecha_actual,
            cliente_nombre=cliente['nombre'],
            cliente_nif=cliente['nif'],
            cliente_direccion=cliente['direccion'],
            cliente_email=cliente['email'],
            items=items,
            subtotal=f"{presupuesto['total_sin_iva']:.2f}",
            iva=f"{presupuesto['iva_21']:.2f}",
            total=f"{presupuesto['total_con_iva']:.2f}"
        )
        
        # Generar PDF con xhtml2pdf
        nombre_archivo = f"factura_{cliente['nombre'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("data/facturas", exist_ok=True)
        ruta_pdf = f"data/facturas/{nombre_archivo}"
        
        # Convertir HTML a PDF
        with open(ruta_pdf, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            raise Exception(f"Error generando PDF: {pisa_status.err}")
        
        return {
            "estado": "éxito",
            "archivo": nombre_archivo,
            "ruta_completa": ruta_pdf,
            "tamano_bytes": os.path.getsize(ruta_pdf),
            "timestamp": datetime.now().isoformat(),
            "mensaje": f"✅ Factura PDF generada para {cliente['nombre']}"
        }
    
    except Exception as e:
        return {
            "estado": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# 3. EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    agent = AutonomousPresupuestoAgent()
    
    resultado = agent.procesar_solicitud(
        """Necesito presupuesto para:
        - Cliente: María López García
        - NIF: 12345678A
        - Email: maria.lopez@example.com
        - Dirección: Calle Mayor 45, Madrid
        - Trabajo: Pintar 120 m² de interior
        - Pintura: Plástica estándar"""
    )
    
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
