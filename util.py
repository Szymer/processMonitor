import psutil
import time
from cachetools import cached, Cache, cachedmethod
# from pprint import pprint as pp


cache= Cache(maxsize=2048)


class ProcessModel:
    def __init__(self):
        self.PID = ''
        self.Name = ''
        self.Status =  ''
        self.Start_Time = ''
        self.Duration =  ''
        self.Memory_Usage_MB = ''
        self.CPU_Usage_Percent = ''
 

class ProcessReader():
    
    def get_process_list(self):
        return psutil.pids()


    def get_process_detail(self, p: psutil.Process )-> ProcessModel :
        process_item = ProcessModel()
        process_item.PID =  p.pid
        process_item.Name = p.name()
        process_item.Status =  p.status()
        process_item.Start_Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.create_time()))
        process_item.Duration = round(time.time() - p.create_time(), 2)
        process_item.Memory_Usage_MB =   round(p.memory_info().rss / (1024 ** 2), 2)
        process_item.CPU_Usage_Percent = p.cpu_percent(interval=0.1)
        cache[p] = process_item
        return process_item
    

    def send_process_to_db(self, p: psutil.Process):    
        p_detail = self.get_process_detail(p)
        print(p_detail.__dict__)
    
    def delete_process_from_db(self, p: psutil.Process):
        
        print(f"REMOVED {p.pid}")
            

    def process_clasyfication(self, processes: psutil.process_iter):
        cached_processes  = cache
        processes = set(processes)
        to_delete = cached_processes.keys() - processes
        to_add = processes - cached_processes.keys()
        return {'to_add' : to_add,  'to_delete' : to_delete}






pr = ProcessReader()
while True:
        processes = pr.process_clasyfication(psutil.process_iter())
        
        for process in processes['to_add']:
            try:
                pr.send_process_to_db(process)
            except Exception as e:
                        print(e)
        for process in processes['to_delete']:
            try:
                pr.delete_process_from_db(process)
                del cache[process]
            except Exception as e:
                        print(e)
        
        print('sleeping 5 s')
        time.sleep(5)
        



