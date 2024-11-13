from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Nonconformity, Severity, Category, Status
import csv
from django.http import HttpResponse

@login_required
def nonconformity_list(request):
    # Obtener todos los objetos necesarios para los filtros
    severities = Severity.objects.all()
    categories = Category.objects.all()
    statuses = Status.objects.all()

    # Obtener los parámetros de filtrado
    code = request.GET.get('code', '')
    creation_date = request.GET.get('creation_date', '')
    description = request.GET.get('description', '')
    severity_id = request.GET.get('severity', '')
    category_id = request.GET.get('category', '')
    status_id = request.GET.get('status', '')

    # Filtrar las no conformidades
    nonconformities = Nonconformity.objects.all()

    if code:
        nonconformities = nonconformities.filter(code__icontains=code)
    if creation_date:
        nonconformities = nonconformities.filter(creation_date__date=creation_date)
    if description:
        nonconformities = nonconformities.filter(description__icontains=description)
    if severity_id:
        nonconformities = nonconformities.filter(severity_id=severity_id)
    if category_id:
        nonconformities = nonconformities.filter(category_id=category_id)
    if status_id:
        nonconformities = nonconformities.filter(status_id=status_id)

    # Ordenar: primero abiertas, luego cerradas, ordenadas por fecha de apertura
    nonconformities = nonconformities.order_by('status__description', 'creation_date')

    context = {
        'nonconformities': nonconformities,
        'severities': severities,
        'categories': categories,
        'statuses': statuses,
    }
    return render(request, 'nonconformities/nonconformity_list.html', context)

# Vista para el detalle AJAX
@login_required
def nonconformity_detail_ajax(request):
    nonconformity_id = request.GET.get('id')
    nonconformity = get_object_or_404(Nonconformity, id=nonconformity_id)
    return render(request, 'nonconformities/nonconformity_detail_partial.html', {'nonconformity': nonconformity})

# Vista para el detalle en página completa
@login_required
def nonconformity_detail(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    return render(request, 'nonconformities/nonconformity_detail.html', {'nonconformity': nonconformity})


@login_required
def export_nonconformities(request):
    # Filtra las no conformidades según los mismos criterios que en la vista de lista
    # (puedes reutilizar el código o crear una función auxiliar)

    # Aquí, simplemente obtendremos todas
    nonconformities = Nonconformity.objects.all()

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
