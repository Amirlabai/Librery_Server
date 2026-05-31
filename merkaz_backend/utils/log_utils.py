import csv
import threading

_log_lock = threading.Lock()

def log_event(filename, data):
    """Appends a new row to a specified CSV log file."""
    with _log_lock:
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
