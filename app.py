import streamlit as st
from src.rag.retriever import CustomerHistoryRAG
from src.agents.budget_agent import BudgetCalculatorAgent
from langchain.schema import HumanMessage, AIMessage
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
        ["🔍 Consulta de Historial (RAG)", "💰 Generador de Presupuestos (Agente)"],
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
    
    # Botón para reiniciar conversación
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Reiniciar", type="secondary"):
            st.session_state.messages = []
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
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Botón para descargar conversación completa
    if st.session_state.messages:
        st.markdown("---")
        
        # Generar contenido de descarga
        download_content = "# Conversación Completa - Presupuesto\n\n"
        download_content += "════════════════════════════════════════════════\n\n"
        for msg in st.session_state.messages:
            role = "👤 USUARIO" if msg["role"] == "user" else "🤖 ASISTENTE"
            download_content += f"**{role}:**\n{msg['content']}\n\n"
            download_content += "────────────────────────────────────────────────\n\n"
        
        st.download_button(
            label="📥 Descargar conversación completa",
            data=download_content,
            file_name=f"conversacion_presupuesto_{st.session_state.messages[0]['content'][:20]}.md",
            mime="text/markdown",
            type="secondary"
        )


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Asistente Empresarial v1.0 | Powered by LangChain + OpenRouter</small>
</div>
""", unsafe_allow_html=True)
