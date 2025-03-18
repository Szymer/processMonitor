from django.db import models
import uuid

class Process(models.Model):
    PID = models.IntegerField(db_index=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.FloatField()
    memory_usage_MB = models.FloatField()
    CPU_Usage_Percent = models.FloatField()
    
    def __str__(self):
        return f"{self.name} (PID: {self.PID})"

class StoredProcess(models.Model):
    iid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    PID = models.IntegerField(db_index=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.FloatField()
    memory_usage_MB = models.FloatField()
    CPU_Usage_Percent = models.FloatField()
    
    def __str__(self):
        return f"[Stored] {self.name} (PID: {self.PID})"

class Snapshot(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)
    processes = models.ManyToManyField(StoredProcess, related_name="snapshots")

    def __str__(self):
        return f"Snapshot {self.timestamp} by {self.author}"

class StoppedProcess(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)
    process = models.ForeignKey(StoredProcess, on_delete=models.CASCADE, related_name="stopped_processes")


    
    
