from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import chromadb
from chromadb.api.client import SharedSystemClient

# Limpiar cache interna de Chroma para evitar errores de tenant
SharedSystemClient.clear_system_cache()


class CustomerHistoryVectorStore:
    def __init__(self, markdown_path="data/customer_history.md", persist_directory="./chroma_db"):
        self.markdown_path = markdown_path
        self.persist_directory = persist_directory
        self.vectorstore = None
        
        # Deshabilitar telemetría de ChromaDB
        chromadb.config.Settings(anonymized_telemetry=False)
        
    def load_and_split_documents(self):
        """Carga el documento markdown y lo divide en chunks"""
        loader = TextLoader(self.markdown_path, encoding='utf-8')
        documents = loader.load()
        
        markdown_splitter = MarkdownTextSplitter(
            chunk_size=500,
            chunk_overlap=50
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
        documents = self.load_and_split_documents()
        embeddings = self.get_embeddings()
        
        # Crear configuración de ChromaDB sin telemetría
        chroma_settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=self.persist_directory,
            collection_name="customer_history",
            client_settings=chroma_settings
        )
        
        print(f"✅ Vector store creado en {self.persist_directory}")
        return self.vectorstore
    
    def load_vectorstore(self):
        """Carga un vector store existente"""
        if os.path.exists(self.persist_directory):
            embeddings = self.get_embeddings()
            
            chroma_settings = chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name="customer_history",
                client_settings=chroma_settings
            )
            print("✅ Vector store cargado desde disco")
            return self.vectorstore
        else:
            print("⚠️ No existe vector store, creando uno nuevo...")
            return self.create_vectorstore()
    
    def get_retriever(self, k=3):
        """Obtiene el retriever configurado"""
        if not self.vectorstore:
            self.load_vectorstore()
        
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
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
    vs = CustomerHistoryVectorStore(
        markdown_path=markdown_path,
        persist_directory=persist_directory,
    )
    vs.create_vectorstore()
    return True
