import os
import time
from datetime import datetime
from datetime import timezone as tz

import psutil

from process_monitor_app.models import Process


class ProcessReader:
    """
    Handles reading and tracking system processes.

    This class is responsible for:
    - Parsing process timestamps.
    - Storing and updating processes in the database.
    - Deleting terminated processes from the database.
    - Classifying processes to determine which should be added or removed.

    Attributes:
        cache (dict): A dictionary storing active processes to track changes efficiently.
    """

    def __init__(self):
        self.cache = {}

    def timestamp_parser(self, timestamp: float) -> datetime:
        """
        Converts a UNIX timestamp into a timezone-aware datetime object.

        Args:
            timestamp (float): The UNIX timestamp of the process creation time.

        Returns:
            datetime: The UTC timezone-aware datetime object.
        """

        naive_dt = datetime.fromtimestamp(timestamp)
        aware_timestamp = naive_dt.replace(tzinfo=tz.utc)
        return aware_timestamp

    def send_process_to_db(self, p: psutil.Process) -> None:
        """
        Stores or updates a process in the database.

        If the process is new, it is saved to the database.
        If the process already exists, its data is updated.

        Args:
            p (psutil.Process): The process object retrieved from `psutil`.
        """
        if p.pid == 0:
            return  # Ignore system process with PID 0
        process_item = Process(
            PID=p.pid,
            name=p.name(),
            status=p.status(),
            start_time=self.timestamp_parser(p._create_time),
            duration=round(time.time() - p.create_time(), 2),
            memory_usage_MB=round(p.memory_info().rss / (1024**2), 2),
            CPU_Usage_Percent=p.cpu_percent(interval=1.0),
        )
        if p.cpu_percent(interval=0.0) > 0:
            print(f"ADDED {p.pid}")
        self.cache[p] = process_item

        if not Process.objects.filter(PID=process_item.PID).exists():
            process_item.save()
        else:
            Process.objects.filter(PID=process_item.PID).update(
                name=process_item.name,
                status=process_item.status,
                start_time=process_item.start_time,
                duration=process_item.duration,
                memory_usage_MB=process_item.memory_usage_MB,
                CPU_Usage_Percent=process_item.CPU_Usage_Percent,
            )

    def delete_process_from_db(self, p: psutil.Process):
        """
        Removes a process from the database.

        Args:
            p (psutil.Process): The process object retrieved from `psutil`.
        """

        process = Process.objects.filter(PID=p.pid)
        process.delete()
        print(f"REMOVED {p.pid}")

    def process_classification(self, processes: psutil.process_iter):
        """
        Classifies processes into those that should be added and those that should be removed.

        Args:
            processes (psutil.process_iter): An iterable of active processes.

        Returns:
            dict: A dictionary containing sets of processes to add and delete.
        """

        cached_processes = self.cache

        # Clear old processes after application start
        if len(cached_processes) == 0:
            Process.objects.all().delete()
        processes = set(processes)
        to_delete = cached_processes.keys() - processes
        to_add = processes - cached_processes.keys()
        return {"to_add": to_add, "to_delete": to_delete}


def run(self):
    """
    Continuously monitors and updates process information in the database.

    This function repeatedly:
    - Checks for new processes to add.
    - Removes terminated processes.
    - Updates process data every few seconds (based on `FREQUENCY`).

    The function runs indefinitely in a loop.
    """

    pr = ProcessReader()
    while True:
        print("Checking processes...")
        processes = pr.process_classification(psutil.process_iter())

        for process in processes["to_add"]:
            try:
                pr.send_process_to_db(process)
            except Exception as e:
                if "process no longer exists" in str(e):
                    pr.delete_process_from_db(process)
        for process in processes["to_delete"]:
            pr.delete_process_from_db(process)
            del pr.cache[process]

        # self.stdout.write('Sleeping for 15 seconds...')
        frequency = os.getenv("FREQUENCY", 15)
        time.sleep(frequency)
