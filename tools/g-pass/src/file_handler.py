# src/file_handler.py
import sys
import os
import argparse
import json
import csv
from datetime import datetime

class FileSaver:
    def __init__(self, output_file, format_type, split_size=0):
        self.base_filename, self.extension = os.path.splitext(output_file)
        if not self.extension: # if no extension, assume .txt
            self.extension = ".txt"
            self.base_filename = output_file

        self.format_type = format_type
        self.split_size = split_size
        self.part_num = 1
        self.current_size = 0
        self.file_handle = None
        self.writer = None
        self.is_json_list = (format_type == 'json' and split_size == 0)
        self.json_buffer = []
        self._open_file()

    def _get_current_filename(self):
        if self.part_num == 1:
            return f"{self.base_filename}{self.extension}"
        else:
            return f"{self.base_filename}_part{self.part_num}{self.extension}"

    def _open_file(self):
        filename = self._get_current_filename()
        print(f"[HANDLER] Opening file: {filename}", file=sys.stderr)
        self.file_handle = open(filename, 'w', encoding='utf-8', newline='')
        self.current_size = 0

        if self.format_type == 'csv':
            self.writer = csv.writer(self.file_handle)
            self.writer.writerow(['password', 'timestamp'])
        
    def _cycle_file(self):
        self.close()
        self.part_num += 1
        self._open_file()

    def write(self, password):
        line = ""
        timestamp = datetime.now().isoformat()

        if self.format_type == 'txt':
            line = f"{password}\n"
            self.file_handle.write(line)

        elif self.format_type == 'csv':
            self.writer.writerow([password, timestamp])
            line = f'"{password}","{timestamp}"\n' # Approximate size

        elif self.format_type == 'json':
            if self.is_json_list:
                self.json_buffer.append({"password": password, "timestamp": timestamp})
                return # Don't write immediately
            else: # JSON Lines for splitting
                record = {"password": password, "timestamp": timestamp}
                line = f"{json.dumps(record)}\n"
                self.file_handle.write(line)
        
        self.current_size += len(line.encode('utf-8'))
        if self.split_size > 0 and self.current_size >= self.split_size:
            self._cycle_file()

    def close(self):
        if self.file_handle:
            if self.is_json_list and self.json_buffer:
                json.dump(self.json_buffer, self.file_handle, indent=2)
            self.file_handle.close()

def main():
    parser = argparse.ArgumentParser(description="g-pass file handler.")
    parser.add_argument('--output', required=True, help="Output file path.")
    parser.add_argument('--format', choices=['txt', 'json', 'csv'], default='txt', help="Output file format.")
    parser.add_argument('--split-size', type=int, default=0, help="Split file size in bytes.")
    
    args = parser.parse_args()
    
    saver = FileSaver(args.output, args.format, args.split_size)
    
    try:
        for line in sys.stdin:
            password = line.strip()
            if password:
                saver.write(password)
    except KeyboardInterrupt:
        print("\n[HANDLER] Interrupted by user.", file=sys.stderr)
    finally:
        saver.close()

if __name__ == "__main__":
    main()