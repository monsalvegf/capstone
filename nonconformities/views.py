from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import Nonconformity, NonconformityLine, Severity, Category, Status
from .forms import NonconformityStatusForm, NonconformityCloseForm, NonconformityLineForm, NonconformityForm
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
def nonconformity_detail(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    return render(request, 'nonconformities/nonconformity_detail.html', {'nonconformity': nonconformity})

@login_required
def nonconformity_detail_partial(request, pk):
    nonconformity = get_object_or_404(Nonconformity, pk=pk)
    # Obtener las líneas de acción relacionadas, ordenadas por fecha de registro
    action_lines = NonconformityLine.objects.filter(nonconformity=nonconformity).order_by('date')

    # Obtener todos los estados para el dropdown
    statuses = Status.objects.all()

    context = {
        'nonconformity': nonconformity,
        'action_lines': action_lines,
        'statuses': statuses,
    }
    return render(request, 'nonconformities/nonconformity_detail_partial.html', context)


@login_required
def change_status(request, pk):
    """
    Cambia el estado de una NC.

    Soporta AJAX y redirección tradicional.
    """
    nonconformity = get_object_or_404(Nonconformity, pk=pk)

    if request.method == 'POST':
        new_status_id = request.POST.get('status')

        if new_status_id:
            try:
                new_status = Status.objects.get(id=new_status_id)
                old_status = nonconformity.status

                nonconformity.status = new_status

                # Si el nuevo estado es "Cerrada" y no tiene closure_date, establecerla
                if new_status.description.lower() in ['cerrada', 'cerrado', 'closed']:
                    if not nonconformity.closure_date:
                        nonconformity.closure_date = timezone.now()

                # Si el estado deja de ser "Cerrada", limpiar closure_date
                elif old_status and old_status.description.lower() in ['cerrada', 'cerrado', 'closed']:
                    nonconformity.closure_date = None

                nonconformity.save()

                # Crear una línea de acción automática registrando el cambio
                NonconformityLine.objects.create(
                    nonconformity=nonconformity,
                    action_description=f"Estado cambiado de '{old_status}' a '{new_status}'",
                    user=request.user
                )

                messages.success(request, f'Estado actualizado a "{new_status}"')

                # Si es AJAX, devolver JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Estado actualizado a "{new_status}"',
                        'new_status': new_status.description,
                        'closure_date': nonconformity.closure_date.strftime('%d/%m/%Y') if nonconformity.closure_date else None
                    })

            except Status.DoesNotExist:
                messages.error(request, 'Estado no válido')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Estado no válido'}, status=400)
        else:
            messages.error(request, 'Debe seleccionar un estado')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Debe seleccionar un estado'}, status=400)

    # Redirección tradicional
    return redirect('nonconformities:nonconformity_detail', pk=pk)


@login_required
def close_nonconformity(request, pk):
    """
    Cierra una NC estableciendo closure_date y cambiando estado a "Cerrada".
    """
    nonconformity = get_object_or_404(Nonconformity, pk=pk)

    # Verificar que no esté ya cerrada
    if nonconformity.closure_date:
        messages.warning(request, 'Esta no conformidad ya está cerrada.')
        return redirect('nonconformities:nonconformity_detail', pk=pk)

    if request.method == 'POST':
        form = NonconformityCloseForm(request.POST)

        if form.is_valid():
            # Establecer fecha de cierre
            nonconformity.closure_date = timezone.now()

            # Buscar estado "Cerrada" y asignarlo
            try:
                closed_status = Status.objects.filter(
                    description__icontains='cerrad'
                ).first()

                if closed_status:
                    nonconformity.status = closed_status
                else:
                    messages.warning(request, 'No se encontró el estado "Cerrada". Actualice manualmente.')
            except:
                pass

            nonconformity.save()

            # Registrar acción de cierre
            closing_comment = form.cleaned_data.get('closing_comment', '')
            action_text = 'No conformidad cerrada.'
            if closing_comment:
                action_text += f' Comentario: {closing_comment}'

            NonconformityLine.objects.create(
                nonconformity=nonconformity,
                action_description=action_text,
                user=request.user
            )

            messages.success(request, f'No conformidad {nonconformity.code} cerrada exitosamente.')
            return redirect('nonconformities:nonconformity_detail', pk=pk)
    else:
        form = NonconformityCloseForm()

    context = {
        'nonconformity': nonconformity,
        'form': form,
    }
    return render(request, 'nonconformities/close_nonconformity.html', context)


