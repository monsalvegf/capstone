from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Nonconformity, Severity, Category, Status
from django.http import HttpResponse
from django.views.generic import ListView
import csv

@login_required
def nonconformity_list(request):
    # Obtener todos los objetos necesarios para los filtros
    severities = Severity.objects.all()
    categories = Category.objects.all()
    statuses = Status.objects.all()

    # Obtener los parámetros de filtrado
    code = request.GET.get('code', '').strip()
    creation_date = request.GET.get('creation_date', '').strip()
    description = request.GET.get('description', '').strip()
    severity_id = request.GET.get('severity', '').strip()
    category_id = request.GET.get('category', '').strip()
    status_id = request.GET.get('status', '').strip()

    # Inicializar el diccionario de filtros
    filters = {}

    # Aplicar filtros solo si los valores son válidos
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

    # Aplicar los filtros al queryset
    nonconformities = Nonconformity.objects.filter(**filters)

    # Ordenar: primero abiertas, luego cerradas, ordenadas por fecha de apertura
    nonconformities = nonconformities.order_by('status__description', 'creation_date')

    context = {
        'nonconformities': nonconformities,
        'severities': severities,
        'categories': categories,
        'statuses': statuses,
    }
    return render(request, 'nonconformities/nonconformity_list.html', context)

@login_required
def nonconformity_detail_partial(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    return render(request, 'nonconformities/nonconformity_detail_partial.html', {'nonconformity': nonconformity})

@login_required
def nonconformity_detail(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    return render(request, 'nonconformities/nonconformity_detail.html', {'nonconformity': nonconformity})

@login_required
def export_nonconformities(request):
    # Filtrar las no conformidades según los mismos criterios que en la vista de lista
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

class NonConformityListView(ListView):
    model = Nonconformity
    template_name = 'nonconformity_list.html'
    context_object_name = 'nonconformities'

    def get_queryset(self):
        queryset = super().get_queryset()
        code = self.request.GET.get('code')
        creation_date = self.request.GET.get('creation_date')
        description = self.request.GET.get('description')
        severity = self.request.GET.get('severity')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')

        if code:
            queryset = queryset.filter(code__icontains=code)
        if creation_date:
            queryset = queryset.filter(creation_date=creation_date)
        if description:
            queryset = queryset.filter(description__icontains=description)
        if severity:
            queryset = queryset.filter(severity__id=severity)
        if category:
            queryset = queryset.filter(category__id=category)
        if status:
            queryset = queryset.filter(status__id=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar listas para los selectores de filtrado
        context['severities'] = Severity.objects.all()
        context['categories'] = Category.objects.all()
        context['statuses'] = Status.objects.all()
        return context
