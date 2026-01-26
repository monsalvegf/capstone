from django import forms
from django.core.exceptions import ValidationError
from .models import Nonconformity, NonconformityLine, Status, Category, Severity
from core.models import Area


class NonconformityForm(forms.ModelForm):
    """
    Formulario para crear y editar No Conformidades.

    Incluye validaciones:
    - Código único (solo en creación)
    - Campos requeridos: code, description, severity, category
    - Closure_date solo si status es "Cerrada"
    """

    class Meta:
        model = Nonconformity
        fields = [
            'code',
            'description',
            'severity',
            'category',
            'area',
            'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe la no conformidad detectada...'
            }),
            'code': forms.TextInput(attrs={
                'placeholder': 'Ej: NC-2025-001'
            }),
        }
        labels = {
            'code': 'Código',
            'description': 'Descripción',
            'severity': 'Severidad',
            'category': 'Clasificación',
            'area': 'Área',
            'status': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos requeridos
        self.fields['code'].required = True
        self.fields['description'].required = True
        self.fields['severity'].required = True
        self.fields['category'].required = True

        # Mejorar apariencia de selects
        self.fields['severity'].empty_label = "Seleccione severidad"
        self.fields['category'].empty_label = "Seleccione clasificación"
        self.fields['area'].empty_label = "Seleccione área (opcional)"
        self.fields['status'].empty_label = "Seleccione estado"

    def clean_code(self):
        """Valida que el código sea único (solo en creación)."""
        code = self.cleaned_data.get('code')

        if not code:
            raise ValidationError('El código es requerido.')

        # Solo validar unicidad si es una nueva NC (no tiene pk)
        if not self.instance.pk:
            if Nonconformity.objects.filter(code=code).exists():
                raise ValidationError(
                    f'El código "{code}" ya existe. Por favor, use uno diferente.'
                )

        return code.upper()  # Convertir a mayúsculas

    def clean_description(self):
        """Valida que la descripción tenga contenido significativo."""
        description = self.cleaned_data.get('description', '').strip()

        if not description:
            raise ValidationError('La descripción es requerida.')

        if len(description) < 10:
            raise ValidationError('La descripción debe tener al menos 10 caracteres.')

        return description

    def clean(self):
        """Validaciones que involucran múltiples campos."""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')

        # Si el estado es "Cerrada", asegurar que se setee closure_date
        # (esto lo manejamos en la vista, pero podríamos validarlo aquí)

        return cleaned_data


class NonconformityLineForm(forms.ModelForm):
    """
    Formulario para agregar acciones/líneas de seguimiento a una NC.

    Solo requiere la descripción de la acción.
    El user, date y nonconformity se asignan automáticamente en la vista.
    """

    class Meta:
        model = NonconformityLine
        fields = ['action_description']
        widgets = {
            'action_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describa la acción realizada o planificada...',
                'class': 'form-control'
            }),
        }
        labels = {
            'action_description': 'Descripción de la Acción',
        }

    def clean_action_description(self):
        """Valida que la descripción de la acción no esté vacía."""
        action = self.cleaned_data.get('action_description', '').strip()

        if not action:
            raise ValidationError('La descripción de la acción es requerida.')

        if len(action) < 5:
            raise ValidationError('La descripción debe tener al menos 5 caracteres.')

        return action


class NonconformityStatusForm(forms.ModelForm):
    """
    Formulario simple para cambiar solo el estado de una NC.

    Útil para workflows rápidos (cambio de estado con un dropdown).
    """

    class Meta:
        model = Nonconformity
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control status-select'
            }),
        }
        labels = {
            'status': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = True
        self.fields['status'].empty_label = None  # No permitir vacío


class NonconformityCloseForm(forms.Form):
    """
    Formulario simple para cerrar una NC.

    Solo pide confirmación opcional con comentario.
    """

    closing_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Comentario de cierre (opcional)...',
            'class': 'form-control'
        }),
        label='Comentario de Cierre',
        help_text='Opcional: añade un comentario explicando el cierre.'
    )

    confirm = forms.BooleanField(
        required=True,
        label='Confirmo que esta NC está resuelta y debe cerrarse',
        error_messages={
            'required': 'Debe confirmar el cierre de la no conformidad.'
        }
    )


class NonconformityFilterForm(forms.Form):
    """
    Formulario para filtrar la lista de No Conformidades.

    Mejora el filtrado existente agregando validación y widgets mejorados.
    """

    code = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por código...'
        }),
        label='Código'
    )

    creation_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date'
        }),
        label='Fecha de Creación'
    )

    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar en descripción...'
        }),
        label='Descripción'
    )

    severity = forms.ModelChoiceField(
        required=False,
        queryset=Severity.objects.all(),
        empty_label='Todas',
        label='Severidad'
    )

    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        empty_label='Todas',
        label='Clasificación'
    )

    status = forms.ModelChoiceField(
        required=False,
        queryset=Status.objects.all(),
        empty_label='Todos',
        label='Estado'
    )

    area = forms.ModelChoiceField(
        required=False,
        queryset=Area.objects.all(),
        empty_label='Todas',
        label='Área'
    )
