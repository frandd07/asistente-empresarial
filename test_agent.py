from src.agents.budget_agent import BudgetCalculatorAgent

def test_budget_agent():
    print("🤖 Inicializando agente autónomo de presupuestos...\n")
    agent = BudgetCalculatorAgent()
    
    # Test 1: Presupuesto completo
    print("="*60)
    print("Test 1: Presupuesto con toda la información")
    print("="*60)
    query1 = "Necesito un presupuesto para pintar 150 m² de interior con pintura premium"
    print(f"Usuario: {query1}\n")
    response1 = agent.generate_budget(query1)
    print(f"\nAgente: {response1}\n")
    
    # Test 2: Presupuesto con información parcial
    print("="*60)
    print("Test 2: Presupuesto con información parcial")
    print("="*60)
    query2 = "¿Cuánto costaría pintar una habitación de 45 metros cuadrados?"
    print(f"Usuario: {query2}\n")
    response2 = agent.generate_budget(query2)
    print(f"\nAgente: {response2}\n")
    
    # Test 3: Proyecto complejo
    print("="*60)
    print("Test 3: Proyecto complejo con alta complejidad")
    print("="*60)
    query3 = "Presupuesto para fachada exterior de 200m² con complejidad alta"
    print(f"Usuario: {query3}\n")
    response3 = agent.generate_budget(query3)
    print(f"\nAgente: {response3}\n")

if __name__ == "__main__":
    test_budget_agent()
