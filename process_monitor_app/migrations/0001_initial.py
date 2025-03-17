# Generated by Django 5.1.7 on 2025-03-17 21:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PID', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('start_Time', models.DateTimeField()),
                ('duration', models.FloatField()),
                ('memory_usage_MB', models.FloatField()),
                ('CPU_Usage_Percent', models.FloatField()),
                ('SnapShot', models.BooleanField(default=False)),
                ('killed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='KilledProcess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('author', models.CharField(max_length=200)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='process_monitor_app.process')),
            ],
        ),
        migrations.CreateModel(
            name='SnapShot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('author', models.CharField(max_length=200)),
                ('processes', models.ManyToManyField(to='process_monitor_app.process')),
            ],
        ),
    ]
