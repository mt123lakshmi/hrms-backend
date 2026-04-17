from datetime import datetime

def calculate_duration(check_in, check_out):
    if not check_in or not check_out:
        return None

    fmt = "%H:%M:%S"

    in_time = datetime.strptime(str(check_in), fmt)
    out_time = datetime.strptime(str(check_out), fmt)

    duration = out_time - in_time

    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60

    return f"{hours}h {minutes}m"