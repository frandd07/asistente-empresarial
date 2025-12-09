from src.llm_setup import get_llm
from src.config import TEMPERATURE_AUTONOMOUS


class PriceMarginAgent:
    def __init__(self):
        self.llm = get_llm(temperature=TEMPERATURE_AUTONOMOUS)

    def analyze_margins(
        self,
        history_text: str,
        job_description: str,
        target_margin_percent: float
    ) -> str:
        """
        Analiza el historial de presupuestos y sugiere precios mínimos
        para el trabajo descrito, manteniendo al menos el margen objetivo.
        """
        prompt = f"""
Eres un asesor de precios y márgenes para una empresa de pintura en España.

Tienes:
- Un HISTORIAL de presupuestos y trabajos realizados (en formato texto Markdown).
- Una DESCRIPCIÓN de un nuevo trabajo.
- Un MARGEN objetivo mínimo de beneficio del {target_margin_percent:.1f}% sobre el coste estimado.

TAREAS:
1. Analiza rápidamente el historial para entender:
   - Tipos de trabajo habituales (interior, exterior, fachadas, comunidades, etc.).
   - Rangos de precios por m² o por trabajo cuando se pueda deducir.
2. A partir de la descripción del nuevo trabajo, estima:
   - Coste aproximado (material + mano de obra) basándote en el histórico.
   - Precio de venta recomendado que asegure al menos el margen del {target_margin_percent:.1f}%.
3. Si el cliente ya tiene un precio en mente (si aparece en la descripción), indica:
   - Si ese precio está por debajo del margen objetivo.
   - Cuál sería el precio mínimo seguro.
4. Devuelve siempre:
   - Un resumen de cómo están los márgenes en el historial.
   - Un precio mínimo recomendado para este trabajo.
   - Consejos claros (subir precio, no bajar de X, ofrecer descuento máximo Y, etc.).

NO inventes datos que contradigan el historial; si el histórico es pobre, trabaja con rangos aproximados.

HISTORIAL DE PRESUPUESTOS:
--------------------------
{history_text}

NUEVO TRABAJO A ANALIZAR:
-------------------------
{job_description}
"""
        resp = self.llm.invoke(prompt)
        return resp.content.strip()
