import os
try:
    from langfuse.langchain import CallbackHandler
except ImportError:
    print("⚠️ Could not import CallbackHandler from langfuse.langchain. Please ensure langfuse is installed correctly.")
    CallbackHandler = None


def get_langfuse_callback():
    """
    Returns a Langfuse CallbackHandler if credentials are set in environment variables.
    Otherwise returns None.
    
    Las credenciales se leen automáticamente de las variables de entorno:
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_BASE_URL (opcional, default: https://cloud.langfuse.com)
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if public_key and secret_key and CallbackHandler:
        try:
            # El CallbackHandler lee automáticamente las variables de entorno
            # No necesita argumentos en el constructor
            return CallbackHandler()
        except Exception as e:
            print(f"⚠️ Error initializing Langfuse: {e}")
            return None
    return None
