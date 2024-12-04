from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Nonconformity, NonconformityLine, Severity, Category, Status
from django.http import HttpResponse
import csv

def get_filtered_nonconformities(request):
    code = request.GET.get('code', '').strip()
    creation_date = request.GET.get('creation_date', '').strip()
    description = request.GET.get('description', '').strip()
    severity_id = request.GET.get('severity', '').strip()
    category_id = request.GET.get('category', '').strip()
    status_id = request.GET.get('status', '').strip()

    filters = {}

    if code:
        filters['code__icontains'] = code
    if creation_date:
        filters['creation_date__date'] = creation_date
    if description:
        filters['description__icontains'] = description
    if severity_id.isdigit():
        filters['severity_id'] = int(severity_id)
    if category_id.isdigit():
        filters['category_id'] = int(category_id)
    if status_id.isdigit():
        filters['status_id'] = int(status_id)

    nonconformities = Nonconformity.objects.filter(**filters)
    nonconformities = nonconformities.order_by('status__description', 'creation_date')

    return nonconformities

@login_required
def nonconformity_list(request):
    severities = Severity.objects.all()
    categories = Category.objects.all()
    statuses = Status.objects.all()

    nonconformities = get_filtered_nonconformities(request)

    context = {
        'nonconformities': nonconformities,
        'severities': severities,
        'categories': categories,
        'statuses': statuses,
    }
    return render(request, 'nonconformities/nonconformity_list.html', context)

@login_required
def export_nonconformities(request):
    nonconformities = get_filtered_nonconformities(request)

    # Crear la respuesta HTTP con el contenido CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nonconformities.csv"'

    writer = csv.writer(response)
    writer.writerow(['Código', 'Fecha Apertura', 'Descripción', 'Severidad', 'Clasificación', 'Estado'])

    for nc in nonconformities:
        writer.writerow([
            nc.code,
            nc.creation_date.strftime('%d/%m/%Y'),
            nc.description,
            nc.severity.name if nc.severity else '',
            nc.category.description if nc.category else '',
            nc.status.description if nc.status else '',
        ])

    return response

@login_required
def nonconformity_detail_partial(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    return render(request, 'nonconformities/nonconformity_detail_partial.html', {'nonconformity': nonconformity})

@login_required
def nonconformity_detail(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    return render(request, 'nonconformities/nonconformity_detail.html', {'nonconformity': nonconformity})

@login_required
def nonconformity_detail_partial(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    # Obtener las líneas de acción relacionadas, ordenadas por fecha de registro
    action_lines = NonconformityLine.objects.filter(nonconformity=nonconformity).order_by('date')
    context = {
        'nonconformity': nonconformity,
        'action_lines': action_lines,
    }
    return render(request, 'nonconformities/nonconformity_detail_partial.html', context)
