from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from documents.models import Document
from records.models import InformationRecord

from .forms import ProfileForm, RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account was created successfully.')
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard_redirect(request):
    return redirect('dashboard')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    user_records = InformationRecord.objects.filter(created_by=request.user)
    context = {
        'form': form,
        'record_count': user_records.count(),
        'active_record_count': user_records.filter(status='active').count(),
        'draft_record_count': user_records.filter(status='draft').count(),
        'archived_record_count': user_records.filter(status='archived').count(),
        'document_count': Document.objects.filter(uploaded_by=request.user).count(),
    }
    return render(request, 'accounts/profile.html', context)
