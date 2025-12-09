"""
Utilidades para generación de PDFs
"""
from typing import List, Dict


def generate_pdf_items(presupuesto_dict: dict) -> List[Dict[str, str]]:
    """
    Genera la lista de items para incluir en un PDF de presupuesto o factura.
    
    Esta función centraliza la lógica de construcción de items que se repite
    en múltiples lugares del código.
    
    Args:
        presupuesto_dict: Diccionario completo del presupuesto con estructura:
            {
                "detalles_trabajo": {
                    "area_m2": float,
                    "tipo_pintura": str,
                    "tipo_trabajo": str
                },
                "presupuesto": {
                    "costo_material": float,
                    "costo_mano_obra": float,
                    "costos_adicionales": {
                        "preparación": float,
                        "transporte": float,
                        "limpieza_final": float
                    }
                }
            }
    
    Returns:
        Lista de diccionarios con items formateados para el PDF
        
    Example:
        >>> presupuesto = {
        ...     "detalles_trabajo": {"area_m2": 100, "tipo_pintura": "plástica", "tipo_trabajo": "interior"},
        ...     "presupuesto": {"costo_material": 850, "costo_mano_obra": 150, 
        ...                    "costos_adicionales": {"preparación": 127.5, "transporte": 50, "limpieza_final": 30}}
        ... }
        >>> items = generate_pdf_items(presupuesto)
        >>> len(items)
        5
    """
    detalles = presupuesto_dict["detalles_trabajo"]
    presupuesto = presupuesto_dict["presupuesto"]
    
    items = [
        {
            "concepto": f"Pintura {detalles['tipo_pintura'].title()} - {detalles['tipo_trabajo'].title()}",
            "cantidad": f"{detalles['area_m2']} m²",
            "precio_unitario": f"€{presupuesto['costo_material'] / detalles['area_m2']:.2f}",
            "importe": f"€{presupuesto['costo_material']:.2f}"
        },
        {
            "concepto": "Mano de obra especializada",
            "cantidad": "1",
            "precio_unitario": f"€{presupuesto['costo_mano_obra']:.2f}",
            "importe": f"€{presupuesto['costo_mano_obra']:.2f}"
        },
        {
            "concepto": "Preparación y acabados",
            "cantidad": "1",
            "precio_unitario": f"€{presupuesto['costos_adicionales']['preparación']:.2f}",
            "importe": f"€{presupuesto['costos_adicionales']['preparación']:.2f}"
        },
        {
            "concepto": "Transporte",
            "cantidad": "1",
            "precio_unitario": f"€{presupuesto['costos_adicionales']['transporte']:.2f}",
            "importe": f"€{presupuesto['costos_adicionales']['transporte']:.2f}"
        },
        {
            "concepto": "Limpieza final",
            "cantidad": "1",
            "precio_unitario": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}",
            "importe": f"€{presupuesto['costos_adicionales']['limpieza_final']:.2f}"
        }
    ]
    
    return items
