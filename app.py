import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime
import os
import json
import re
import glob

from src.agents.router_agent import RouterAgent
from src.rag.retriever import CustomerHistoryRAG
from src.agents.budget_agent import BudgetCalculatorAgent
from src.agents.price_margin_agent import PriceMarginAgent
from src.agents.autonomous_agent import calcular_presupuesto, generar_pdf_presupuesto_streamlit, generar_pdf_factura_streamlit
from src.utils.history_manager import guardar_presupuesto_en_historial
from src.rag.vector_store import rebuild_customer_history_vectorstore

# Configuración de la página
st.set_page_config(page_title=" Entre Brochas", layout="wide")

# Inicialización de agentes con cache
@st.cache_resource
def initialize_router_agent():
    return RouterAgent()

@st.cache_resource
def initialize_rag():
    return CustomerHistoryRAG()

@st.cache_resource
def initialize_price_agent():
    return PriceMarginAgent()

@st.cache_resource
def initialize_budget_agent():
    return BudgetCalculatorAgent()


def buscar_presupuesto_por_rag(prompt: str):
    """
    Usa RAG para buscar presupuestos pendientes y luego localiza el archivo JSON.
    """
    try:
        rag = initialize_rag()
        
        # Construir query más natural para mejorar la búsqueda semántica
        query = f"Estado del presupuesto para: {prompt}"
        
        result = rag.query(query)
        respuesta_rag = result.get("answer", "")
        
        # Intentar extraer el número de presupuesto de la respuesta RAG
        match = re.search(r'PRES-\d{14}', respuesta_rag)
        
        if match:
            presupuesto_numero = match.group(0)
            
            # Localizar el archivo JSON correspondiente
            json_path = os.path.join("data/presupuestos", f"presupuesto_{presupuesto_numero}.json")
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verificar que esté en estado "Presupuestado"
                    if data.get("estado", "").lower() == "presupuestado":
                        return {
                            "path": json_path,
                            "data": data,
                            "numero": presupuesto_numero
                        }
        
        # Si no encontramos por número PRES, buscar por nombre de cliente en los JSONs
        import unicodedata
        json_files = glob.glob("data/presupuestos/presupuesto_*.json")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verificar que esté en estado "Presupuestado"
                    if data.get("estado", "").lower() == "presupuestado":
                        cliente_nombre = data.get("cliente", {}).get("nombre", "").lower()
                        prompt_lower = prompt.lower()
                        
                        # Normalizar tildes para comparación
                        cliente_normalized = ''.join(
                            c for c in unicodedata.normalize('NFD', cliente_nombre)
                            if unicodedata.category(c) != 'Mn'
                        )
                        prompt_normalized = ''.join(
                            c for c in unicodedata.normalize('NFD', prompt_lower)
                            if unicodedata.category(c) != 'Mn'
                        )
                        
                        # Verificar si alguna palabra del nombre aparece en el prompt
                        palabras_nombre = cliente_normalized.split()
                        if any(palabra in prompt_normalized for palabra in palabras_nombre if len(palabra) > 3):
                            presupuesto_numero = data.get("presupuesto_numero")
                            return {
                                "path": json_file,
                                "data": data,
                                "numero": presupuesto_numero
                            }
            except Exception as e:
                continue
        
        return None
    
    except Exception as e:
        print(f"Error en búsqueda RAG de presupuesto: {e}")
        return None


