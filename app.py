import streamlit as st
from src.rag.retriever import CustomerHistoryRAG
from src.agents.budget_agent import BudgetCalculatorAgent
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
    st.markdown("El agente calculará presupuestos de forma autónoma basándose en tu descripción.")
    
    # Ejemplos de solicitudes
    with st.expander("💡 Ejemplos de solicitudes"):
        st.markdown("""
        - Necesito presupuesto para pintar 150 m² de interior con pintura premium
        - ¿Cuánto costaría pintar una habitación de 45 metros cuadrados?
        - Presupuesto para fachada exterior de 200m² con complejidad alta
        - Quiero pintar 80m² de mi casa, ¿cuánto cuesta?
        """)
    
    # Input del usuario
    request = st.text_area(
        "Describe tu proyecto:",
        placeholder="Ejemplo: Necesito presupuesto para pintar 120m² de interior",
        height=100,
        key="agent_request"
    )
    
    if st.button("🤖 Generar Presupuesto", type="primary", key="agent_button"):
        if request:
            with st.spinner("🤖 El agente está calculando tu presupuesto..."):
                try:
                    agent = initialize_agent()
                    
                    # Capturar output del agente
                    response = agent.generate_budget(request)
                    
                    # Mostrar respuesta
                    st.success("✅ Presupuesto generado")
                    st.markdown("### 💵 Tu Presupuesto:")
                    st.markdown(response)
                    
                    # Botón para descargar
                    st.download_button(
                        label="📥 Descargar presupuesto",
                        data=f"# Presupuesto\n\n**Solicitud:**\n{request}\n\n**Respuesta:**\n{response}",
                        file_name="presupuesto.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Por favor, describe tu proyecto")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Asistente Empresarial v1.0 | Powered by LangChain + OpenRouter</small>
</div>
""", unsafe_allow_html=True)
