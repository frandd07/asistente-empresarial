from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from datetime import datetime


class PresupuestoPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_styles()

    def _create_styles(self):
        # Estilo para el contenido del presupuesto
        self.styles.add(ParagraphStyle(
            name='PresupuestoContent',
            fontSize=10,
            leading=14,
            alignment=0,
            textColor=colors.HexColor('#1F2937'),
            fontName='Courier',
            spaceBefore=2,
            spaceAfter=2
        ))

    def generate_presupuesto_pdf(self, presupuesto_text: str, filename="presupuesto.pdf"):
        """
        Genera un PDF a partir de un texto de presupuesto ya limpio y calculado
        
        Args:
            presupuesto_text: Texto del presupuesto completo y limpio
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40,
            title="Presupuesto de Pintura"
        )
        
        elements = []
        
        # Fecha de emisión
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"<b>Documento emitido el:</b> {fecha}", self.styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Contenido del presupuesto
        if presupuesto_text:
            # Dividir en líneas y renderizar cada una
            lines = presupuesto_text.split('\n')
            for line in lines:
                if line.strip():
                    # Escapar caracteres especiales para reportlab
                    line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    elements.append(Paragraph(line_escaped, self.styles['PresupuestoContent']))
                else:
                    elements.append(Spacer(1, 5))
        else:
            elements.append(Paragraph("No se pudo generar el presupuesto.", self.styles['Normal']))
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


def create_presupuesto_pdf(presupuesto_text: str) -> bytes:
    """Función auxiliar para generar PDF desde texto limpio"""
    generator = PresupuestoPDFGenerator()
    return generator.generate_presupuesto_pdf(presupuesto_text)
