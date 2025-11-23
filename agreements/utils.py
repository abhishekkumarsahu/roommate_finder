from django.template.loader import render_to_string
from django.conf import settings
from io import BytesIO
import os
from xhtml2pdf import pisa
from django.core.files.base import ContentFile


def generate_pdf_from_html(html_content, output_path):
    """
    Uses xhtml2pdf to generate a PDF file from HTML content.
    """
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("utf-8")), dest=result)

    if not pdf.err:
        with open(output_path, "wb") as output_file:
            output_file.write(result.getvalue())
        return True
    return False


def generate_agreement_pdf(agreement):
    """
    Generates PDF using the custom styled agreement_template.html
    """

    context = {
        "agreement": agreement,
        "listing": agreement.listing,
        "tenant": agreement.tenant,
        "owner": agreement.owner,
    }

    # Render HTML template
    html_string = render_to_string("agreements/agreement_template.html", context)

    # Temp PDF path
    pdf_filename = f"agreement-{agreement.id}.pdf"
    pdf_folder = os.path.join(settings.MEDIA_ROOT, "agreements", f"listing-{agreement.listing.id}")
    os.makedirs(pdf_folder, exist_ok=True)

    pdf_path = os.path.join(pdf_folder, pdf_filename)

    # Generate PDF
    success = generate_pdf_from_html(html_string, pdf_path)

    if success:
        # Save PDF to model FileField
        with open(pdf_path, "rb") as pdf_file:
            agreement.pdf_file.save(pdf_filename, ContentFile(pdf_file.read()), save=True)
        return True

    return False
