from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Agreement
from listings.models import Listing
from .forms import AgreementForm
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from .utils import generate_agreement_pdf

# PDF generation imports
import tempfile
import os
from common.utils import notify 

# We'll try using WeasyPrint; import inside function to handle optional dependency.

@login_required
def start_agreement(request, inquiry_id):
    """
    Create an Agreement record initiated from an Inquiry (chat).
    Assumes you pass tenant and owner information via inquiry.
    """
    from chat.models import Inquiry
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    listing = inquiry.listing

    # who is tenant? the one who expressed interest (from_user)
    tenant = inquiry.from_user
    owner = inquiry.to_user

    # prevent duplicates: one active agreement per inquiry/listing pair
    agreement, created = Agreement.objects.get_or_create(
        listing=listing,
        tenant=tenant,
        owner=owner,
        defaults={}
    )
    return redirect('agreements:fill_agreement', agreement_id=agreement.id)


@login_required
def fill_agreement(request, agreement_id):
    agreement = get_object_or_404(Agreement, id=agreement_id)

    # security: only tenant or owner can fill
    if request.user not in [agreement.tenant, agreement.owner]:
        messages.error(request, "You don't have permission to access this agreement.")
        return redirect('chat:inbox')

    if request.method == 'POST':
        form = AgreementForm(request.POST, instance=agreement)
        if form.is_valid():
            form.save()
            # mark which user submitted
            if request.user == agreement.tenant:
                agreement.tenant_submitted = True
            if request.user == agreement.owner:
                agreement.owner_submitted = True
            agreement.save()

            messages.success(request, "Agreement details saved.")
            # if both submitted, generate pdf
            if agreement.both_submitted():
                generate_agreement_pdf(agreement)
                agreement.status = 'completed'
                agreement.save()
                # 🔔 SEND NOTIFICATIONS TO BOTH PARTIES
                notify(
                    user=agreement.tenant,
                    message="Your room agreement is ready for download.",
                    link=f"/agreements/view/{agreement.id}/"
                )

                notify(
                    user=agreement.owner,
                    message="Room agreement completed successfully.",
                    link=f"/agreements/view/{agreement.id}/"
                )
                messages.success(request, "Agreement completed and PDF generated.")
                return redirect('agreements:view_agreement', agreement_id=agreement.id)

            return redirect('agreements:fill_agreement', agreement_id=agreement.id)
    else:
        form = AgreementForm(instance=agreement)

    return render(request, 'agreements/fill_agreement.html', {
        'agreement': agreement,
        'form': form
    })


@login_required
def view_agreement(request, agreement_id):
    agreement = get_object_or_404(Agreement, id=agreement_id)
    if request.user not in [agreement.tenant, agreement.owner]:
        messages.error(request, "Not authorized.")
        return redirect('chat:inbox')

    return render(request, 'agreements/view_agreement.html', {'agreement': agreement})


@login_required
def download_agreement(request, agreement_id):
    agreement = get_object_or_404(Agreement, id=agreement_id)
    if request.user not in [agreement.tenant, agreement.owner]:
        messages.error(request, "Not authorized.")
        return redirect('chat:inbox')

    if not agreement.pdf_file:
        messages.error(request, "Agreement PDF not generated yet.")
        return redirect('agreements:view_agreement', agreement_id=agreement.id)

    from django.http import FileResponse
    response = FileResponse(agreement.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="agreement-{agreement.id}.pdf"'
    return response
