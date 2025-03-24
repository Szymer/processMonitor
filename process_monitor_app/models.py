import uuid

from django.db import models


class Process(models.Model):
    """
    Represents a running process.

    This model stores information about active system processes, including
    their resource usage and runtime details.

    Attributes:
        PID (int): The unique process ID.
        name (str): The name of the process.
        status (str): The current status of the process (e.g., running, stopped).
        start_time (datetime): The timestamp when the process started.
        duration (float): The total duration (in seconds) the process has been running.
        memory_usage_MB (float): The memory usage of the process in megabytes.
        CPU_Usage_Percent (float): The CPU usage percentage of the process.
    """

    PID = models.IntegerField(db_index=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.FloatField()
    memory_usage_MB = models.FloatField()
    CPU_Usage_Percent = models.FloatField()

    def __str__(self):
        return f"{self.name} (PID: {self.PID})"


class Snapshot(models.Model):
    """
    Represents a snapshot of all running processes at a specific point in time.

    This model stores metadata about the snapshot, such as the author and timestamp.

    Attributes:
        timestamp (datetime): The date and time when the snapshot was created.
        author (str): The username of the person who created the snapshot.
    """

    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)

    def __str__(self):
        return f"Snapshot {self.id} by {self.author} at {self.timestamp}"


class StoredProcess(models.Model):
    """
    Stores process data captured in a snapshot.

    This model represents a historical record of a process that was running
    at the time of a snapshot.

    Attributes:
        iid (UUID): A unique identifier for the stored process.
        PID (int): The process ID at the time of the snapshot.
        name (str): The name of the process.
        status (str): The process status at the time of the snapshot.
        start_time (datetime): The start time of the process.
        duration (float): The duration (in seconds) the process had been running.
        memory_usage_MB (float): The memory usage in megabytes.
        CPU_Usage_Percent (float): The CPU usage percentage.
        snapshot (ForeignKey): A reference to the associated `Snapshot` instance.
    """

    iid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    PID = models.IntegerField(db_index=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.FloatField()
    memory_usage_MB = models.FloatField()
    CPU_Usage_Percent = models.FloatField()
    snapshot = models.ForeignKey(
        Snapshot, on_delete=models.CASCADE, related_name="stored_processes"
    )

    def __str__(self):
        return f"[Stored] {self.name} (PID: {self.PID})"


class StoppedProcess(models.Model):
    """
    Represents a process that has been manually stopped.

    This model stores information about terminated processes, including
    who stopped them and when.

    Attributes:
        timestamp (datetime): The date and time when the process was stopped.
        author (str): The username of the person who stopped the process.
        name (str): The name of the stopped process.
    """

    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)
    name = models.CharField(max_length=200, db_default="Unknown")

    def __str__(self):
        return f"Process {self.name} stopped by {self.author} at {self.timestamp}"
