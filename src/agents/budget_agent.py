from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.llm_setup import get_llm

class BudgetCalculatorAgent:
    """Agente autónomo para calcular presupuestos de pintura"""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.tools = self._create_tools()
        self.agent_executor = None
        
    def _create_tools(self):
        """Define las herramientas disponibles para el agente"""
        
        def calculate_paint_needed(surface_area: str) -> str:
            """
            Calcula la cantidad de pintura necesaria en litros.
            Args:
                surface_area: Superficie en metros cuadrados (ejemplo: "120")
            Returns:
                Cantidad de pintura en litros
            """
            try:
                area = float(surface_area)
                # Rendimiento promedio: 1L cubre ~10m² (2 capas)
                liters = (area / 10) * 2
                return f"Para {area}m² necesitas aproximadamente {liters:.1f} litros de pintura (considerando 2 capas)"
            except:
                return "Error: Por favor proporciona un número válido de metros cuadrados"
        
        def get_paint_price(paint_type: str) -> str:
            """
            Obtiene el precio por litro según el tipo de pintura.
            Args:
                paint_type: Tipo de pintura (interior, exterior, premium, economica)
            Returns:
                Precio por litro en euros
            """
            prices = {
                "interior": 15.0,
                "exterior": 22.0,
                "premium": 28.0,
                "economica": 10.0,
                "estandar": 15.0
            }
            paint_type_lower = paint_type.lower()
            for key, price in prices.items():
                if key in paint_type_lower:
                    return f"Pintura {paint_type}: {price}€/litro"
            return "Pintura estándar: 15€/litro"
        
        def calculate_labor_cost(surface_area: str, complexity: str = "media") -> str:
            """
            Calcula el coste de mano de obra.
            Args:
                surface_area: Superficie en metros cuadrados
                complexity: Complejidad del trabajo (baja, media, alta)
            Returns:
                Coste estimado de mano de obra
            """
            try:
                area = float(surface_area)
                complexity_lower = complexity.lower()
                
                # Precio base por m²
                if "baja" in complexity_lower:
                    price_per_m2 = 8.0
                elif "alta" in complexity_lower:
                    price_per_m2 = 15.0
                else:  # media
                    price_per_m2 = 12.0
                
                labor_cost = area * price_per_m2
                return f"Mano de obra para {area}m² (complejidad {complexity}): {labor_cost:.2f}€"
            except:
                return "Error: Proporciona metros cuadrados válidos"
        
        # Crear las herramientas
        tools = [
            Tool(
                name="calcular_pintura_necesaria",
                func=calculate_paint_needed,
                description="Calcula cuántos litros de pintura se necesitan dado los metros cuadrados a pintar. Input: metros cuadrados como string (ej: '120')"
            ),
            Tool(
                name="obtener_precio_pintura",
                func=get_paint_price,
                description="Obtiene el precio por litro de pintura según el tipo. Input: tipo de pintura como string (interior, exterior, premium, economica)"
            ),
            Tool(
                name="calcular_mano_obra",
                func=calculate_labor_cost,
                description="Calcula el coste de mano de obra según superficie y complejidad. Input: superficie en m² y complejidad (baja/media/alta) separados por coma"
            )
        ]
        
        return tools
    
    def setup_agent(self):
        """Configura el agente con system prompt"""
        
        system_prompt = """Eres un asistente experto en presupuestos para una empresa de pinturas.

Tu trabajo es ayudar a calcular presupuestos de forma precisa y profesional.

Cuando un cliente te pida un presupuesto:
1. PRIMERO identifica qué información necesitas (metros cuadrados, tipo de pintura, complejidad)
2. Si falta información, pregunta amablemente al cliente
3. Usa las herramientas disponibles para calcular:
   - Cantidad de pintura necesaria
   - Precio de la pintura según tipo
   - Coste de mano de obra
4. Presenta un presupuesto detallado y claro con:
   - Desglose de materiales (pintura)
   - Desglose de mano de obra
   - Coste total
5. Sé amable y profesional

IMPORTANTE: 
- Siempre usa las herramientas para hacer cálculos, NO hagas cálculos mentales
- Si el cliente no especifica tipo de pintura, pregunta
- Si no especifica complejidad, asume complejidad media
- Redondea los costes finales a 2 decimales

Ejemplo de buena respuesta:
"Perfecto, déjame calcular el presupuesto para tu proyecto...
[usa herramientas]
**Presupuesto Detallado:**
- Materiales (pintura): XXX€
- Mano de obra: XXX€
- **Total: XXX€**"
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Crear el agente
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Crear el executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        print("✅ Agente autónomo de presupuestos configurado")
        return self.agent_executor
    
    def generate_budget(self, user_input: str):
        """Genera un presupuesto basándose en la entrada del usuario"""
        if not self.agent_executor:
            self.setup_agent()
        
        result = self.agent_executor.invoke({"input": user_input})
        return result["output"]
