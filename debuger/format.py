import os
import json
import autopep8
from jsbeautifier import beautify
import subprocess
import argparse
import hashlib
import shutil


# 1. عمل نسخة احتياطية للملف
def backup_file(file_path):
    backup_path = file_path + ".bak"
    shutil.copy(file_path, backup_path)
    print(f"Backup created for {file_path}")


# 2. فحص إذا كان الملف بحاجة للتنسيق
def needs_formatting(original_content, formatted_content):
    return original_content != formatted_content


# 3. حساب الـ hash للملفات لتجنب إعادة التنسيق
def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


# 4. تهيئة ملف معين بناءً على امتداده
def format_file(file_path, spaces=4, backup=False):
    extension = os.path.splitext(file_path)[1]
    try:
        # عمل نسخة احتياطية إذا كان الخيار موجودًا
        if backup:
            backup_file(file_path)

        # عملية التنسيق حسب نوع الملف
        if extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            formatted_content = json.dumps(data, indent=spaces)
            with open(file_path, 'r+', encoding='utf-8') as file:
                original_content = file.read()
                if needs_formatting(original_content, formatted_content):
                    file.seek(0)
                    file.write(formatted_content)
                    file.truncate()
                    print(f"Formatted JSON file: {file_path}")

        elif extension == '.py':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # إعداد autopep8 مع عدد المسافات المحدد
            options = {
                'aggressive': 1,
                'indent_size': spaces
            }
            formatted_content = autopep8.fix_code(content, options=options)
            if needs_formatting(content, formatted_content):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(formatted_content)
                print(f"Formatted Python file: {file_path}")

        elif extension == '.js':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # إعداد jsbeautifier مع عدد المسافات المحدد
            options = {
                "indent_size": spaces
            }
            formatted_content = beautify(content, options)
            if needs_formatting(content, formatted_content):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(formatted_content)
                print(f"Formatted JavaScript file: {file_path}")

        elif extension == '.sh':
            subprocess.run(['shfmt', '-w', '-i', str(spaces), file_path])
            print(f"Formatted Shell script file: {file_path}")

        elif extension == '.c' or extension == '.h':
            subprocess.run(['clang-format', '-i', file_path])
            print(f"Formatted C/C++ file: {file_path}")

        elif extension == '.java':
            subprocess.run(['clang-format', '-i', file_path])
            print(f"Formatted Java file: {file_path}")

        elif extension == '.dart':
            subprocess.run(['dart', 'format', file_path])
            print(f"Formatted Dart file: {file_path}")

        else:
            print(f"File type '{extension}' not supported for formatting.")

    except Exception as e:
        print(f"Error formatting {file_path}: {e}")


# 5. تهيئة جميع الملفات داخل مجلد معين
def format_directory(directory, spaces=4, backup=False):
    for root, _, files in os.walk(directory):
        for file in files:
            format_file(os.path.join(root, file), spaces, backup)


# 6. دعم استخدام الاختصارات من سطر الأوامر
def main():
    parser = argparse.ArgumentParser(description="Multi-File Formatter")
    parser.add_argument("path", help="Path to file or directory")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Format all files in directory recursively")
    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="Create a backup before formatting")
    parser.add_argument(
        "-s",
        "--spaces",
        type=int,
        default=4,
        help="Number of spaces to use for indentation (default: 4)")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        format_directory(args.path, spaces=args.spaces, backup=args.backup)
    else:
        format_file(args.path, spaces=args.spaces, backup=args.backup)


if __name__ == "__main__":
    main()
