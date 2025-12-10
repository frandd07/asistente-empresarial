from langchain_openai import ChatOpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME, TEMPERATURE
from src.monitoring import get_langfuse_callback

def get_llm(temperature=TEMPERATURE):
    """Configura y retorna el LLM con OpenRouter y callbacks de Langfuse"""
    langfuse_handler = get_langfuse_callback()
    
    return ChatOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        model=MODEL_NAME,
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",  # Para Streamlit
        },
        callbacks=[langfuse_handler] if langfuse_handler else []
    )
