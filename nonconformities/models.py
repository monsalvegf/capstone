from django.db import models
from django.contrib.auth.models import User

class Nonconformity(models.Model):
    # La clave primaria 'id' es automática
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    closure_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='nonconformities')
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=50)
    severity = models.ForeignKey('Severity', on_delete=models.SET_NULL, null=True)  # Nuevo campo
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)  # Nuevo campo

    def __str__(self):
        return f"{self.code} - {self.description[:50]}"

class NonconformityLine(models.Model):
    # La clave primaria 'id' es automática
    nonconformity = models.ForeignKey(Nonconformity, related_name='lines', on_delete=models.CASCADE)
    action_description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Action {self.id} of Nonconformity {self.nonconformity.code}"

class Status(models.Model):
    id = models.AutoField(primary_key=True, db_column='Es_Id')
    description = models.CharField(max_length=50, db_column='Es_Descripcion')

    def __str__(self):
        return self.description

class Area(models.Model):
    id = models.AutoField(primary_key=True, db_column='Area_Id')
    description = models.CharField(max_length=50, db_column='Area_Descripcion')
    codification = models.CharField(max_length=10, db_column='Area_Codificacion')

    def __str__(self):
        return self.description

class Severity(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.description

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.description
