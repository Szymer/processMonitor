# Generated by Django 5.1.7 on 2025-03-20 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("process_monitor_app", "0002_stoppedprocess_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="storedprocess",
            name="StoppedProcess",
        ),
    ]
