def detect_risk(cpu, ram, disk):

    avg = (cpu + ram + disk) / 3

    if avg >= 90:
        return "Critical"

    elif avg >= 75:
        return "Warning"

    return "Safe"

def protect_system(risk):

    if risk == "Critical":
        return "Power Saver Activated / Heavy Tasks Reduced"

    elif risk == "Warning":
        return "Monitoring Increased"

    return "Normal Operation"