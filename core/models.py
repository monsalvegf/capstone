from django.db import models

class Area(models.Model):
    description = models.CharField(max_length=50)
    codification = models.CharField(max_length=10)

    def __str__(self):
        return self.description

class Severity(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
