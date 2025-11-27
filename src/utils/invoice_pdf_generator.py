from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from datetime import datetime


class InvoicePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_styles()

    def _create_styles(self):
        self.styles.add(ParagraphStyle(
            name="InvoiceTitle",
            fontSize=20,
            leading=24,
            alignment=1,
            textColor=colors.HexColor("#111827"),
            spaceAfter=20,
            fontName="Helvetica-Bold",
        ))
        self.styles.add(ParagraphStyle(
            name="InvoiceContent",
            fontSize=10,
            leading=14,
            alignment=0,
            textColor=colors.HexColor("#111827"),
            fontName="Courier",
            spaceBefore=1,
            spaceAfter=1,
        ))

    def generate_invoice_pdf(self, invoice_text: str) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
            title="Factura de Pintura",
        )

        elements = []
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph("FACTURA DE SERVICIOS DE PINTURA", self.styles["InvoiceTitle"]))
        elements.append(Paragraph(f"Documento generado el: {fecha}", self.styles["Normal"]))
        elements.append(Spacer(1, 15))

        for line in invoice_text.split("\n"):
            line = line.rstrip()
            if not line:
                elements.append(Spacer(1, 5))
                continue
            safe_line = (line
                         .replace("&", "&amp;")
                         .replace("<", "&lt;")
                         .replace(">", "&gt;"))
            elements.append(Paragraph(safe_line, self.styles["InvoiceContent"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


def create_invoice_pdf(invoice_text: str) -> bytes:
    gen = InvoicePDFGenerator()
    return gen.generate_invoice_pdf(invoice_text)
