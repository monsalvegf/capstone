# Generated by Django 5.1.2 on 2024-11-12 18:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(db_column='Es_Descripcion', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Nonconformity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('closure_date', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=50)),
                ('area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.area')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='nonconformities.category')),
                ('severity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.severity')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nonconformities', to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='nonconformities.status')),
            ],
        ),
        migrations.CreateModel(
            name='NonconformityLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_description', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('nonconformity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='nonconformities.nonconformity')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
