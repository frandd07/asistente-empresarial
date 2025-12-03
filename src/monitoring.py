import os
try:
    from langfuse.langchain import CallbackHandler
except ImportError:
    print("⚠️ Could not import CallbackHandler from langfuse.langchain. Please ensure langfuse is installed correctly.")
    CallbackHandler = None


def get_langfuse_callback():
    """
    Returns a Langfuse CallbackHandler if credentials are set.
    Otherwise returns None.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if public_key and secret_key and CallbackHandler:
        try:
            return CallbackHandler(
                public_key=public_key,
                secret_key=secret_key,
                host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
            )
        except Exception as e:
            print(f"⚠️ Error initializing Langfuse: {e}")
            return None
    return None