@login_required
def reopen_nonconformity(request, pk):
    """
    Reabre una NC cerrada, limpiando closure_date y cambiando estado.
    """
    nonconformity = get_object_or_404(Nonconformity, pk=pk)

    if request.method == 'POST':
        if not nonconformity.closure_date:
            messages.warning(request, 'Esta no conformidad no está cerrada.')
        else:
            # Limpiar fecha de cierre
            nonconformity.closure_date = None

            # Cambiar a estado "Abierta"
            try:
                open_status = Status.objects.filter(
                    description__icontains='abierta'
                ).first()

                if open_status:
                    nonconformity.status = open_status
            except:
                pass

            nonconformity.save()

            # Registrar acción
            NonconformityLine.objects.create(
                nonconformity=nonconformity,
                action_description='No conformidad reabierta.',
                user=request.user
            )

            messages.success(request, f'No conformidad {nonconformity.code} reabierta.')

    return redirect('nonconformities:nonconformity_detail', pk=pk)


@login_required
def add_action(request, pk):
    """
    Añade una línea de acción/seguimiento a una NC.

    Soporta AJAX para actualización sin recargar página.
    """
    nonconformity = get_object_or_404(Nonconformity, pk=pk)

    if request.method == 'POST':
        form = NonconformityLineForm(request.POST)

        if form.is_valid():
            # Crear la línea de acción
            action_line = form.save(commit=False)
            action_line.nonconformity = nonconformity
            action_line.user = request.user
            action_line.save()

            messages.success(request, 'Acción agregada exitosamente.')

            # Si es AJAX, devolver JSON con la nueva acción
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Acción agregada exitosamente.',
                    'action': {
                        'id': action_line.id,
                        'description': action_line.action_description,
                        'date': action_line.date.strftime('%d/%m/%Y %H:%M'),
                        'user': action_line.user.username if action_line.user else 'Sin usuario'
                    }
                })

            # Redirección tradicional
            return redirect('nonconformities:nonconformity_detail', pk=pk)
        else:
            # Si hay errores de validación
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario.',
                    'errors': form.errors
                }, status=400)

            messages.error(request, 'Error al agregar la acción. Verifique los datos.')

    # Si no es POST o hay errores, redirigir
    return redirect('nonconformities:nonconformity_detail', pk=pk)


@login_required
def create_nonconformity(request):
    """
    Crea una nueva No Conformidad desde el frontend.

    Formulario completo con validaciones:
    - Código único
    - Campos requeridos
    - Usuario creador automático
    """
    if request.method == 'POST':
        form = NonconformityForm(request.POST)

        if form.is_valid():
            # Crear la NC sin guardar aún
            nonconformity = form.save(commit=False)

            # Asignar el usuario creador
            nonconformity.user = request.user

            # Si no tiene estado, asignar "Abierta" por defecto
            if not nonconformity.status:
                try:
                    default_status = Status.objects.filter(
                        description__icontains='abierta'
                    ).first()
                    if default_status:
                        nonconformity.status = default_status
                except:
                    pass

            # Guardar la NC
            nonconformity.save()

            # Crear línea de acción automática de creación
            NonconformityLine.objects.create(
                nonconformity=nonconformity,
                action_description=f'No conformidad creada por {request.user.username}',
                user=request.user
            )

            messages.success(
                request,
                f'No conformidad {nonconformity.code} creada exitosamente.'
            )

            # Redirigir al detalle de la NC recién creada
            return redirect('nonconformities:nonconformity_detail', pk=nonconformity.pk)
    else:
        form = NonconformityForm()

    context = {
        'form': form,
    }
    return render(request, 'nonconformities/create_nonconformity.html', context)


@login_required
def update_nonconformity(request, pk):
    """
    Edita una No Conformidad existente.

    Permite modificar todos los campos excepto:
    - Usuario creador
    - Fecha de creación
    - Closure_date (se gestiona con el botón "Cerrar")
    """
    nonconformity = get_object_or_404(Nonconformity, pk=pk)

    if request.method == 'POST':
        form = NonconformityForm(request.POST, instance=nonconformity)

        if form.is_valid():
            # Guardar los cambios
            updated_nc = form.save()

            # Registrar la edición en el historial
            NonconformityLine.objects.create(
                nonconformity=updated_nc,
                action_description=f'No conformidad editada por {request.user.username}',
                user=request.user
            )

            messages.success(
                request,
                f'No conformidad {updated_nc.code} actualizada exitosamente.'
            )

            return redirect('nonconformities:nonconformity_detail', pk=pk)
    else:
        form = NonconformityForm(instance=nonconformity)

    context = {
        'form': form,
        'nonconformity': nonconformity,
        'is_edit': True,
    }
    return render(request, 'nonconformities/create_nonconformity.html', context)
