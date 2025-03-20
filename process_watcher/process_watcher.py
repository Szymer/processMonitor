import os
import psutil
from   datetime import datetime, timezone as tz
import time
from process_monitor_app.models import Process, Snapshot



class ProcessReader():
    
    def __init__(self):
        self.cache = {}

    def timestamp_parser(self, timestamp: float) -> datetime:
        naiv_dt = datetime.fromtimestamp(timestamp)
        aware_timestamp = naiv_dt.replace(tzinfo=tz.utc)
        return aware_timestamp
    
    def send_process_to_db(self, p: psutil.Process) -> None:    
        if p.pid == 0:
            return 
        process_item = Process(
            PID =  p.pid,
            name = p.name(),
            status =  p.status(),
            start_time = self.timestamp_parser(p._create_time),
            duration = round(time.time() - p.create_time(), 2),
            memory_usage_MB =   round(p.memory_info().rss / (1024 ** 2), 2),
            CPU_Usage_Percent = p.cpu_percent(interval=1.0)
            )
        if p.cpu_percent(interval=0.0) > 0:
            print(f"ADDED {p.pid}")
        self.cache[p] = process_item
      
        if not Process.objects.filter(PID = process_item.PID).exists():
                process_item.save()
        else:
            Process.objects.filter(PID=process_item.PID).update(
                name=process_item.name,
                status=process_item.status,
                start_time=process_item.start_time,
                duration=process_item.duration,
                memory_usage_MB=process_item.memory_usage_MB,
                CPU_Usage_Percent=process_item.CPU_Usage_Percent
            )
  
    
    def delete_process_from_db(self, p: psutil.Process):
        process = Process.objects.filter(PID = p.pid)
        process.delete()
        print(f"REMOVED {p.pid}")
            

    def process_classification(self, processes: psutil.process_iter):
        cached_processes  = self.cache
        
        if len(cached_processes)==0:
            db_processes = Process.objects.all().delete()
            db_processes2 = Snapshot.objects.all().delete()
        
        processes = set(processes)
        to_delete = cached_processes.keys() - processes
        to_add = processes - cached_processes.keys()
        return {'to_add' : to_add,  'to_delete' : to_delete}




def run(self):        
        pr = ProcessReader()
        while True:
            print("Checking processes...")
            processes = pr.process_classification(psutil.process_iter())

            for process in processes['to_add']:
                try:
                    pr.send_process_to_db(process)
                except Exception as e:
                    if "process no longer exists" in str(e):
                        pr.delete_process_from_db(process)
            for process in processes['to_delete']:
                    pr.delete_process_from_db(process)
                    del pr.cache[process]

            # self.stdout.write('Sleeping for 15 seconds...')
            frequency = os.getenv('FREQUENCY', 15)
            time.sleep(frequency)

