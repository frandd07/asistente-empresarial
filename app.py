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
- 🤖 **Agente autónomo** que genera TODO automáticamente
""")


# Sidebar para seleccionar funcionalidad
with st.sidebar:
    st.header("⚙️ Opciones")
    
    mode = st.radio(
        "Selecciona una funcionalidad:",
        [
            "🔍 Consulta de Historial (RAG)",
            "💰 Generador de Presupuestos (Manual)",
            "📈 Asistente de Precios y Márgenes",
            "🤖 Agente Autónomo (TODO Automático)"
        ],
        index=3  # Por defecto el autónomo
    )
    
    st.markdown("---")
    st.markdown("### 📊 Información del Sistema")
    
    if mode == "🤖 Agente Autónomo (TODO Automático)":
        st.success("""
        **Modo Autónomo Activo:**
        
        ✓ Conversación natural
        ✓ El agente pregunta lo que necesite
        ✓ Cuando tenga todo, AUTOMÁTICAMENTE:
          • Genera presupuesto
          • Crea PDF
          • Genera factura
          • Guarda en historial
        
        **Sin clics adicionales**
        """)
    else:
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


# ========================================================================
# MODO: AGENTE AUTÓNOMO CONVERSACIONAL
# ========================================================================
if mode == "🤖 Agente Autónomo (TODO Automático)":
    st.header("🤖 Agente Autónomo - Conversación Natural")
    st.markdown("""
    💬 **Habla con el agente de forma natural.** Te preguntará lo que necesite.
    
    ✨ Cuando tenga toda la información, **automáticamente**:
    - Generará el presupuesto completo
    - Creará el PDF profesional
    - Generará la factura
    - Guardará en el historial
    - Te dará los enlaces de descarga
    
    **Todo sin que tengas que hacer clic en nada más.**
    """)
    
    # Inicializar estados
    if "auto_messages" not in st.session_state:
        st.session_state.auto_messages = []
    
    if "auto_completed" not in st.session_state:
        st.session_state.auto_completed = False
    
    if "auto_pdf_bytes" not in st.session_state:
        st.session_state.auto_pdf_bytes = None
    
    if "auto_invoice_pdf_bytes" not in st.session_state:
        st.session_state.auto_invoice_pdf_bytes = None
    
    if "auto_presupuesto_texto" not in st.session_state:
        st.session_state.auto_presupuesto_texto = None
    
    # Botón para reiniciar
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Nueva conversación", type="secondary"):
            st.session_state.auto_messages = []
            st.session_state.auto_completed = False
            st.session_state.auto_pdf_bytes = None
            st.session_state.auto_invoice_pdf_bytes = None
            st.session_state.auto_presupuesto_texto = None
            st.rerun()
    
    # Mostrar historial de mensajes
    for message in st.session_state.auto_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("💬 Escribe tu mensaje (ej: Necesito presupuesto para 100m²)..."):
        # Añadir mensaje del usuario
        st.session_state.auto_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analizando y procesando..."):
                try:
                    agent = initialize_agent()
                    
                    # Convertir historial
                    lc_history = []
                    for msg in st.session_state.auto_messages[:-1]:
                        if msg["role"] == "user":
                            lc_history.append(HumanMessage(content=msg["content"]))
                        else:
                            lc_history.append(AIMessage(content=msg["content"]))
                    
                    # Generar respuesta
                    response = agent.generate_budget(prompt, chat_history=lc_history)
                    
                    # Detectar si el agente tiene toda la información
                    # (busca palabras clave que indiquen que el presupuesto está completo)
                    palabras_completado = [
                        "presupuesto total",
                        "total con iva",
                        "coste total",
                        "precio final",
                        "€",
                        "euros"
                    ]
                    
                    tiene_info_completa = any(palabra in response.lower() for palabra in palabras_completado)
                    
                    # Mostrar respuesta
                    st.markdown(response)
                    st.session_state.auto_messages.append({"role": "assistant", "content": response})
                    
                    # Si tiene info completa y aún no se ha ejecutado, EJECUTAR TODO AUTOMÁTICAMENTE
                    if tiene_info_completa and not st.session_state.auto_completed:
                        st.markdown("---")
                        st.info("🤖 **Detecté que tengo toda la información. Ejecutando acciones automáticas...**")
                        
                        with st.spinner("⚙️ Generando presupuesto limpio..."):
                            try:
                                from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                                presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.auto_messages)
                                st.session_state.auto_presupuesto_texto = presupuesto_limpio
                                st.success("✅ Presupuesto procesado")
                            except Exception as e:
                                st.error(f"Error en presupuesto: {e}")
                        
                        # Generar PDF del presupuesto
                        with st.spinner("📄 Generando PDF del presupuesto..."):
                            try:
                                from src.utils.pdf_generator import create_presupuesto_pdf
                                pdf_bytes = create_presupuesto_pdf(presupuesto_limpio)
                                st.session_state.auto_pdf_bytes = pdf_bytes
                                st.success("✅ PDF del presupuesto creado")
                            except Exception as e:
                                st.error(f"Error generando PDF: {e}")
                        
                        # Generar factura
                        with st.spinner("🧾 Generando factura..."):
                            try:
                                from src.utils.invoice_generator import generate_invoice_from_budget
                                factura_texto = generate_invoice_from_budget(presupuesto_limpio)
                                
                                # Generar PDF de la factura
                                invoice_pdf_bytes = create_invoice_pdf(factura_texto)
                                st.session_state.auto_invoice_pdf_bytes = invoice_pdf_bytes
                                st.success("✅ Factura y PDF de factura creados")
                            except Exception as e:
                                st.error(f"Error generando factura: {e}")
                        
                        # Guardar en historial
                        with st.spinner("💾 Guardando en historial de clientes..."):
                            try:
                                from src.utils.history_manager import guardar_presupuesto_en_historial
                                from src.rag.vector_store import rebuild_customer_history_vectorstore
                                
                                resultado = guardar_presupuesto_en_historial(presupuesto_limpio)
                                if resultado:
                                    rebuild_customer_history_vectorstore()
                                    st.cache_resource.clear()
                                    st.success("✅ Guardado en historial y RAG actualizado")
                                else:
                                    st.warning("⚠️ No se pudo guardar en historial")
                            except Exception as e:
                                st.error(f"Error guardando: {e}")
                        
                        st.session_state.auto_completed = True
                        
                        st.markdown("---")
                        st.success("""
                        🎉 **¡Todas las acciones completadas automáticamente!**
                        
                        ✓ Presupuesto calculado
                        ✓ PDF generado
                        ✓ Factura creada
                        ✓ Guardado en historial
                        
                        **Descarga tus archivos abajo** ⬇️
                        """)
                        
                        st.rerun()
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.auto_messages.append({"role": "assistant", "content": error_msg})
    
    # Mostrar botones de descarga si todo está completado
    if st.session_state.auto_completed:
        st.markdown("---")
        st.markdown("### 📥 Descargas Disponibles")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.auto_pdf_bytes:
                st.download_button(
                    label="📄 Descargar Presupuesto PDF",
                    data=st.session_state.auto_pdf_bytes,
                    file_name=f"presupuesto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        
        with col2:
            if st.session_state.auto_invoice_pdf_bytes:
                st.download_button(
                    label="🧾 Descargar Factura PDF",
                    data=st.session_state.auto_invoice_pdf_bytes,
                    file_name=f"factura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        
        with col3:
            if st.session_state.auto_presupuesto_texto:
                st.download_button(
                    label="📝 Descargar Presupuesto TXT",
                    data=st.session_state.auto_presupuesto_texto,
                    file_name=f"presupuesto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    type="secondary"
                )


# ========================================================================
# Modo: Consulta de Historial (RAG)
# ========================================================================
elif mode == "🔍 Consulta de Historial (RAG)":
    st.header("🔍 Consulta de Historial de Clientes")
    st.markdown("Pregunta sobre trabajos anteriores, clientes, pinturas utilizadas, costes, etc.")
    
    if "last_rag_answer" not in st.session_state:
        st.session_state.last_rag_answer = None
    if "last_invoice_text" not in st.session_state:
        st.session_state.last_invoice_text = None
    
    with st.expander("💡 Ejemplos de consultas"):
        st.markdown("""
        - ¿Qué trabajo se le hizo a María González?
        - ¿Qué clientes han usado pintura Jotun?
        - ¿Cuánto costó el trabajo de Carlos Ruiz?
        - ¿Qué trabajos se hicieron en noviembre?
        - ¿Cuál fue el trabajo más caro?
        """)
    
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
                    
                    st.success("✅ Información encontrada")
                    st.markdown("### 📝 Respuesta:")
                    st.markdown(result["answer"])
                    
                    st.session_state.last_rag_answer = result["answer"]
                    st.session_state.last_invoice_text = None
                    
                    with st.expander("📚 Ver documentos fuente"):
                        for i, doc in enumerate(result["source_documents"], 1):
                            st.markdown(f"**Documento {i}:**")
                            st.text(doc.page_content)
                            st.markdown("---")
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Por favor, escribe una consulta")
    
    if st.session_state.last_rag_answer:
        st.markdown("---")
        if st.button("🧾 Generar factura de este presupuesto", type="primary", key="invoice_from_rag"):
            from src.utils.invoice_generator import generate_invoice_from_budget
            with st.spinner("🧾 Generando factura..."):
                try:
                    factura = generate_invoice_from_budget(st.session_state.last_rag_answer)
                    st.session_state.last_invoice_text = factura
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.last_invoice_text:
            st.markdown("### 🧾 Factura generada")
            st.markdown(st.session_state.last_invoice_text)

            if "invoice_pdf_bytes_rag" not in st.session_state:
                st.session_state.invoice_pdf_bytes_rag = None
            
            if st.button("📄 Crear PDF de la factura", type="secondary", key="create_invoice_pdf_rag"):
                with st.spinner("📄 Creando PDF..."):
                    try:
                        pdf_bytes = create_invoice_pdf(st.session_state.last_invoice_text)
                        st.session_state.invoice_pdf_bytes_rag = pdf_bytes
                        st.success("✅ PDF creado")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
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
                        st.error("❌ No se encuentra data/customer_history.md.")
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
                    st.error(f"❌ Error: {str(e)}")


# ========================================================================
# Modo: Generador Manual (tu sistema anterior)
# ========================================================================
else:
    st.header("💰 Generador de Presupuestos (Modo Manual)")
    st.markdown("Conversación natural + botones manuales para generar archivos.")
    
    with st.expander("💡 Ejemplos de solicitudes"):
        st.markdown("""
        - Necesito presupuesto para pintar 150 m² de interior
        - Quiero presupuesto para 439 metros para mi cliente Ronaldo
        - ¿Cuánto costaría pintar una habitación de 45 metros cuadrados?
        """)
    
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
    
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Reiniciar", type="secondary"):
            st.session_state.messages = []
            st.session_state.pdf_ready = False
            st.session_state.pdf_bytes = None
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Escribe aquí tu mensaje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Pensando..."):
                try:
                    agent = initialize_agent()
                    
                    lc_history = []
                    for msg in st.session_state.messages[:-1]:
                        if msg["role"] == "user":
                            lc_history.append(HumanMessage(content=msg["content"]))
                        else:
                            lc_history.append(AIMessage(content=msg["content"]))
                    
                    response = agent.generate_budget(prompt, chat_history=lc_history)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.pdf_ready = False
                    st.session_state.pdf_bytes = None
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    if st.session_state.messages:
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            download_content = "# Conversación Completa\n\n"
            for msg in st.session_state.messages:
                role = "👤 USUARIO" if msg["role"] == "user" else "🤖 ASISTENTE"
                download_content += f"**{role}:**\n{msg['content']}\n\n"
            
            st.download_button(
                label="📄 Markdown",
                data=download_content,
                file_name=f"conversacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                type="secondary"
            )
        
        with col2:
            if not st.session_state.pdf_ready:
                if st.button("🔄 Generar PDF", type="primary", key="generate_pdf"):
                    with st.spinner("🤖 Generando..."):
                        try:
                            from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                            from src.utils.pdf_generator import create_presupuesto_pdf
                            
                            presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.messages)
                            pdf_bytes = create_presupuesto_pdf(presupuesto_limpio)
                            st.session_state.pdf_bytes = pdf_bytes
                            st.session_state.pdf_ready = True
                            st.success("✅ PDF generado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            if st.session_state.pdf_ready and st.session_state.pdf_bytes:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=st.session_state.pdf_bytes,
                    file_name=f"presupuesto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
        
        with col3:
            if st.button("💾 Guardar en Historial", type="primary", key="save_history"):
                with st.spinner("💾 Guardando..."):
                    try:
                        from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                        from src.utils.history_manager import guardar_presupuesto_en_historial
                        from src.rag.vector_store import rebuild_customer_history_vectorstore

                        presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.messages)
                        resultado = guardar_presupuesto_en_historial(presupuesto_limpio)

                        if resultado:
                            st.success("✅ Guardado")
                            with st.spinner("🔄 Actualizando RAG..."):
                                rebuild_customer_history_vectorstore()
                            st.success("✅ RAG actualizado")
                            st.cache_resource.clear()
                        else:
                            st.error("❌ No se pudo guardar")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col4:
            if st.button("🧾 Generar Factura", type="primary", key="generate_invoice"):
                with st.spinner("🧾 Generando factura..."):
                    try:
                        from src.utils.presupuesto_cleaner import get_presupuesto_final_limpio
                        from src.utils.invoice_generator import generate_invoice_from_budget

                        presupuesto_limpio = get_presupuesto_final_limpio(st.session_state.messages)
                        factura_texto = generate_invoice_from_budget(presupuesto_limpio)
                        st.session_state.invoice_text = factura_texto
                        st.session_state.invoice_pdf_bytes = None
                        st.markdown("### 🧾 Factura generada")
                        st.markdown(factura_texto)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            if st.session_state.invoice_text:
                if st.button("📄 Crear PDF factura", type="secondary", key="create_invoice_pdf"):
                    try:
                        pdf_bytes = create_invoice_pdf(st.session_state.invoice_text)
                        st.session_state.invoice_pdf_bytes = pdf_bytes
                        st.success("✅ PDF creado")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

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
    <small>Asistente Empresarial v2.0 | Agente Autónomo Conversacional 🤖</small>
</div>
""", unsafe_allow_html=True)
