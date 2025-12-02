from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from src.llm_setup import get_llm
from src.rag.vector_store import CustomerHistoryVectorStore

class CustomerHistoryRAG:
    def __init__(self):
        self.vectorstore = CustomerHistoryVectorStore()
        self.llm = get_llm(temperature=0.3)
        self.qa_chain = None
    
    def setup_qa_chain(self):
        """Configura la cadena de QA con RAG"""
        try:
            retriever = self.vectorstore.get_retriever(k=3)
            
            # Prompt personalizado para el contexto de empresa de pinturas
            template = """Eres un asistente de una empresa de pinturas. Tu trabajo es ayudar a consultar el historial de trabajos realizados.

Contexto de trabajos anteriores:
{context}

Pregunta: {question}

Responde de forma clara y profesional. Si la información no está en el contexto, indícalo amablemente.
Si te preguntan por un cliente específico, proporciona todos los detalles disponibles (fecha, trabajo realizado, pintura usada, coste, etc.).
IMPORTANTE: Si encuentras números de documento (como PRES-20251202193045), inclúyelos SIEMPRE en tu respuesta.

Respuesta:"""
            
            PROMPT = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            
            # Crear la cadena de RetrievalQA
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            print("✅ Cadena RAG configurada correctamente")
            return self.qa_chain
            
        except Exception as e:
            print(f"❌ Error configurando cadena RAG: {e}")
            raise
    
    def query(self, question: str):
        """Realiza una consulta al sistema RAG"""
        try:
            if not self.qa_chain:
                self.setup_qa_chain()
            
            result = self.qa_chain.invoke({"query": question})
            
            return {
                "answer": result["result"],
                "source_documents": result["source_documents"]
            }
        except Exception as e:
            print(f"❌ Error en query RAG: {e}")
            return {
                "answer": f"Error al consultar el historial: {str(e)}",
                "source_documents": []
            }
    
    def query_simple(self, question: str):
        """Consulta simplificada que solo retorna la respuesta"""
        result = self.query(question)
        return result["answer"]
