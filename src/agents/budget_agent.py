from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.llm_setup import get_llm

class BudgetCalculatorAgent:
    """
    Agente conversacional para RECOPILAR DATOS de un presupuesto.
    Su única misión es hablar con el usuario hasta tener todos los datos necesarios.
    Cuando los tiene, devuelve un JSON limpio.
    """
    
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.agent_executor = None
        
    def _create_tools(self):
        """Este agente ya no usa herramientas de cálculo. Su única función es conversar."""
        return []
    
    def setup_agent(self):
        """Configura el agente con el nuevo system prompt enfocado en devolver JSON."""
        
        system_prompt = """Eres un asistente experto en recopilar información para crear presupuestos de "PINTURAS PROFESIONALES S.L.".

TU ÚNICA MISIÓN:
Conversar con el cliente hasta obtener TODOS los datos necesarios. Una vez que los tengas, tu ÚLTIMA respuesta debe ser ÚNICAMENTE un JSON con la información.

DATOS OBLIGATORIOS A RECOPILAR:
- `cliente_nombre`: Nombre completo del cliente o empresa.
- `cliente_nif`: NIF o CIF del cliente.
- `cliente_direccion`: Dirección completa donde se realizará el trabajo.
- `area_m2`: Área a pintar en metros cuadrados (solo el número, tipo float).
- `tipo_pintura`: Tipo de pintura (ej: "plástica", "acrílica"). Si no se especifica, asume "plástica".
- `tipo_trabajo`: Tipo de trabajo (ej: "interior", "exterior", "fachada"). Si no se especifica, asume "interior".

REGLAS CLAVE:
1. Siempre saluda amablemente al inicio de la conversación.
2. Si falta algún dato de la lista, pregunta amablemente SOLO por la información que falta.
3. NO inventes ningún dato. Si el usuario no te lo proporciona, pídeselo.
4. CUANDO TENGAS TODOS LOS DATOS, y solo entonces, genera el JSON. Este debe ser tu ÚLTIMA respuesta y no debe contener texto adicional.
5. El JSON debe estar limpio, sin `json` ni marcas de código alrededor (NO ```json ... ```, SOLO el JSON).
6. Asegúrate de que `area_m2` sea un número flotante (ej. 80.0), no un string.
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Este agente ya no necesita tools, pero la función las espera
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=[],
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=[],
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15
        )
        
        print("✅ Agente RECOPILADOR de datos configurado.")
        return self.agent_executor

    def generate_budget(self, user_input: str, chat_history=None):
        """
        Genera una respuesta conversacional o un JSON cuando tiene todos los datos.
        """
        if not self.agent_executor:
            self.setup_agent()
        
        inputs = {"input": user_input}
        if chat_history:
            inputs["chat_history"] = chat_history
            
        result = self.agent_executor.invoke(inputs)
        return result["output"]
