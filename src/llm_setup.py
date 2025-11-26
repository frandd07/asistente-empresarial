from langchain_openai import ChatOpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME

def get_llm(temperature=0.7):
    """Configura y retorna el LLM con OpenRouter"""
    return ChatOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        model=MODEL_NAME,
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",  # Para Streamlit
        }
    )
