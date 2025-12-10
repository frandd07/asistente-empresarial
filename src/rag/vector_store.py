from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import chromadb
from chromadb.config import Settings
import shutil

class CustomerHistoryVectorStore:
    def __init__(self, markdown_path="data/customer_history.md", persist_directory="./chroma_db"):
        self.markdown_path = markdown_path
        self.persist_directory = persist_directory
        self.vectorstore = None
    
    def load_and_split_documents(self):
        """Carga el documento markdown y lo divide en chunks"""
        if not os.path.exists(self.markdown_path):
            print(f"⚠️ Archivo {self.markdown_path} no existe. Creando uno vacío...")
            os.makedirs(os.path.dirname(self.markdown_path) or ".", exist_ok=True)
            with open(self.markdown_path, 'w', encoding='utf-8') as f:
                f.write("# Historial de Clientes\n\n(Sin registros aún)\n")
        
        loader = TextLoader(self.markdown_path, encoding='utf-8')
        documents = loader.load()
        
        markdown_splitter = MarkdownTextSplitter(
            chunk_size=1000,  # Aumentado de 500 para más contexto
            chunk_overlap=200  # Aumentado de 50 para mejor coherencia
        )
        
        split_docs = markdown_splitter.split_documents(documents)
        print(f"✅ Documento cargado: {len(split_docs)} chunks creados")
        return split_docs
    
    def get_embeddings(self):
        """Retorna embeddings locales gratuitos usando HuggingFace"""
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embeddings locales cargados (multilingüe)")
        return embeddings
    
    def create_vectorstore(self):
        """Crea el vector store con ChromaDB y embeddings locales"""
        try:
            # Limpiar el directorio si existe para evitar problemas de tenant
            if os.path.exists(self.persist_directory):
                print(f"🧹 Limpiando vector store anterior en {self.persist_directory}...")
                try:
                    shutil.rmtree(self.persist_directory)
                except OSError as e:
                    print(f"⚠️ No se pudo eliminar el directorio (posible bloqueo de Windows): {e}")
            
            documents = self.load_and_split_documents()
            embeddings = self.get_embeddings()
            
            # Crear configuración de ChromaDB sin telemetría
            chroma_settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
            
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Crear cliente de Chroma manualmente
            client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=chroma_settings
            )
            
            # Eliminar colección si existe
            try:
                client.delete_collection("customer_history")
                print("🗑️ Colección anterior eliminada")
            except:
                pass
            
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=self.persist_directory,
                collection_name="customer_history",
                client=client
            )
            
            print(f"✅ Vector store creado en {self.persist_directory}")
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Error creando vector store: {e}")
            raise
    
    def load_vectorstore(self):
        """Carga un vector store existente o lo reconstruye si el archivo fuente ha cambiado"""
        try:
            # Verificar si existe el archivo de historial
            if not os.path.exists(self.markdown_path):
                print(f"⚠️ Archivo {self.markdown_path} no existe. Creando uno vacío...")
                os.makedirs(os.path.dirname(self.markdown_path) or ".", exist_ok=True)
                with open(self.markdown_path, 'w', encoding='utf-8') as f:
                    f.write("# Historial de Clientes\n\n(Sin registros aún)\n")
            
            # Obtener timestamp del archivo de historial
            history_mtime = os.path.getmtime(self.markdown_path)
            
            # Verificar si existe el vector store y si es más antiguo que el archivo de historial
            should_rebuild = False
            
            if os.path.exists(self.persist_directory):
                try:
                    # Obtener timestamp del directorio del vector store
                    vectorstore_mtime = os.path.getmtime(self.persist_directory)
                    
                    # Si el historial es más nuevo, necesitamos reconstruir
                    if history_mtime > vectorstore_mtime:
                        print(f"📝 Detectado cambio en {self.markdown_path}, reconstruyendo vector store...")
                        should_rebuild = True
                except:
                    should_rebuild = True
            else:
                print("⚠️ No existe vector store, creando uno nuevo...")
                should_rebuild = True
            
            # Si necesitamos reconstruir, hacerlo
            if should_rebuild:
                return self.create_vectorstore()
            
            # Si no, cargar el existente
            embeddings = self.get_embeddings()
            
            chroma_settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
            
            # Crear cliente de Chroma
            client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=chroma_settings
            )
            
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name="customer_history",
                client=client
            )
            
            print("✅ Vector store cargado desde disco")
            return self.vectorstore
                
        except Exception as e:
            print(f"⚠️ Error cargando vector store: {e}")
            print("🔄 Recreando vector store...")
            return self.create_vectorstore()
    
    def get_retriever(self, k=8):  # Aumentado de 5 a 8
        """Obtiene el retriever configurado"""
        if not self.vectorstore:
            self.load_vectorstore()
        
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",  # Cambiado de mmr a similarity para más relevancia
            search_kwargs={"k": k}
        )
        
        return retriever
def rebuild_customer_history_vectorstore(
    markdown_path: str = "data/customer_history.md",
    persist_directory: str = "./chroma_db",
):
    """
    Helper para reconstruir el vector store de historial de clientes.
    Se puede llamar desde app.py cada vez que se guarde un nuevo presupuesto.
    """
    try:
        vs = CustomerHistoryVectorStore(
            markdown_path=markdown_path,
            persist_directory=persist_directory,
        )
        vs.create_vectorstore()
        print("✅ Vector store reconstruido exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error reconstruyendo vector store: {e}")
        return False
