# Generated by Django 5.1.1 on 2024-10-21 19:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_timeslot_remove_appointment_doctor_profile_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='session',
        ),
        migrations.AlterField(
            model_name='appointment',
            name='time_slot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.timeslot'),
        ),
    ]