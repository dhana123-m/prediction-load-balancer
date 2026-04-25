import psutil

def get_metrics():

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    network = round(
        psutil.net_io_counters().bytes_sent / (1024 * 1024), 2
    )

    # Battery
    battery = psutil.sensors_battery()

    if battery:
        battery_percent = battery.percent
    else:
        battery_percent = 100

    # Temperature
    cpu_temp = 0

    try:
        temps = psutil.sensors_temperatures()

        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    cpu_temp = entry.current
                    break
                break

    except:
        cpu_temp = 0

    return cpu, ram, disk, network, battery_percent, cpu_temp