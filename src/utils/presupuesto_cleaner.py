from langchain_openai import ChatOpenAI
import os


def get_presupuesto_final_limpio(messages: list) -> str:
    """
    Usa un LLM para convertir la conversación en un presupuesto profesional
    con todos los valores calculados, sin variables ni código.
    
    Args:
        messages: Lista de mensajes de la conversación (dict con 'role' y 'content')
    
    Returns:
        String con el presupuesto profesional completo
    """
    
    # Convertir historial a texto
    texto_chat = ""
    for msg in messages:
        role = "EMPRESA" if msg["role"] == "assistant" else "CLIENTE"
        texto_chat += f"**{role}:**\n{msg['content']}\n\n{'─'*60}\n\n"
    
    # Prompt especializado para generar presupuesto final
    prompt = f"""Eres un asistente experto en generar documentos empresariales profesionales.

A partir de la siguiente conversación entre una empresa de pinturas y un cliente, tu tarea es generar ÚNICAMENTE el presupuesto final profesional, listo para entregar al cliente.

REQUISITOS OBLIGATORIOS:
1. Extrae TODOS los datos recopilados (cliente, superficie, precios, etc.)
2. Calcula TODOS los importes numéricos (no dejes variables tipo {{variable}})
3. Presenta el presupuesto en formato limpio y profesional
4. Incluye:
   - Datos de la empresa
   - Datos del cliente
   - Detalles del proyecto
   - Desglose completo con importes CALCULADOS
   - Total con IVA
   - Condiciones
5. NO incluyas explicaciones, NO código Python, NO variables sin calcular

════════════════════════════════════════════════
         PRESUPUESTO DE PINTURA
════════════════════════════════════════════════

DATOS DE LA EMPRESA:
Empresa: PINTURAS PROFESIONALES S.L.
CIF: B12345678
Dirección: Calle del Pintor 23, 28015 Madrid
Teléfono: +34 910 123 456
Email: presupuestos@pinturaspro.es

────────────────────────────────────────────────

DATOS DEL CLIENTE:
Nombre: [nombre completo extraído]
NIF/CIF: [nif extraído]
Teléfono: [teléfono extraído]
Dirección del trabajo: [dirección extraída]
Email: [email extraído o "No proporcionado"]

────────────────────────────────────────────────

FECHA: [fecha actual]
Nº PRESUPUESTO: PRE-2024-[número aleatorio 3 dígitos]
VALIDEZ: 30 días

────────────────────────────────────────────────

DESCRIPCIÓN DEL PROYECTO:
Trabajos de pintura en [interior/exterior] con superficie total de [X] m².

DETALLES TÉCNICOS:
• Superficie total: [X] m²
• Tipo de pintura: [Interior/Exterior]
• Complejidad: [Baja/Media/Alta]
• Número de capas: 2 capas
• Incluye: Imprimación y acabado

────────────────────────────────────────────────

DESGLOSE DE COSTES:

1. MATERIALES
   - Pintura ([X] L × [Y]€/L) ............... [TOTAL]€
   - Imprimación (10%) ....................... [TOTAL]€
   - Material auxiliar (10%) ................. [TOTAL]€
   
   SUBTOTAL MATERIALES ...................... [SUMA]€

2. MANO DE OBRA
   - Preparación y aplicación ([X] m²) ....... [TOTAL]€
   
   SUBTOTAL MANO DE OBRA .................... [TOTAL]€

────────────────────────────────────────────────

BASE IMPONIBLE: ......................... [TOTAL SIN IVA]€
IVA (21%): .............................. [IVA]€

TOTAL PRESUPUESTO: ...................... [TOTAL CON IVA]€

────────────────────────────────────────────────

CONDICIONES:
• Validez del presupuesto: 30 días
• Forma de pago: 50% al inicio, 50% al finalizar
• Plazo de ejecución: [X] días laborables
• Garantía: 2 años en mano de obra

════════════════════════════════════════════════

CONVERSACIÓN:

{texto_chat}

IMPORTANTE: Responde SOLO con el presupuesto completo. Todos los números deben estar CALCULADOS (no variables).

PRESUPUESTO FINAL:"""
    
    # Llamar al LLM - versión simplificada
    llm = ChatOpenAI(
        model="google/gemini-2.5-flash-exp:free",  # Modelo actualizado
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3
    )
    
    try:
        result = llm.invoke(prompt)
        presupuesto_limpio = result.content.strip()
        
        # Limpieza adicional
        if "PRESUPUESTO FINAL:" in presupuesto_limpio:
            presupuesto_limpio = presupuesto_limpio.split("PRESUPUESTO FINAL:")[-1].strip()
        
        return presupuesto_limpio
        
    except Exception as e:
        # Si falla, intentar con modelo alternativo
        try:
            llm_backup = ChatOpenAI(
                model="deepseek/deepseek-chat",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                temperature=0.3
            )
            result = llm_backup.invoke(prompt)
            presupuesto_limpio = result.content.strip()
            
            if "PRESUPUESTO FINAL:" in presupuesto_limpio:
                presupuesto_limpio = presupuesto_limpio.split("PRESUPUESTO FINAL:")[-1].strip()
            
            return presupuesto_limpio
        except:
            return f"Error al generar presupuesto: {str(e)}"
