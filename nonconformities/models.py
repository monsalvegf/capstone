from django.db import models
from django.contrib.auth.models import User

class Incidencia(models.Model):
    # Clave primaria 'id' es automática
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='incidencias')
    estado = models.ForeignKey('Estado', on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True)
    codigo = models.CharField(max_length=50)
    clasificacion = models.ForeignKey('Clasificacion', on_delete=models.SET_NULL, null=True)  # Nuevo campo

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}"

class LineaIncidencia(models.Model):
    # Clave primaria 'id' es automática
    incidencia = models.ForeignKey(Incidencia, related_name='lineas', on_delete=models.CASCADE)
    descripcion_accion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Acción {self.id} de Incidencia {self.incidencia.codigo}"

class Estado(models.Model):
    id = models.AutoField(primary_key=True, db_column='Es_Id')
    descripcion = models.CharField(max_length=50, db_column='Es_Descripcion')

    def __str__(self):
        return self.descripcion

class Area(models.Model):
    id = models.AutoField(primary_key=True, db_column='Area_Id')
    descripcion = models.CharField(max_length=50, db_column='Area_Descripcion')
    codificacion = models.CharField(max_length=10, db_column='Area_Codificacion')

    def __str__(self):
        return self.descripcion

class Clasificacion(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion
