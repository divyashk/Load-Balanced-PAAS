#%%
from time import sleep
import psutil
import os

#%%
def get_memory_details():
    mem = psutil.virtual_memory()
    mem_details = {
        "total": mem.total,
        "available": mem.available,
        "percent": mem.percent
    }

    return mem_details

def get_cpu_details():
    cpu_details = {
        "percent": psutil.cpu_percent(2) # CPU usage in last 2 seconds
    }
    return cpu_details

if __name__ == "__main__":
    print(get_memory_details())
    print(get_cpu_details())

    for i in range(10):
        sleep(1)
        load1, load5, load15 = psutil.getloadavg()
        cpu_usage = (load5/os.cpu_count()) * 100
        
        print("The CPU usage is : ", cpu_usage)

