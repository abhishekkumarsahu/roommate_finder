from django.template.loader import render_to_string
from django.conf import settings
import os
import tempfile

def mask_aadhaar(aadhaar):
    if not aadhaar:
        return ''
    s = str(aadhaar)
    # show only last 4 digits, mask rest
    return 'XXXX-XXXX-' + s[-4:]

def generate_agreement_pdf(agreement):
    """
    Generates PDF for the given Agreement.
    Tries to use WeasyPrint; falls back to ReportLab if unavailable.
    """
    context = {
        'agreement': agreement,
        'listing': agreement.listing,
        'tenant': agreement.tenant,
        'owner': agreement.owner,
        'mask_aadhaar': mask_aadhaar,
    }

    # Render HTML
    html_string = render_to_string('agreements/agreement_template.html', context)

    # Try WeasyPrint
    try:
        from weasyprint import HTML, CSS
        # we can include a basic CSS file or inline styles
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(tmp_fd)
        HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(tmp_path)

        # save to agreement.pdf_file
        with open(tmp_path, 'rb') as fh:
            from django.core.files.base import File
            agreement.pdf_file.save(os.path.basename(tmp_path), File(fh), save=True)

        os.remove(tmp_path)
        return True

    except Exception as e:
        # Fallback to ReportLab (simpler)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(tmp_fd)
            c = canvas.Canvas(tmp_path, pagesize=A4)
            textobject = c.beginText(40, 800)
            textobject.setFont("Helvetica", 11)
            lines = [
                f"Room Agreement - {agreement.listing.title}",
                f"Owner: {agreement.owner.full_name} ({mask_aadhaar(agreement.owner.aadhaar_number)})",
                f"Tenant: {agreement.tenant.full_name} ({mask_aadhaar(agreement.tenant.aadhaar_number)})",
                f"Rent: {agreement.rent}",
                f"Deposit: {agreement.deposit}",
                f"Start Date: {agreement.start_date}",
                f"End Date: {agreement.end_date}",
                "",
                "Clauses:",
                agreement.clauses or "None",
            ]
            for line in lines:
                textobject.textLine(str(line))
            c.drawText(textobject)
            c.showPage()
            c.save()

            with open(tmp_path, 'rb') as fh:
                from django.core.files.base import File
                agreement.pdf_file.save(os.path.basename(tmp_path), File(fh), save=True)
            os.remove(tmp_path)
            return True

        except Exception as e2:
            # If both methods fail, log and return False
            import logging
            logging.exception("PDF generation failed: %s | %s" % (e, e2))
            return False
