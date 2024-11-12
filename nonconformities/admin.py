from django.contrib import admin

# Importa los modelos con los nuevos nombres en inglés
from .models import Nonconformity, NonconformityLine, Status, Area, Severity, Category

# Registro de modelos en el admin
admin.site.register(Status)
admin.site.register(Severity)
admin.site.register(Category)

# Personalización de la vista de Area en el admin
class AreaAdmin(admin.ModelAdmin):
    list_display = ('description', 'codification')
    search_fields = ('description', 'codification')

admin.site.register(Area, AreaAdmin)

# Inline para NonconformityLine en Nonconformity
class NonconformityLineInline(admin.TabularInline):
    model = NonconformityLine
    extra = 1

# Personalización de la vista de Nonconformity en el admin
class NonconformityAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'creation_date', 'status', 'area', 'severity', 'category')
    list_filter = ('status', 'area', 'severity', 'category')
    inlines = [NonconformityLineInline]

admin.site.register(Nonconformity, NonconformityAdmin)
