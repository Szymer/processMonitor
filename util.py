import psutil
import time
from pprint import pprint as pp

def get_process_list():
    

    p = psutil.Process()
    with p.oneshot():
        p.name()  # execute internal routine once collecting multiple info
        p.cpu_times()  # return cached value
        p.cpu_percent()  # return cached value
        p.create_time()  # return cached value
        p.ppid()  # return cached value
        p.status()  # return cached value
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    process_list = []
    for p in psutil.process_iter(['pid', 'name', 'status', 'memory_info', 'cpu_percent', 'create_time']):
        try:
            
            process_list.append({
                "PID": p.info["pid"],
                "Name": p.info["name"],
                "Status": p.info["status"],
                "Start Time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.info["create_time"])),
                "Duration": time.time() - p.info["create_time"],
                "Memory Usage (MB)": round(p.info["memory_info"].rss / (1024 ** 2), 2),
                "CPU Usage (%)": p.cpu_percent(interval=0.1),
            })
            x =1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return process_list



x = get_process_list()

pp(x)

