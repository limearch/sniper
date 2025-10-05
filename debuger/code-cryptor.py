from argparse import ArgumentParser
import marshal as m
import base64 as b
import json
import csv
import os
import sys

class PyPrivate:
    def read(self, path):
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            sys.exit()

    def write(self, path, text):
        with open(path, 'w') as file:
            file.write(text)

    def Marshal(self, path):
        code = self.read(path)
        en = f'import marshal as m\nexec(m.loads({m.dumps(compile(code, "<string>", "exec"))}))'
        self.write(path, en)

    def Base64(self, path):
        en = f"import base64 as b\n" \
             f"data=lambda x:x({b.b16encode(self.read(path).encode())})\n" \
             f"exec(compile(data(b.b16decode),'<string>','exec'))"
        self.write(path, en)

    def DoubleBase64(self, path):
        self.Base64(path)
        self.Base64(path)

    def Layers(self, path):
        for _ in range(4):
            self.DoubleBase64(path)
            self.Marshal(path)

    def ProcessFiles(self, files, process_function):
        for file in files:
            if os.path.isfile(file):
                process_function(file)
                print(f"Processed {file} using {process_function.__name__}")
            else:
                print(f"File not found: {file}")

    def VerifyFile(self, path):
        try:
            with open(path, 'r') as file:
                file.read()
            return True
        except:
            return False

    def ProcessJson(self, path):
        data = self.read(path)
        json_data = json.dumps(json.loads(data))
        self.write(path, json_data)

    def ProcessCsv(self, path):
        data = self.read(path)
        lines = data.splitlines()
        reader = csv.reader(lines)
        csv_data = [row for row in reader]
        processed_data = '\n'.join([','.join(row) for row in csv_data])
        self.write(path, processed_data)

parser = ArgumentParser()
parser.add_argument('-e', '--encode', help='Encode a file: pyprivate -e file.py')
parser.add_argument('-d', '--decode', help='Decode a file: pyprivate -d file.py')
parser.add_argument('-l', '--layers', help='Apply layers of encoding to a file: pyprivate -l file.py')
parser.add_argument('-f', '--files', nargs='+', help='Process multiple files with the chosen method')
parser.add_argument('-v', '--verify', help='Verify if the file exists and is readable: pyprivate -v file.py')
parser.add_argument('-j', '--json', help='Process JSON file: pyprivate -j file.json')
parser.add_argument('-c', '--csv', help='Process CSV file: pyprivate -c file.csv')

args = parser.parse_args()

def App():
    pypriv = PyPrivate()
    out = []

    if args.verify:
        if pypriv.VerifyFile(args.verify):
            print(f"File {args.verify} is readable.")
        else:
            print(f"File {args.verify} is not readable or does not exist.")

    if args.encode:
        if os.path.isfile(args.encode):
            pypriv.Base64(args.encode)
            out.append(f'Base64 encoding applied to: {args.encode}')
        else:
            out.append(f'File not found: {args.encode}')

    if args.decode:
        if os.path.isfile(args.decode):
            pypriv.DoubleBase64(args.decode)
            out.append(f'Double Base64 decoding applied to: {args.decode}')
        else:
            out.append(f'File not found: {args.decode}')

    if args.layers:
        if os.path.isfile(args.layers):
            pypriv.Layers(args.layers)
            out.append(f'Layers applied to: {args.layers}')
        else:
            out.append(f'File not found: {args.layers}')

    if args.files:
        method = None
        if args.encode:
            method = pypriv.Base64
        elif args.decode:
            method = pypriv.DoubleBase64
        elif args.layers:
            method = pypriv.Layers

        if method:
            pypriv.ProcessFiles(args.files, method)
        else:
            print('No processing method specified.')

    if args.json:
        if os.path.isfile(args.json):
            pypriv.ProcessJson(args.json)
            out.append(f'JSON processing applied to: {args.json}')
        else:
            out.append(f'File not found: {args.json}')

    if args.csv:
        if os.path.isfile(args.csv):
            pypriv.ProcessCsv(args.csv)
            out.append(f'CSV processing applied to: {args.csv}')
        else:
            out.append(f'File not found: {args.csv}')

    if out:
        print('\n'.join(out))

if __name__ == "__main__":
    App()
