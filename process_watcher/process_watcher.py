import psutil
import time
from process_monitor_app.models import Process





class ProcessReader():
    
    def __init__(self):
        self.cache = {}


    def send_process_to_db(self, p: psutil.Process) -> None:    
        process_item = Process(
            PID =  p.pid,
            name = p.name(),
            status =  p.status(),
            start_time = time.strftime("%Y-%m-%d %H:%M:%S"),
            duration = round(time.time() - p.create_time(), 2),
            memory_usage_MB =   round(p.memory_info().rss / (1024 ** 2), 2),
            CPU_Usage_Percent = p.cpu_percent(interval=0.0)
            )
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
        processes = set(processes)
        to_delete = cached_processes.keys() - processes
        to_add = processes - cached_processes.keys()
        return {'to_add' : to_add,  'to_delete' : to_delete}





