from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from records.models import InformationRecord

from .forms import DocumentUploadForm
from .models import Document


@login_required
def document_list(request):
    documents = Document.objects.select_related('record', 'uploaded_by').order_by('-uploaded_at')
    return render(request, 'documents/document_list.html', {'documents': documents})


@login_required
def upload_document(request, record_id):
    record = get_object_or_404(InformationRecord, pk=record_id)
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.record = record
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('record_detail', pk=record.pk)
    else:
        form = DocumentUploadForm()
    return render(request, 'documents/document_upload.html', {'record': record, 'form': form})


@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    response = FileResponse(document.file.open('rb'), as_attachment=True, filename=document.file.name.split('/')[-1])
    return response


@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    record_pk = document.record_id
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
    return redirect('record_detail', pk=record_pk)
