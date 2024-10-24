from django.contrib import admin

# Register your models here.

from .models import Incidencia_Cabecera, Incidencia_Linea, Estado, Area

admin.site.register(Estado)
admin.site.register(Area)

class Incidencia_LineaInline(admin.TabularInline):
    model = Incidencia_Linea
    extra = 1

class Incidencia_CabeceraAdmin(admin.ModelAdmin):
    list_display = ('In_Codificacion', 'In_Descripcion', 'In_Fecha', 'In_Estado', 'In_Area')
    search_fields = ('In_Codificacion', 'In_Descripcion')
    list_filter = ('In_Estado', 'In_Area')
    inlines = [Incidencia_LineaInline]

admin.site.register(Incidencia_Cabecera, Incidencia_CabeceraAdmin)