def buscar_factura_por_rag(prompt: str):
    """
    Usa RAG para buscar facturas pendientes de pago y luego localiza el archivo JSON.
    """
    try:
        rag = initialize_rag()
        
        # Construir query más natural para mejorar la búsqueda semántica
        query = f"Estado de la factura o presupuesto para: {prompt}"
        
        result = rag.query(query)
        respuesta_rag = result.get("answer", "")
        
        # Intentar extraer el número de presupuesto de la respuesta RAG
        match = re.search(r'PRES-\d{14}', respuesta_rag)
        
        if match:
            presupuesto_numero = match.group(0)
            
            # Localizar el archivo JSON correspondiente
            json_path = os.path.join("data/presupuestos", f"presupuesto_{presupuesto_numero}.json")
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verificar que esté pendiente de pago
                    if data.get("estadoPago", "").lower() == "pendiente":
                        return {
                            "path": json_path,
                            "data": data,
                            "numero": presupuesto_numero
                        }
        
        # Si no encontramos por número PRES, intentar buscar por nombre de cliente en los JSONs
        # Extraer posible nombre del cliente del prompt
        import os
        import json
        
        json_files = glob.glob("data/presupuestos/presupuesto_*.json")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verificar que esté pendiente de pago
                    if data.get("estadoPago", "").lower() == "pendiente":
                        # Buscar coincidencia de nombre (sin tildes, case-insensitive)
                        cliente_nombre = data.get("cliente", {}).get("nombre", "").lower()
                        prompt_lower = prompt.lower()
                        
                        # Normalizar tildes para comparación
                        import unicodedata
                        cliente_normalized = ''.join(
                            c for c in unicodedata.normalize('NFD', cliente_nombre)
                            if unicodedata.category(c) != 'Mn'
                        )
                        prompt_normalized = ''.join(
                            c for c in unicodedata.normalize('NFD', prompt_lower)
                            if unicodedata.category(c) != 'Mn'
                        )
                        
                        # Verificar si alguna palabra del nombre aparece en el prompt
                        palabras_nombre = cliente_normalized.split()
                        if any(palabra in prompt_normalized for palabra in palabras_nombre if len(palabra) > 3):
                            presupuesto_numero = data.get("presupuesto_numero")
                            return {
                                "path": json_file,
                                "data": data,
                                "numero": presupuesto_numero
                            }
            except Exception as e:
                continue
        
        return None
    
    except Exception as e:
        print(f"Error en búsqueda RAG de factura: {e}")
        return None


