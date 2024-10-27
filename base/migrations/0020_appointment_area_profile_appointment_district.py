# Generated by Django 5.1.1 on 2024-10-26 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_timeslot_opd_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='area_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.areaprofile'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.district'),
        ),
    ]
