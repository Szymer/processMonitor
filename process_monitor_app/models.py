from django.db import models

# Create your models here.

class Process(models.Model):
    PID = models.IntegerField()
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.FloatField()
    memory_usage_MB = models.FloatField()
    CPU_Usage_Percent = models.FloatField()
    SnapShot = models.BooleanField(default=False)
    killed = models.BooleanField(default=False) 


class SnapShot(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)
    processes = models.ManyToManyField(Process)


class KilledProcess(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)    
    
    