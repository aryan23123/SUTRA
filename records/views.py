import csv
import io
import zipfile
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from documents.forms import DocumentUploadForm
from documents.models import Document

from .forms import CategoryForm, InformationRecordForm, RecordFilterForm, TagForm
from .models import Category, InformationRecord, Tag


@login_required
def dashboard(request):
    total_records = InformationRecord.objects.count()
    active_records = InformationRecord.objects.filter(status='active').count()
    draft_records = InformationRecord.objects.filter(status='draft').count()
    archived_records = InformationRecord.objects.filter(status='archived').count()
    total_categories = Category.objects.count()
    total_documents = Document.objects.count()
    recent_records = list(
        InformationRecord.objects.select_related('category', 'created_by')
        .prefetch_related('tags')
        .order_by('-updated_at')[:5]
    )
    recent_documents = list(
        Document.objects.select_related('record', 'uploaded_by').order_by('-uploaded_at')[:5]
    )
    recent_activity = [
        {
            'kind': 'record',
            'action': 'Record last updated',
            'title': record.title,
            'timestamp': record.updated_at,
            'record_id': record.pk,
        }
        for record in recent_records
    ]
    recent_activity.extend(
        {
            'kind': 'document',
            'action': 'Document uploaded',
            'title': document.title,
            'actor': (
                document.uploaded_by.get_full_name() or document.uploaded_by.username
                if document.uploaded_by
                else 'Workspace'
            ),
            'timestamp': document.uploaded_at,
            'record_id': document.record_id,
            'record_title': document.record.title,
            'document_id': document.pk,
        }
        for document in recent_documents
    )
    recent_activity.sort(key=lambda item: item['timestamp'], reverse=True)
    return render(
        request,
        'records/dashboard.html',
        {
            'total_records': total_records,
            'active_records': active_records,
            'draft_records': draft_records,
            'archived_records': archived_records,
            'total_categories': total_categories,
            'total_documents': total_documents,
            'recent_records': recent_records,
            'recent_documents': recent_documents,
            'recent_activity': recent_activity[:6],
        },
    )


def _get_filter_dict(request):
    session_filters = request.session.get('record_filters', {})
    if request.method == 'GET' and request.GET:
        filter_dict = {
            'q': request.GET.get('q', ''),
            'status': request.GET.get('status', ''),
            'category': request.GET.get('category', ''),
            'tags': list(request.GET.getlist('tags')),
        }
        request.session['record_filters'] = filter_dict
        return filter_dict

    return {
        'q': session_filters.get('q', ''),
        'status': session_filters.get('status', ''),
        'category': session_filters.get('category', ''),
        'tags': session_filters.get('tags', []),
    }


def _build_record_queryset(filters):
    queryset = InformationRecord.objects.select_related('category', 'created_by').prefetch_related('tags')
    search_query = (filters.get('q') or '').strip()
    if search_query:
        queryset = queryset.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    status = filters.get('status') or ''
    if status:
        queryset = queryset.filter(status=status)

    category_id = filters.get('category') or ''
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    tag_ids = filters.get('tags') or []
    if isinstance(tag_ids, str):
        tag_ids = [tag_ids]
    if tag_ids:
        queryset = queryset.filter(tags__id__in=tag_ids).distinct()

    return queryset.order_by('-updated_at')


@login_required
def record_list(request):
    filters = _get_filter_dict(request)
    queryset = _build_record_queryset(filters)
    form = RecordFilterForm(
        {
            'q': filters.get('q', ''),
            'status': filters.get('status', ''),
            'category': filters.get('category', ''),
            'tags': filters.get('tags', []),
        }
    )
    context = {
        'records': queryset,
        'categories': Category.objects.order_by('name'),
        'tags': Tag.objects.order_by('name'),
        'filter_form': form,
        'filters': filters,
    }
    return render(request, 'records/record_list.html', context)


@login_required
def record_create(request):
    if request.method == 'POST':
        form = InformationRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            form.save_m2m()
            messages.success(request, 'Record created successfully.')
            return redirect('record_detail', pk=record.pk)
    else:
        form = InformationRecordForm()
    return render(
        request,
        'records/record_form.html',
        {
            'form': form,
            'title': 'Create Record',
            'has_categories': Category.objects.exists(),
            'has_tags': Tag.objects.exists(),
        },
    )


