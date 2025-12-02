import shutil
import os

def reset_chroma_db():
    """Elimina completamente la base de datos vectorial corrupta"""
    chroma_path = "./chroma_db"
    
    if os.path.exists(chroma_path):
        print(f"🗑️ Eliminando {chroma_path}...")
        shutil.rmtree(chroma_path)
        print("✅ Base de datos vectorial eliminada")
    else:
        print("ℹ️ No existe base de datos vectorial")
    
    print("\n🔄 Ahora reinicia tu aplicación Streamlit")

if __name__ == "__main__":
    reset_chroma_db()
