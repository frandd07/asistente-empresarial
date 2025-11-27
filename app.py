import streamlit as st
from src.utils.invoice_pdf_generator import create_invoice_pdf
from src.rag.retriever import CustomerHistoryRAG
from src.agents.budget_agent import BudgetCalculatorAgent
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime
from src.agents.price_margin_agent import PriceMarginAgent
import os



# Configuración de la página
st.set_page_config(
    page_title="Asistente Empresarial - Pinturas",
    page_icon="🎨",
    layout="wide"
)


# Inicializar sistemas (con cache)
@st.cache_resource
def initialize_rag():
    """Inicializa el sistema RAG"""
    return CustomerHistoryRAG()

@st.cache_resource
def initialize_price_agent():
    return PriceMarginAgent()


@st.cache_resource
def initialize_agent():
    """Inicializa el agente de presupuestos"""
    return BudgetCalculatorAgent()


# Título y descripción
st.title("🎨 Asistente Empresarial - Empresa de Pinturas")
st.markdown("""
Bienvenido al asistente inteligente de nuestra empresa de pinturas. Puedo ayudarte con:
- 📋 **Consultar historial de clientes** y trabajos anteriores
- 💰 **Generar presupuestos** automáticos para nuevos proyectos
""")


# Sidebar para seleccionar funcionalidad
with st.sidebar:
    st.header("⚙️ Opciones")
    
    mode = st.radio(
        "Selecciona una funcionalidad:",
        ["🔍 Consulta de Historial (RAG)",
     "💰 Generador de Presupuestos (Agente)",
     "📈 Asistente de Precios y Márgenes"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 Información del Sistema")
    st.info("""
    **Tecnologías:**
    - LangChain + OpenRouter
    - ChromaDB (Vector Store)
    - Embeddings locales
    - Agentes autónomos
    """)
    
    # Verificar API key
    if os.getenv("OPENROUTER_API_KEY"):
        st.success("✅ API Key configurada")
    else:
        st.error("❌ Falta API Key")


# Separador
st.markdown("---")


# Modo: Consulta de Historial (RAG)
if mode == "🔍 Consulta de Historial (RAG)":
    st.header("🔍 Consulta de Historial de Clientes")
    st.markdown("Pregunta sobre trabajos anteriores, clientes, pinturas utilizadas, costes, etc.")
    
    # Inicializar estado para guardar última respuesta RAG y factura
    if "last_rag_answer" not in st.session_state:
        st.session_state.last_rag_answer = None
    if "last_invoice_text" not in st.session_state:
        st.session_state.last_invoice_text = None
    
    # Ejemplos de consultas
    with st.expander("💡 Ejemplos de consultas"):
        st.markdown("""
        - ¿Qué trabajo se le hizo a María González?
        - ¿Qué clientes han usado pintura Jotun?
        - ¿Cuánto costó el trabajo de Carlos Ruiz?
        - ¿Qué trabajos se hicieron en noviembre?
        - ¿Cuál fue el trabajo más caro?
        """)
    
    # Input del usuario
    query = st.text_input(
        "Tu consulta:",
        placeholder="Ejemplo: ¿Qué trabajo se le hizo a Ana Martínez?",
        key="rag_query"
    )
    
    if st.button("🔎 Consultar", type="primary", key="rag_button"):
        if query:
            with st.spinner("🔄 Buscando en el historial..."):
                try:
                    rag = initialize_rag()
                    result = rag.query(query)
                    
                    # Mostrar respuesta
                    st.success("✅ Información encontrada")
                    st.markdown("### 📝 Respuesta:")
                    st.markdown(result["answer"])
                    
                    # Guardar última respuesta para usarla como base de factura
                    st.session_state.last_rag_answer = result["answer"]
                    st.session_state.last_invoice_text = None  # reset
                    
                    # Mostrar documentos fuente (opcional)
                    with st.expander("📚 Ver documentos fuente"):
                        for i, doc in enumerate(result["source_documents"], 1):
                            st.markdown(f"**Documento {i}:**")
                            st.text(doc.page_content)
                            st.markdown("---")
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Por favor, escribe una consulta")
    
    # Si hay una respuesta del RAG, permitir generar factura
    if st.session_state.last_rag_answer:
        st.markdown("---")
        if st.button("🧾 Generar factura de este presupuesto", type="primary", key="invoice_from_rag"):
            from src.utils.invoice_generator import generate_invoice_from_budget
            with st.spinner("🧾 Generando factura a partir del presupuesto encontrado..."):
                try:
                    factura = generate_invoice_from_budget(st.session_state.last_rag_answer)
                    st.session_state.last_invoice_text = factura
                except Exception as e:
                    st.error(f"❌ Error generando factura: {str(e)}")
        
        # Mostrar factura si ya se generó
        if st.session_state.last_invoice_text:
            st.markdown("### 🧾 Factura generada")
            st.markdown(st.session_state.last_invoice_text)

            # Añadir botón para generar PDF de la factura
            if "invoice_pdf_bytes_rag" not in st.session_state:
                st.session_state.invoice_pdf_bytes_rag = None
            
            if st.button("📄 Crear PDF de la factura", type="secondary", key="create_invoice_pdf_rag"):
                with st.spinner("📄 Creando PDF..."):
                    try:
                        pdf_bytes = create_invoice_pdf(st.session_state.last_invoice_text)
                        st.session_state.invoice_pdf_bytes_rag = pdf_bytes
                        st.success("✅ PDF de la factura creado")
                    except Exception as e:
                        st.error(f"❌ Error creando PDF de la factura: {str(e)}")
            
            if st.session_state.invoice_pdf_bytes_rag:
                st.download_button(
                    label="📥 Descargar Factura PDF",
                    data=st.session_state.invoice_pdf_bytes_rag,
                    file_name=f"factura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key="download_invoice_pdf_rag_btn"
                )
elif mode == "📈 Asistente de Precios y Márgenes":
    st.header("📈 Asistente de Precios y Márgenes")
    st.markdown("Analiza tu histórico de presupuestos y te sugiere precios mínimos según el margen que marques.")

    target_margin = st.slider(
        "Margen mínimo de beneficio (%)",
        min_value=10,
        max_value=60,
        value=25,
        step=5,
    )

    job_description = st.text_area(
        "Describe el trabajo que quieres analizar",
        placeholder="Ejemplo: Pintar 120 m² interior, pintura plástica blanca, cliente nuevo..."
    )

    if st.button("🔍 Analizar precios y márgenes", type="primary", key="analyze_margins"):
        if not job_description.strip():
            st.warning("⚠️ Por favor, describe el trabajo a analizar.")
        else:
            with st.spinner("📊 Analizando histórico..."):
                try:
                    history_path = "data/customer_history.md"
                    if not os.path.exists(history_path):
                        st.error("❌ No se encuentra data/customer_history.md. Guarda antes algún presupuesto.")
                    else:
                        with open(history_path, "r", encoding="utf-8") as f:
                            history_text = f.read()

                        price_agent = initialize_price_agent()
                        analysis = price_agent.analyze_margins(
                            history_text=history_text,
                            job_description=job_description,
                            target_margin_percent=float(target_margin),
                        )

                        st.markdown("### 📊 Análisis de precios y márgenes")
                        st.markdown(analysis)
                except Exception as e:
                    st.error(f"❌ Error analizando márgenes: {str(e)}")

# Modo: Generador de Presupuestos (Agente)
else:
    st.header("💰 Generador de Presupuestos Automático")
    st.markdown("El agente calculará presupuestos de forma autónoma. Mantén una conversación natural para completar todos los datos.")
    
    # Ejemplos de solicitudes
    with st.expander("💡 Ejemplos de solicitudes"):
        st.markdown("""
        - Necesito presupuesto para pintar 150 m² de interior
        - Quiero presupuesto para 439 metros para mi cliente Ronaldo
        - ¿Cuánto costaría pintar una habitación de 45 metros cuadrados?
        - Presupuesto para fachada exterior de 200m²
        """)
    
    # Inicializar historial de chat en session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "pdf_ready" not in st.session_state:
        st.session_state.pdf_ready = False
    
    if "pdf_bytes" not in st.session_state:
        st.session_state.pdf_bytes = None

    if "invoice_text" not in st.session_state:
        st.session_state.invoice_text = None

    if "invoice_pdf_bytes" not in st.session_state:
        st.session_state.invoice_pdf_bytes = None
    
    # Botón para reiniciar conversación
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Reiniciar", type="secondary"):
            st.session_state.messages = []
            st.session_state.pdf_ready = False
            st.session_state.pdf_bytes = None
            st.rerun()
    
    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario con chat
    if prompt := st.chat_input("Escribe aquí tu mensaje..."):
        # Añadir mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("🤖 Pensando..."):
                try:
                    agent = initialize_agent()
                    
                    # Convertir historial al formato de LangChain
                    lc_history = []
                    for msg in st.session_state.messages[:-1]:  # Excluir el último mensaje
                        if msg["role"] == "user":
                            lc_history.append(HumanMessage(content=msg["content"]))
                        else:
                            lc_history.append(AIMessage(content=msg["content"]))
                    
                    # Generar respuesta con historial
                    response = agent.generate_budget(prompt, chat_history=lc_history)
                    
                    # Mostrar respuesta
                    st.markdown(response)
                    
                    # Añadir respuesta al historial
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Resetear PDF cuando hay nueva respuesta
                    st.session_state.pdf_ready = False
                    st.session_state.pdf_bytes = None
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Botones para descargar conversación completa y guardar en historial
    if st.session_state.messages:
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)  # 3 columnas ahora
        
        # Botón descargar Markdown
        with col1:
            download_content = "# Conversación Completa - Presupuesto\n\n"
            download_content += "════════════════════════════════════════════════\n\n"
            for msg in st.session_state.messages:
                role = "👤 USUARIO" if msg["role"] == "user" else "🤖 ASISTENTE"
                download_content += f"**{role}:**\n{msg['content']}\n\n"
                download_content += "────────────────────────────────────────────────\n\n"
            
            st.download_button(
                label="📄 Markdown",
                data=download_content,
                file_name=f"conversacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                type="secondary"
            )
        
        # Botón para generar y descargar PDF
        with col2:
            # Botón para generar PDF
            if not st.session_state.pdf_ready:
                if st.button("🔄 Generar PDF", type="primary", key="generate_pdf"):
                    with st.spinner("🤖 Generando presupuesto profesional..."):
                        try:
                            from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                            from src.utils.pdf_generator import create_presupuesto_pdf
                            
                            # 1. Usar LLM para limpiar y calcular presupuesto
                            presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.messages)
                            
                            # 2. Generar PDF con el texto limpio
                            pdf_bytes = create_presupuesto_pdf(presupuesto_limpio)
                            
                            # 3. Guardar en session state
                            st.session_state.pdf_bytes = pdf_bytes
                            st.session_state.pdf_ready = True
                            
                            st.success("✅ PDF generado")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error generando PDF: {str(e)}")
            
            # Botón para descargar PDF (solo aparece cuando está listo)
            if st.session_state.pdf_ready and st.session_state.pdf_bytes:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=st.session_state.pdf_bytes,
                    file_name=f"presupuesto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        
               # Botón para guardar en historial (usa el presupuesto limpio)
        with col3:
            if st.button("💾 Guardar en Historial", type="primary", key="save_history"):
                with st.spinner("💾 Guardando cliente..."):
                    try:
                        from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                        from src.utils.history_manager import guardar_presupuesto_en_historial
                        from src.rag.vector_store import rebuild_customer_history_vectorstore  # NUEVO

                        # 1. Obtener el presupuesto limpio (igual que para el PDF)
                        presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.messages)

                        # 2. Guardar en customer_history.md
                        resultado = guardar_presupuesto_en_historial(presupuesto_limpio)

                        if resultado:
                            st.success("✅ Cliente guardado en customer_history.md")
                            
                            # 3. Reconstruir índice RAG
                            with st.spinner("🔄 Actualizando índice RAG..."):
                                rebuild_customer_history_vectorstore()

                            st.success("✅ Índice RAG actualizado. Ya puedes consultarlo en modo RAG.")
                            # 4. Limpiar caché de initialize_rag() para que coja el índice nuevo
                            st.cache_resource.clear()
                        else:
                            st.error("❌ No se pudo guardar en el historial")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col4:
 # 1) Generar factura en texto
            if st.button("🧾 Generar Factura", type="primary", key="generate_invoice"):
                with st.spinner("🧾 Generando factura a partir del presupuesto..."):
                    try:
                        from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                        from src.utils.invoice_generator import generate_invoice_from_budget

                        presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.messages)
                        factura_texto = generate_invoice_from_budget(presupuesto_limpio)

                        st.session_state.invoice_text = factura_texto
                        st.session_state.invoice_pdf_bytes = None  # reset

                        st.markdown("### 🧾 Factura generada")
                        st.markdown(factura_texto)

                    except Exception as e:
                        st.error(f"❌ Error generando factura: {str(e)}")

            # 2) Crear y descargar PDF si ya hay factura en texto
            if st.session_state.invoice_text:
                if st.button("📄 Crear PDF de la factura", type="secondary", key="create_invoice_pdf"):
                    try:
                        pdf_bytes = create_invoice_pdf(st.session_state.invoice_text)
                        st.session_state.invoice_pdf_bytes = pdf_bytes
                        st.success("✅ PDF de la factura creado")
                    except Exception as e:
                        st.error(f"❌ Error creando PDF de la factura: {str(e)}")

                if st.session_state.invoice_pdf_bytes:
                    st.download_button(
                        label="📥 Descargar Factura PDF",
                        data=st.session_state.invoice_pdf_bytes,
                        file_name=f"factura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        key="download_invoice_pdf_btn"
                    )


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Asistente Empresarial v1.0 | Powered by LangChain + OpenRouter</small>
</div>
""", unsafe_allow_html=True)