@login_required
def record_detail(request, pk):
    record = get_object_or_404(
        InformationRecord.objects.select_related('category', 'created_by').prefetch_related(
            'tags',
            'documents__uploaded_by',
        ),
        pk=pk,
    )
    upload_form = DocumentUploadForm()
    return render(request, 'records/record_detail.html', {'record': record, 'upload_form': upload_form})


@login_required
def record_edit(request, pk):
    record = get_object_or_404(InformationRecord, pk=pk)
    if request.method == 'POST':
        form = InformationRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated successfully.')
            return redirect('record_detail', pk=record.pk)
    else:
        form = InformationRecordForm(instance=record)
    return render(
        request,
        'records/record_form.html',
        {
            'form': form,
            'title': 'Edit Record',
            'record': record,
            'has_categories': Category.objects.exists(),
            'has_tags': Tag.objects.exists(),
        },
    )


@login_required
def record_delete(request, pk):
    record = get_object_or_404(InformationRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Record deleted successfully.')
        return redirect('record_list')
    return redirect('record_detail', pk=record.pk)


@login_required
def category_list(request):
    categories = Category.objects.order_by('name')
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    return render(request, 'records/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_create(request):
    return category_list(request)


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'records/category_form.html', {'form': form, 'category': category})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category_list')
    return redirect('category_list')


@login_required
def tag_list(request):
    tags = Tag.objects.order_by('name')
    form = TagForm()
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag created successfully.')
            return redirect('tag_list')
    return render(request, 'records/tag_list.html', {'tags': tags, 'form': form})


@login_required
def tag_create(request):
    return tag_list(request)


@login_required
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag updated successfully.')
            return redirect('tag_list')
    else:
        form = TagForm(instance=tag)
    return render(request, 'records/tag_form.html', {'form': form, 'tag': tag})


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag deleted successfully.')
        return redirect('tag_list')
    return redirect('tag_list')


def _serialize_record_for_export(record):
    return [
        record.title,
        record.status,
        record.category.name if record.category else '',
        ', '.join(tag.name for tag in record.tags.all()),
        record.created_by.get_full_name() or record.created_by.username,
        record.created_at.strftime('%Y-%m-%d %H:%M'),
        record.updated_at.strftime('%Y-%m-%d %H:%M'),
    ]


def _create_pdf_response(records):
    lines = ['Information Management System - Records Export', 'Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M')]
    for record in records:
        lines.append(f"- {record.title} | {record.status} | {record.category.name if record.category else 'Uncategorized'}")

    text = '\n'.join(lines)
    pdf_lines = []
    y = 760
    for line in text.splitlines():
        pdf_lines.append(f"BT /F1 12 Tf 50 {y} Td ({line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')}) Tj ET")
        y -= 18

    content = '\n'.join(pdf_lines)
    objects = [
        '<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        f'<< /Length {len(content.encode("latin-1"))} >>\nstream\n{content}\nendstream',
    ]

    pdf = b'%PDF-1.4\n'
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f'{idx} 0 obj\n{obj}\nendobj\n'.encode('latin-1')

    xref_start = len(pdf)
    pdf += f'xref\n0 {len(objects) + 1}\n'.encode('latin-1')
    pdf += b'0000000000 65535 f \n'
    for offset in offsets[1:]:
        pdf += f'{offset:010d} 00000 n \n'.encode('latin-1')
    pdf += f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n'.encode('latin-1')

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="records_export.pdf"'
    return response


@login_required
def export_records_pdf(request):
    filters = _get_filter_dict(request)
    records = _build_record_queryset(filters)
    return _create_pdf_response(records)


@login_required
def export_records_excel(request):
    filters = _get_filter_dict(request)
    records = _build_record_queryset(filters)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Status', 'Category', 'Tags', 'Created By', 'Created At', 'Updated At'])
    for record in records:
        writer.writerow(_serialize_record_for_export(record))

    response = HttpResponse(output.getvalue().encode('utf-8-sig'), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="records_export.xls"'
    return response
