# Generated by Django 5.1.7 on 2025-03-20 18:28

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Process",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("PID", models.IntegerField(db_index=True)),
                ("name", models.CharField(max_length=200)),
                ("status", models.CharField(max_length=200)),
                ("start_time", models.DateTimeField()),
                ("duration", models.FloatField()),
                ("memory_usage_MB", models.FloatField()),
                ("CPU_Usage_Percent", models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name="Snapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("author", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="StoppedProcess",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("author", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="StoredProcess",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "iid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("PID", models.IntegerField(db_index=True)),
                ("name", models.CharField(max_length=200)),
                ("status", models.CharField(max_length=200)),
                ("start_time", models.DateTimeField()),
                ("duration", models.FloatField()),
                ("memory_usage_MB", models.FloatField()),
                ("CPU_Usage_Percent", models.FloatField()),
                (
                    "StoppedProcess",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stored_processes",
                        to="process_monitor_app.stoppedprocess",
                    ),
                ),
                (
                    "snapshot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stored_processes",
                        to="process_monitor_app.snapshot",
                    ),
                ),
            ],
        ),
    ]
