# Generated by Django 5.1.1 on 2024-10-20 06:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_delete_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorprofile',
            name='area_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.areaprofile'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='area_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.areaprofile'),
        ),
    ]