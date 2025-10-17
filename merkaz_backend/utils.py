import os
import csv
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from openpyxl.workbook import Workbook
except ImportError:
    print("Warning: openpyxl not found. Excel export will not work. Run 'pip install openpyxl'.")
    class Workbook: pass

def log_event(filename, data):
    """Appends a new row to a specified CSV log file."""
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def csv_to_xlsx_in_memory(csv_filepath):
    """Converts a CSV file to an XLSX file in memory (BytesIO)."""
    if 'Workbook' not in globals():
        raise RuntimeError("openpyxl library is missing.")
    wb = Workbook()
    ws = wb.active
    ws.title = os.path.basename(csv_filepath).replace('.csv', '').title()
    try:
        with open(csv_filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                ws.append(row)
    except FileNotFoundError:
        ws.append(["Error", "File Not Found"])
    memory_file = BytesIO()
    wb.save(memory_file)
    memory_file.seek(0)
    return memory_file

def create_file_with_header(filename, header):
    """Creates a file with a header if it doesn't exist."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(header)
        print(f"Created file: {filename}")
