from django.contrib import admin

# Register your models here.

from .models import Incidencia, LineaIncidencia, Estado, Area, Clasificacion

# Resto del código...

admin.site.register(Estado)
admin.site.register(Area)
admin.site.register(Clasificacion) 

class AreaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'codificacion')
    search_fields = ('descripcion', 'codificacion')

class LineaIncidenciaInline(admin.TabularInline):
    model = LineaIncidencia
    extra = 1

class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'fecha_creacion', 'estado', 'area', 'clasificacion') 
    list_filter = ('estado', 'area', 'clasificacion')  
    inlines = [LineaIncidenciaInline]

admin.site.register(Incidencia, IncidenciaAdmin)

