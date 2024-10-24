from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Incidencia_Cabecera(models.Model):
    In_Id = models.AutoField(primary_key=True)
    In_Descripcion = models.TextField()
    In_Fecha = models.DateTimeField(auto_now_add=True)
    In_FechaCierre = models.DateTimeField(null=True, blank=True)
    In_Usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='incidencias')
    In_Estado = models.ForeignKey('Estado', on_delete=models.SET_NULL, null=True)
    In_Area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True)
    In_Codificacion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.In_Codificacion} - {self.In_Descripcion[:50]}"

class Incidencia_Linea(models.Model):
    Il_Id = models.AutoField(primary_key=True)
    In_Cab = models.ForeignKey(Incidencia_Cabecera, related_name='lineas', on_delete=models.CASCADE)
    Il_DesAccion = models.TextField()
    Il_Fecha = models.DateTimeField(auto_now_add=True)
    Id_Usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Acción {self.Il_Id} de Incidencia {self.In_Cab.In_Codificacion}"

class Estado(models.Model):
    Es_Id = models.AutoField(primary_key=True)
    Es_Descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.Es_Descripcion

class Area(models.Model):
    Area_Id = models.AutoField(primary_key=True)
    Area_Descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.Area_Descripcion

