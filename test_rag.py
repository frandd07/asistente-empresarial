from src.rag.retriever import CustomerHistoryRAG

def test_rag_system():
    print("🔧 Inicializando sistema RAG...")
    rag = CustomerHistoryRAG()
    
    # Test 1: Consulta por cliente específico
    print("\n" + "="*50)
    print("Test 1: Búsqueda por cliente")
    print("="*50)
    question1 = "¿Qué trabajo se le hizo a María González?"
    answer1 = rag.query_simple(question1)
    print(f"Pregunta: {question1}")
    print(f"Respuesta: {answer1}\n")
    
    # Test 2: Consulta por tipo de pintura
    print("="*50)
    print("Test 2: Búsqueda por pintura")
    print("="*50)
    question2 = "¿Qué clientes han usado pintura Jotun?"
    answer2 = rag.query_simple(question2)
    print(f"Pregunta: {question2}")
    print(f"Respuesta: {answer2}\n")
    
    # Test 3: Consulta por coste
    print("="*50)
    print("Test 3: Búsqueda por presupuesto")
    print("="*50)
    question3 = "¿Cuánto costó el trabajo de Carlos Ruiz?"
    answer3 = rag.query_simple(question3)
    print(f"Pregunta: {question3}")
    print(f"Respuesta: {answer3}\n")

if __name__ == "__main__":
    test_rag_system()
