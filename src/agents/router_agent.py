from src.llm_setup import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RouterAgent:
    """
    Un agente simple que clasifica la intención del usuario para dirigir la
    solicitud al agente o herramienta adecuada.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0)
        self.prompt_template = self._create_prompt_template()
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def _create_prompt_template(self):
        """
        Crea el prompt para el agente clasificador.
        """
        prompt = """
Tu única tarea es clasificar la intención del usuario en una de las siguientes categorías.
Responde únicamente con una sola palabra, sin explicaciones ni saludos.

Las categorías son:
- 'presupuesto': Si el usuario quiere crear, generar o solicitar un presupuesto.
- 'historial': Si el usuario pregunta sobre clientes, trabajos pasados, facturas o presupuestos antiguos.
- 'margenes': Si el usuario pregunta sobre análisis de precios, costes o márgenes de beneficio.
- 'aceptar_presupuesto': Si el usuario indica que acepta el presupuesto actual y desea convertirlo en factura.
- 'marcar_pagada': Si el usuario indica que una factura ha sido pagada.
- 'general': Si es un saludo, una conversación general o cualquier otra cosa no clasificable.

Ejemplos:
Usuario: "Hola, necesito un presupuesto para pintar 100m2"
Respuesta: presupuesto

Usuario: "¿cuánto le cobramos a juan pérez la última vez?"
Respuesta: historial

Usuario: "merece la pena este trabajo con un margen del 25%?"
Respuesta: margenes

Usuario: "acepto el presupuesto que me has dado"
Respuesta: aceptar_presupuesto

Usuario: "la factura del presupuesto PRES-20231128123456 ya está pagada"
Respuesta: marcar_pagada

Usuario: "gracias"
Respuesta: general

Usuario: "buenos días"
Respuesta: general

Ahora, clasifica la siguiente entrada del usuario.
Recuerda: responde solo con una de las categorías.

Usuario: "{user_input}"
Respuesta:""" 
        return ChatPromptTemplate.from_template(prompt)

    def route(self, user_input: str) -> str:
        """
        Clasifica la entrada del usuario y devuelve la categoría.
        """
        try:
            # .invoke espera un diccionario, pasamos el input del usuario
            result = self.chain.invoke({"user_input": user_input})
            # Limpiamos espacios en blanco o nuevas líneas
            return result.strip().lower()
        except Exception as e:
            print(f"Error al enrutar la solicitud: {e}")
            return "general"

if __name__ == '__main__':
    # Ejemplo de uso
    router = RouterAgent()
    
    test_inputs = [
        "Quiero un presupuesto para mi oficina",
        "dame el historial de Ana de Armas",
        "es rentable pintar una fachada de 200m2 por 2000 euros?",
        "hola que tal",
        "adios",
        "generar presupuesto para 50m2 cliente 'Pepe'"
    ]
    
    for text in test_inputs:
        route = router.route(text)
        print(f"Input: '{text}' -> Ruta: '{route}'")