def handle_mark_as_paid(budget_dict, budget_json_path, chat_history):
    """Marca una factura como pagada en el archivo JSON y actualiza el historial."""
    try:
        # Cargar el JSON actual para asegurar que tenemos la última versión
        with open(budget_json_path, 'r', encoding='utf-8') as f:
            current_budget_data = json.load(f)
        
        current_budget_data["estadoPago"] = "Pagada"
        current_budget_data["fechaPago"] = datetime.now().isoformat()
        
        with open(budget_json_path, 'w', encoding='utf-8') as f:
            json.dump(current_budget_data, f, indent=4, ensure_ascii=False)
        
        st.session_state.messages.append({"role": "assistant", "content": f"✅ Factura {current_budget_data['presupuesto_numero']} marcada como PAGADA."})
        
        # Registrar en el historial de clientes
        historial_entrada_pagada = current_budget_data.copy()
        historial_entrada_pagada["estado"] = "Factura Pagada"
        guardar_historial_resultado = guardar_presupuesto_en_historial(historial_entrada_pagada)
        
        if guardar_historial_resultado["estado"] == "éxito":
            rebuild_customer_history_vectorstore()
            st.cache_resource.clear()
            st.session_state.messages.append({"role": "assistant", "content": "Historial de cliente actualizado (Factura Pagada)."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error actualizando historial: {guardar_historial_resultado['error']}"})
        
        st.session_state.current_task = None
        st.session_state.rag_refresh = True
        
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Error al marcar como pagada: {str(e)}"})


def handle_accept_budget(budget_dict, budget_json_path, chat_history):
    """Convierte un presupuesto aceptado en una factura."""
    try:
        # Cargar el JSON actual
        with open(budget_json_path, 'r', encoding='utf-8') as f:
            current_budget_data = json.load(f)
        
        # 1. Generar la factura en PDF
        invoice_result = generar_pdf_factura_streamlit(current_budget_data)
        
        if invoice_result["estado"] == "éxito":
            with open(invoice_result["ruta_completa"], 'rb') as f:
                st.session_state.invoice_pdf_bytes = f.read()
            st.session_state.messages.append({"role": "assistant", "content": f"✅ Factura {invoice_result['archivo']} generada y guardada."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error generando factura: {invoice_result['error']}"})
            return
        
        # 2. Actualizar el estado del presupuesto
        current_budget_data["estado"] = "Facturado y Pendiente de Pago"
        current_budget_data["estadoPago"] = "Pendiente"
        current_budget_data["fechaFacturacion"] = datetime.now().isoformat()
        
        with open(budget_json_path, 'w', encoding='utf-8') as f:
            json.dump(current_budget_data, f, indent=4, ensure_ascii=False)
        
        st.session_state.final_budget_dict = current_budget_data
        st.session_state.messages.append({"role": "assistant", "content": "Estado del presupuesto actualizado a 'Facturado y Pendiente de Pago'."})
        
        # 3. Añadir al historial
        historial_entrada = current_budget_data.copy()
        historial_entrada["estado"] = "Facturado y Pendiente de Pago"
        guardar_historial_resultado = guardar_presupuesto_en_historial(historial_entrada)
        
        if guardar_historial_resultado["estado"] == "éxito":
            rebuild_customer_history_vectorstore()
            st.cache_resource.clear()
            st.session_state.messages.append({"role": "assistant", "content": "Historial de cliente actualizado (Factura Pendiente)."})
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error actualizando historial: {guardar_historial_resultado['error']}"})
        
        st.session_state.current_task = None
        st.session_state.task_completed = True
        st.session_state.rag_refresh = True
        
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Error al aceptar el presupuesto como factura: {str(e)}"})


def handle_budget_conversation(prompt, history):
    """Maneja la conversación para crear un presupuesto."""
    agent = initialize_budget_agent()
    response_text = agent.generate_budget(prompt, chat_history=history)
    
    # Intentar extraer el JSON de la respuesta del agente de forma más robusta
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group()
        
        try:
            data_collected = json.loads(json_str)
            st.session_state.messages.append({"role": "assistant", "content": "Perfecto! Tengo todos los datos. Procesando todo automáticamente..."})
            
            with st.spinner("Calculando presupuesto, generando PDFs y guardando en historial..."):
                # 1. Calcular
                final_budget = calcular_presupuesto(**data_collected)
                final_budget["estado"] = "Presupuestado"
                st.session_state.final_budget_dict = final_budget
                
                # Guardar JSON
                os.makedirs("data/presupuestos", exist_ok=True)
                budget_json_path = os.path.join("data/presupuestos", f"presupuesto_{final_budget['presupuesto_numero']}.json")
                with open(budget_json_path, 'w', encoding='utf-8') as f:
                    json.dump(final_budget, f, indent=4, ensure_ascii=False)
                
                st.session_state.budget_json_path = budget_json_path
                
                # 2. Generar PDF
                pdf_result = generar_pdf_presupuesto_streamlit(final_budget)
                
                if pdf_result["estado"] == "éxito":
                    with open(pdf_result["ruta_completa"], 'rb') as f:
                        st.session_state.pdf_bytes = f.read()
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ Presupuesto PDF '{pdf_result['archivo']}' generado."})
                else:
                    # Log the error and inform the user
                    error_message = pdf_result.get("error", "Error desconocido al generar el PDF.")
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ Error al generar el presupuesto PDF: {error_message}"})
                    st.session_state.pdf_bytes = None # Ensure it's None if generation failed
                    # Task is not completed if PDF generation fails, so we ensure task_completed is not set to True later if PDF failed.

                # 3. Guardar en historial (this should still happen even if PDF fails, as it's a separate step)
                guardar_resultado = guardar_presupuesto_en_historial(final_budget)
                
                if guardar_resultado["estado"] == "éxito":
                    rebuild_customer_history_vectorstore()
                    st.cache_resource.clear()
                    # Only mark task as completed and show success message if PDF was also successful
                    if st.session_state.pdf_bytes:
                        st.session_state.messages.append({"role": "assistant", "content": "✅ Presupuesto generado! Puedes descargarlo. Si deseas aceptarlo y generar la factura, házmelo saber."})
                        st.session_state.task_completed = True
                    else:
                        # If PDF failed but history saved, still inform user about history save but not task completion
                        st.session_state.messages.append({"role": "assistant", "content": "✅ Presupuesto guardado en historial (PDF no generado)."})
                        st.session_state.task_completed = False # Task is not truly completed if PDF failed
                else:
                    # Log error saving to history
                    error_message = guardar_resultado.get("error", "Error desconocido al guardar historial.")
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ Error al guardar en el historial de cliente: {error_message}"})
                    st.session_state.task_completed = False # Task failed
                
                st.session_state.current_task = None
        
        except json.JSONDecodeError:
            # Si el JSON extraído es inválido, podría ser parte de la conversación
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
    else:
        # Si no hay JSON, es una pregunta del agente
        st.session_state.messages.append({"role": "assistant", "content": response_text})


def handle_history_query(prompt):
    """Maneja una consulta al historial de clientes."""
    rag = initialize_rag()
    with st.spinner("Buscando en el historial..."):
        result = rag.query(prompt)
    
    response = result.get("answer", "No he encontrado información sobre eso.")
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.last_rag_response_content = response
    st.session_state.current_task = None


def handle_margins_query(prompt, history_text):
    """Maneja una consulta sobre márgenes de beneficio."""
    price_agent = initialize_price_agent()
    
    full_context = f"Historial de trabajos:\n{history_text}\n\nConsulta del usuario: {prompt}"
    
    with st.spinner("Analizando precios y márgenes..."):
        analysis = price_agent.analyze_margins(
            history_text=history_text,
            job_description=prompt,
            target_margin_percent=25.0,
        )
    
    st.session_state.messages.append({"role": "assistant", "content": analysis})
    st.session_state.current_task = None


# ============== UI PRINCIPAL ==============

st.title("Entre brochas")
st.markdown("Soy tu asistente inteligente. Puedes pedirme un presupuesto, consultar el historial de un cliente o analizar márgenes de un trabajo, todo en este chat.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ Información")
    st.info("""
    Este es un asistente unificado. Simplemente escribe lo que necesitas:
    
    - **Para un presupuesto**: "Necesito presupuesto para 100m² para Juan Pérez"
    - **Para historial**: "¿Qué trabajo le hicimos a María?"
    - **Para márgenes**: "Analiza el precio para pintar una fachada de 300m²"
    - **Para aceptar un presupuesto**: "Acepta el presupuesto de Juan Pérez"
    - **Para marcar una factura como pagada**: "La factura de María López ya está pagada"
    """)
    
    if os.getenv("OPENROUTER_API_KEY"):
        st.success("✅ API Key configurada")
    else:
        st.error("❌ Falta API Key")
    
    if st.button("🔄 Nueva Conversación"):
        st.session_state.clear()
        st.rerun()

# Inicialización del estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_task" not in st.session_state:
    st.session_state.current_task = None

if "task_completed" not in st.session_state:
    st.session_state.task_completed = False

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "invoice_pdf_bytes" not in st.session_state:
    st.session_state.invoice_pdf_bytes = None

if "final_budget_dict" not in st.session_state:
    st.session_state.final_budget_dict = None

if "budget_json_path" not in st.session_state:
    st.session_state.budget_json_path = None

if "last_rag_response_content" not in st.session_state:
    st.session_state.last_rag_response_content = None

if "rag_refresh" not in st.session_state:
    st.session_state.rag_refresh = False

# Mostrar historial del chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("¿Cómo puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        # Lógica principal de enrutamiento
        if st.session_state.current_task is None:
            router = initialize_router_agent()
            route = router.route(prompt)
            st.session_state.current_task = route
        else:
            route = st.session_state.current_task
        
        # Ejecutar la tarea correspondiente
        if route == "presupuesto":
            lc_history = [HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"]) 
                         for msg in st.session_state.messages[:-1]]
            handle_budget_conversation(prompt, lc_history)
        
        elif route == "historial":
            handle_history_query(prompt)
        
        elif route == "margenes":
            history_path = "data/customer_history.md"
            history_text = ""
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    history_text = f.read()
            handle_margins_query(prompt, history_text)
        
        elif route == "aceptar_presupuesto":
            # Usar RAG para buscar el presupuesto
            if st.session_state.final_budget_dict and st.session_state.budget_json_path:
                # Si existe en sesión, usar ese
                handle_accept_budget(st.session_state.final_budget_dict, st.session_state.budget_json_path, st.session_state.messages[:-1])
            else:
                # Buscar usando RAG
                st.session_state.messages.append({"role": "assistant", "content": "🔍 Buscando el presupuesto mediante RAG..."})
                
                resultado = buscar_presupuesto_por_rag(prompt)
                
                if resultado:
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ Presupuesto {resultado['numero']} encontrado para {resultado['data']['cliente']['nombre']}. Procediendo a generar la factura..."})
                    handle_accept_budget(resultado['data'], resultado['path'], st.session_state.messages[:-1])
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "❌ No encontré ningún presupuesto pendiente. ¿Puedes verificar el nombre del cliente o generar un nuevo presupuesto?"})
                    st.session_state.current_task = None
        
        elif route == "marcar_pagada":
            # Intentar extraer el número exacto primero
            match_presupuesto = re.search(r'PRES-\d{14}', prompt)
            
            if match_presupuesto:
                # Si hay número exacto, usarlo directamente
                presupuesto_numero_a_pagar = match_presupuesto.group(0)
                budget_json_path_to_pay = os.path.join("data/presupuestos", f"presupuesto_{presupuesto_numero_a_pagar}.json")
                
                if os.path.exists(budget_json_path_to_pay):
                    with open(budget_json_path_to_pay, 'r', encoding='utf-8') as f:
                        budget_data_to_pay = json.load(f)
                    
                    if budget_data_to_pay.get("estadoPago") == "Pendiente":
                        handle_mark_as_paid(budget_data_to_pay, budget_json_path_to_pay, st.session_state.messages[:-1])
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": f"La factura {presupuesto_numero_a_pagar} no está pendiente de pago."})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"No encontré la factura {presupuesto_numero_a_pagar}."})
            else:
                # Buscar usando RAG
                st.session_state.messages.append({"role": "assistant", "content": "🔍 Buscando la factura mediante RAG..."})
                
                resultado = buscar_factura_por_rag(prompt)
                
                if resultado:
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ Factura {resultado['numero']} encontrada para {resultado['data']['cliente']['nombre']}. Marcando como pagada..."})
                    handle_mark_as_paid(resultado['data'], resultado['path'], st.session_state.messages[:-1])
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "❌ No encontré ninguna factura pendiente. ¿Puedes verificar el nombre del cliente o proporcionar el número de factura?"})
            
            st.session_state.current_task = None
        
        else:  # Ruta general
            st.session_state.messages.append({"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte? Si necesitas un presupuesto, consultar un historial o analizar precios, solo tienes que pedírmelo."})
            st.session_state.current_task = None
    
    st.rerun()

# Lógica para mostrar descargas
if st.session_state.task_completed and (st.session_state.pdf_bytes or st.session_state.invoice_pdf_bytes):
    st.markdown("---")
    st.markdown("### 📥 Descargas Disponibles")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.pdf_bytes and st.session_state.final_budget_dict:
            st.download_button(
                label="📄 Descargar Presupuesto PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"presupuesto_{st.session_state.final_budget_dict['presupuesto_numero']}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.download_button(
                label="📄 Descargar Presupuesto PDF",
                data=b"",
                file_name="presupuesto.pdf",
                mime="application/pdf",
                disabled=True
            )
    
    with col2:
        if st.session_state.invoice_pdf_bytes and st.session_state.final_budget_dict:
            st.download_button(
                label="🧾 Descargar Factura PDF",
                data=st.session_state.invoice_pdf_bytes,
                file_name=f"factura_{st.session_state.final_budget_dict['presupuesto_numero']}.pdf",
                mime="application/pdf",
                type="primary"
            )

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray;"><small>Asistente Empresarial v6.0 | RAG-Powered Search</small></div>',
    unsafe_allow_html=True
)
