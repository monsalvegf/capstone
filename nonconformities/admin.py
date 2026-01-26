from django.contrib import admin

# Importa los modelos con los nuevos nombres en inglés
from .models import Severity, Status, Category, Nonconformity, NonconformityLine

# Registro de modelos específicos de 'nonconformities'

class NonconformityLineInline(admin.TabularInline):
    model = NonconformityLine
    extra = 1

class NonconformityAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'creation_date', 'status', 'area', 'category')
    list_filter = ('status', 'area', 'category')
    inlines = [NonconformityLineInline]


admin.site.register(Severity)
admin.site.register(Status)
admin.site.register(Nonconformity, NonconformityAdmin)
admin.site.register(Category)


