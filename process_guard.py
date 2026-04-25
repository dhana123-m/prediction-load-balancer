import psutil
import time

SAFE_SYSTEM = [
    "System",
    "System Idle Process",
    "svchost.exe",
    "explorer.exe",
    "Registry",
    "Memory Compression"
]


def top_process():

    # Warm up CPU counters
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except:
            pass

    time.sleep(1)

    heavy_name = "None"
    heavy_cpu = 0
    heavy_pid = 0

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):

        try:
            name = proc.info['name']
            cpu = proc.info['cpu_percent']
            pid = proc.info['pid']

            if not name:
                continue

            if name in SAFE_SYSTEM:
                continue

            if cpu > heavy_cpu:
                heavy_cpu = cpu
                heavy_name = name
                heavy_pid = pid

        except:
            pass

    return heavy_name, heavy_cpu, heavy_pid


def detect_heavy_user_app():

    heavy_name, heavy_cpu, heavy_pid = top_process()

    if heavy_cpu >= 90:
        return heavy_name, heavy_pid, heavy_cpu

    return None, None, 0


def kill_process(pid):

    try:
        psutil.Process(pid).terminate()
        return True
    except:
        return False