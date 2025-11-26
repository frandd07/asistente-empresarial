from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.llm_setup import get_llm
from datetime import datetime
import random


class BudgetCalculatorAgent:
    """Agente autónomo para generar presupuestos completos"""
    
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
                liters = (area / 10) * 2
                return f"{liters:.1f}"
            except:
                return "Error en cálculo"
        
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
                "estandar": 15.0,
                "cocina": 25.0,
                "baño": 25.0
            }
            paint_type_lower = paint_type.lower()
            for key, price in prices.items():
                if key in paint_type_lower:
                    return f"{price}"
            return "15.0"
        
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
                
                if "baja" in complexity_lower:
                    price_per_m2 = 8.0
                elif "alta" in complexity_lower:
                    price_per_m2 = 15.0
                else:
                    price_per_m2 = 12.0
                
                labor_cost = area * price_per_m2
                return f"{labor_cost:.2f}"
            except:
                return "Error en cálculo"
        
        def get_current_date() -> str:
            """
            Obtiene la fecha actual para el presupuesto.
            Returns:
                Fecha actual en formato DD/MM/YYYY
            """
            return datetime.now().strftime("%d/%m/%Y")
        
        tools = [
            Tool(
                name="calcular_pintura_necesaria",
                func=calculate_paint_needed,
                description="Calcula cuántos litros de pintura se necesitan. Input: metros cuadrados como string (ej: '120'). Output: litros necesarios"
            ),
            Tool(
                name="obtener_precio_pintura",
                func=get_paint_price,
                description="Obtiene el precio por litro de pintura. Input: tipo de pintura (interior/exterior/premium). Output: precio por litro"
            ),
            Tool(
                name="calcular_mano_obra",
                func=calculate_labor_cost,
                description="Calcula coste de mano de obra. Input: 'superficie,complejidad' (ej: '120,media'). Output: coste total mano de obra"
            ),
            Tool(
                name="obtener_fecha_actual",
                func=get_current_date,
                description="Obtiene la fecha actual para el presupuesto. No requiere input. Output: fecha DD/MM/YYYY"
            )
        ]
        
        return tools
    
    def setup_agent(self):
        """Configura el agente con system prompt mejorado"""
        
        system_prompt = """Eres un asistente experto en presupuestos para "PINTURAS PROFESIONALES S.L.", empresa española de pinturas.

**DATOS DE LA EMPRESA:**
- Nombre: PINTURAS PROFESIONALES S.L.
- CIF: B12345678
- Dirección: Calle del Pintor 23, 28015 Madrid
- Teléfono: +34 910 123 456
- Email: presupuestos@pinturaspro.es

**TU MISIÓN:**
Generar presupuestos COMPLETOS y PROFESIONALES listos para entregar al cliente.

**ORDEN ESTRICTO DE RECOPILACIÓN (SIGUE ESTE ORDEN SIEMPRE):**

🔴 **PASO 1 - DATOS DEL CLIENTE (PRIORIDAD MÁXIMA):**
Antes de hacer CUALQUIER otra cosa, necesitas estos datos:
   ✅ Nombre completo del cliente (o nombre de empresa)
   ✅ NIF/CIF
   ✅ Teléfono de contacto
   ✅ Dirección COMPLETA donde se realizará el trabajo
   ✅ Email (opcional)

**Si falta ALGUNO de estos datos, pregunta PRIMERO por ellos. NO preguntes por tipo de pintura o complejidad hasta tener todos los datos del cliente.**

EJEMPLO CORRECTO:
Usuario: "Quiero presupuesto para 439 metros para Ronaldo"
Tú: "Perfecto, voy a preparar el presupuesto para pintar 439m² para Ronaldo. Para hacer un presupuesto oficial, necesito completar los datos del cliente:

1. Nombre completo: Ya tengo 'Ronaldo', ¿cuál es su apellido completo?
2. NIF/CIF: ¿Cuál es su NIF o CIF?
3. Teléfono: ¿Un teléfono donde podamos contactarle?
4. Dirección: ¿Dirección completa (calle, número, código postal, ciudad)?
5. Email: ¿Email de contacto? (opcional)

Una vez tenga estos datos, calcularé el presupuesto."

🟡 **PASO 2 - DATOS TÉCNICOS DEL PROYECTO:**
Solo DESPUÉS de tener todos los datos del cliente, pregunta:
   - ¿Interior o exterior? (Si no dice, asume interior)
   - ¿Alguna complejidad especial? (Si no dice, asume media)

🟢 **PASO 3 - CALCULAR CON HERRAMIENTAS:**
Usa TODAS estas herramientas:
   ✅ obtener_fecha_actual (para la fecha)
   ✅ calcular_pintura_necesaria (con los m²)
   ✅ obtener_precio_pintura (con el tipo)
   ✅ calcular_mano_obra (con m² y complejidad)

🔵 **PASO 4 - GENERAR PRESUPUESTO COMPLETO**

**REGLAS CRÍTICAS:**
❌ NO preguntes por tipo de pintura o complejidad antes de tener datos del cliente
❌ NO inventes NUNCA los datos del cliente (NIF, teléfono, dirección)
✅ Si falta dato del cliente, pregunta SOLO por ese dato
✅ Si no especifica tipo: usa "interior" por defecto
✅ Si no especifica complejidad: usa "media" por defecto
✅ SIEMPRE usa las 4 herramientas disponibles
✅ Presenta presupuesto completo y profesional
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15
        )
        
        print("✅ Agente de presupuestos completos configurado")
        return self.agent_executor

    def generate_budget(self, user_input: str, chat_history=None):
        """Genera un presupuesto basándose en la entrada del usuario"""
        if not self.agent_executor:
            self.setup_agent()
        
        inputs = {"input": user_input}
        if chat_history:
            inputs["chat_history"] = chat_history
            
        result = self.agent_executor.invoke(inputs)
        return result["output"]
