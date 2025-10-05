from argparse import ArgumentParser
import marshal as m
import base64 as b
import json
import csv
import os
import sys
import zlib
from cryptography.fernet import Fernet

class PyPrivate:
    def __init__(self):
        self.key = Fernet.generate_key()  # مفتاح للتشفير باستخدام AES
        self.cipher_suite = Fernet(self.key)

    def read(self, path):
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            sys.exit()

    def write(self, path, text):
        try:
            with open(path, 'w') as file:
                file.write(text)
        except Exception as e:
            print(f"Error writing to file {path}: {e}")
            sys.exit()

    # Base64 encoding
    def Base64(self, path):
        try:
            encoded = b.b64encode(self.read(path).encode()).decode()
            self.write(path, encoded)
        except Exception as e:
            print(f"Error encoding file {path} with Base64: {e}")

    # Base64 decoding
    def Base64Decode(self, path):
        try:
            decoded = b.b64decode(self.read(path)).decode()
            self.write(path, decoded)
        except Exception as e:
            print(f"Error decoding file {path} with Base64: {e}")

    # AES encryption
    def AESEncrypt(self, path):
        try:
            encrypted_data = self.cipher_suite.encrypt(self.read(path).encode())
            self.write(path, encrypted_data.decode())
        except Exception as e:
            print(f"Error encrypting file {path} with AES: {e}")

    # AES decryption
    def AESDecrypt(self, path):
        try:
            decrypted_data = self.cipher_suite.decrypt(self.read(path).encode())
            self.write(path, decrypted_data.decode())
        except Exception as e:
            print(f"Error decrypting file {path} with AES: {e}")

    # XOR encryption (simple encryption method)
    def XOR(self, path, key):
        try:
            data = self.read(path)
            encrypted_data = ''.join(chr(ord(c) ^ key) for c in data)
            self.write(path, encrypted_data)
        except Exception as e:
            print(f"Error encrypting file {path} with XOR: {e}")

    def XORDecrypt(self, path, key):
        self.XOR(path, key)  # XOR encryption and decryption are the same operation

    # Compression and Decompression
    def Compress(self, path):
        try:
            data = self.read(path)
            compressed_data = zlib.compress(data.encode())
            self.write(path, compressed_data.decode('latin1'))  # latin1 to handle binary safely
        except Exception as e:
            print(f"Error compressing file {path}: {e}")

    def Decompress(self, path):
        try:
            data = self.read(path)
            decompressed_data = zlib.decompress(data.encode('latin1')).decode()
            self.write(path, decompressed_data)
        except Exception as e:
            print(f"Error decompressing file {path}: {e}")

    # File verification
    def VerifyFile(self, path):
        return os.path.isfile(path) and os.access(path, os.R_OK)

    # JSON and CSV Processing
    def ProcessJson(self, path):
        try:
            data = self.read(path)
            json_data = json.dumps(json.loads(data), indent=4)
            self.write(path, json_data)
        except Exception as e:
            print(f"Error processing JSON file {path}: {e}")

    def ProcessCsv(self, path):
        try:
            data = self.read(path)
            lines = data.splitlines()
            reader = csv.reader(lines)
            csv_data = [row for row in reader]
            processed_data = '\n'.join([','.join(row) for row in csv_data])
            self.write(path, processed_data)
        except Exception as e:
            print(f"Error processing CSV file {path}: {e}")

    # Preview file content
    def Preview(self, path, length=100):
        try:
            data = self.read(path)
            print(f"Preview ({length} characters):\n{data[:length]}")
        except Exception as e:
            print(f"Error previewing file {path}: {e}")

