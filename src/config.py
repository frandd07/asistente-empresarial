import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Configuración del modelo
MODEL_NAME = "google/gemini-2.5-flash"  # O el que prefieras
TEMPERATURE = 0.7
