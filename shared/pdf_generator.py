from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime
from apps.models import Order, OrderItem
from django.conf import settings

INVOICES_DIR = os.path.join(settings.BASE_DIR, 'invoices')

os.makedirs(INVOICES_DIR, exist_ok=True)

def generate_invoice_pdf(order_id: int) -> BytesIO:
    """
    Génère une facture PDF pour une commande
    """
    try:
        order = Order.objects.select_related("user").get(id=order_id)
    except Order.DoesNotExist:
        raise ValueError(f"Commande {order_id} non trouvée")
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#333333'),
        spaceAfter=30,
        alignment=1 
    )
    story.append(Paragraph("FACTURE", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    info_data = [
        ["N° Facture:", f"CMD-{order.id:05d}", "Date:", datetime.now().strftime("%d/%m/%Y")],
        ["Client:", order.user.username, "Email:", order.user.email],
        ["Statut:", order.status, "", ""]
    ]
    
    info_table = Table(info_data, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ROWBACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 1*cm))
    
    items = OrderItem.objects.filter(order=order).select_related("product")
    
    items_data = [
        ["Produit", "Quantité", "Prix Unitaire", "Montant"]
    ]
    
    for item in items:
        items_data.append([
            item.product.name,
            str(item.quantity),
            f"{float(item.unit_price_frozen):.2f} €",
            f"{float(item.quantity * item.unit_price_frozen):.2f} €"
        ])
    
    items_data.append(["", "", "TOTAL:", f"{float(order.total_amount):.2f} €"])
    
    items_table = Table(items_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUND', (0, 1), (-1, -2), colors.white),
        ('ROWBACKGROUND', (-1, -1), (-1, -1), colors.HexColor('#E8E8E8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 1*cm))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph("Merci de votre confiance!", footer_style))
    
    doc.build(story)
    
    pdf_buffer.seek(0)
    return pdf_buffer


def save_invoice_to_file(order_id: int) -> str:
    """
    Génère et sauvegarde une facture PDF sur le disque
    Retourne le chemin du fichier
    """
    pdf_buffer = generate_invoice_pdf(order_id)
    
    order = Order.objects.get(id=order_id)
    filename = f"invoice_user{order.user_id}_order{order_id}.pdf"
    filepath = os.path.join(INVOICES_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    order.invoice_file = filename
    order.save()
    
    return filepath