# Argument parsing
parser = ArgumentParser()
parser.add_argument('-e', '--encode', help='Base64 encode a file: pyprivate -e file.py')
parser.add_argument('-ed', '--decode', help='Base64 decode a file: pyprivate -ed file.py')
parser.add_argument('-aes', '--aes-encrypt', help='AES encrypt a file: pyprivate -aes file.py')
parser.add_argument('-aesd', '--aes-decrypt', help='AES decrypt a file: pyprivate -aesd file.py')
parser.add_argument('-xor', '--xor-encrypt', type=int, help='XOR encrypt a file with a key: pyprivate -xor file.py 123')
parser.add_argument('-xord', '--xor-decrypt', type=int, help='XOR decrypt a file with a key: pyprivate -xord file.py 123')
parser.add_argument('-v', '--verify', help='Verify if a file exists and is readable: pyprivate -v file.py')
parser.add_argument('-j', '--json', help='Process JSON file: pyprivate -j file.json')
parser.add_argument('-c', '--csv', help='Process CSV file: pyprivate -c file.csv')
parser.add_argument('-p', '--preview', help='Preview the content of a file: pyprivate -p file.py')
parser.add_argument('-pl', '--preview-length', type=int, default=100, help='Specify the length of the preview')
parser.add_argument('-z', '--compress', help='Compress a file before encoding: pyprivate -z file.py')
parser.add_argument('-zd', '--decompress', help='Decompress a file after encoding: pyprivate -zd file.py')
parser.add_argument('-o', '--output', help='Specify output file path')

args = parser.parse_args()

def App():
    pypriv = PyPrivate()
    out = []

    def write_output(path, data):
        if args.output:
            pypriv.write(args.output, data)
        else:
            pypriv.write(path, data)

    if args.verify:
        if pypriv.VerifyFile(args.verify):
            print(f"File {args.verify} is readable.")
        else:
            print(f"File {args.verify} is not readable or does not exist.")

    if args.encode:
        if pypriv.VerifyFile(args.encode):
            pypriv.Base64(args.encode)
            out.append(f'Base64 encoding applied to: {args.encode}')
        else:
            out.append(f'File not found: {args.encode}')

    if args.decode:
        if pypriv.VerifyFile(args.decode):
            pypriv.Base64Decode(args.decode)
            out.append(f'Base64 decoding applied to: {args.decode}')
        else:
            out.append(f'File not found: {args.decode}')

    if args.aes_encrypt:
        if pypriv.VerifyFile(args.aes_encrypt):
            pypriv.AESEncrypt(args.aes_encrypt)
            out.append(f'AES encryption applied to: {args.aes_encrypt}')
        else:
            out.append(f'File not found: {args.aes_encrypt}')

    if args.aes_decrypt:
        if pypriv.VerifyFile(args.aes_decrypt):
            pypriv.AESDecrypt(args.aes_decrypt)
            out.append(f'AES decryption applied to: {args.aes_decrypt}')
        else:
            out.append(f'File not found: {args.aes_decrypt}')

    if args.xor_encrypt:
        if pypriv.VerifyFile(args.xor_encrypt):
            pypriv.XOR(args.xor_encrypt, args.xor_encrypt)
            out.append(f'XOR encryption applied to: {args.xor_encrypt}')
        else:
            out.append(f'File not found: {args.xor_encrypt}')

    if args.xor_decrypt:
        if pypriv.VerifyFile(args.xor_decrypt):
            pypriv.XORDecrypt(args.xor_decrypt, args.xor_decrypt)
            out.append(f'XOR decryption applied to: {args.xor_decrypt}')
        else:
            out.append(f'File not found: {args.xor_decrypt}')

    if args.json:
        if pypriv.VerifyFile(args.json):
            pypriv.ProcessJson(args.json)
            out.append(f'JSON processing applied to: {args.json}')
        else:
            out.append(f'File not found: {args.json}')

    if args.csv:
        if pypriv.VerifyFile(args.csv):
            pypriv.ProcessCsv(args.csv)
            out.append(f'CSV processing applied to: {args.csv}')
        else:
            out.append(f'File not found: {args.csv}')

    if args.preview:
        if pypriv.VerifyFile(args.preview):
            pypriv.Preview(args.preview, args.preview_length)
        else:
            out.append(f'File not found: {args.preview}')

    if args.compress:
        if pypriv.VerifyFile(args.compress):
            pypriv.Compress(args.compress)
            out.append(f'Compression applied to: {args.compress}')
        else:
            out.append(f'File not found: {args.compress}')

    if args.decompress:
        if pypriv.VerifyFile(args.decompress):
            pypriv.Decompress(args.decompress)
            out.append(f'Decompression applied to: {args.decompress}')
        else:
            out.append(f'File not found: {args.decompress}')

    if out:
        print('\n'.join(out))

if __name__ == "__main__":
    App()
