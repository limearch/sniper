import requests
import os
import sys
import argparse
from bs4 import BeautifulSoup as Soup
from colorama import Fore, Style, init
from N4Tools.Design import ThreadAnimation, Color, Square

# تفعيل مكتبة colorama للعمل على جميع الأنظمة
init(autoreset=True)

# استخدام argparse لتمرير اسم المكتبة عبر سطر الأوامر
parser = argparse.ArgumentParser(description="Search and install Python packages from PyPi.")
parser.add_argument('library', nargs='?', type=str, help="The name of the Python package to search for")
parser.add_argument('--exact', action='store_true', help="Search for the exact package name")
parser.add_argument('--version', type=str, help="Specify a version to install")
parser.add_argument('--latest', action='store_true', help="Install the latest version of the package")
args = parser.parse_args()

Namelib = args.library

class Search_in_Pypi:
    def __init__(self, text):
        self.url = f'https://pypi.org/search/?q={Namelib.replace(" ", "+")}&o='
        self.MainLink = 'https://pypi.org'
        self.session = requests.Session()  # تحسين السرعة باستخدام الجلسة

    def getcode(self, page=1):
        url_with_page = f"{self.url}&page={page}"
        response = self.session.get(url_with_page)
        return Soup(response.text, 'html.parser')

    def GetNames(self):
        page = 1
        data = {}
        while True:
            soup = self.getcode(page)
            packages = soup.find_all('a', {'class': 'package-snippet'})
            if not packages:  
                break
            for Form in packages:
                name = Form.find('span', {'class': 'package-snippet__name'}).text
                version = Form.find('span', {'class': 'package-snippet__version'}).text
                href = self.MainLink + Form.get('href')
                if args.exact and name.lower() != Namelib.lower():
                    continue  # تجاهل المكتبات التي لا تتطابق تمامًا
                data[name] = {'version': version + ' ', 'href': href}
            page += 1
            if len(data) >= 20:
                break
        if data:
            return data
        else:
            print(Color().reader(f"\r[$YELLOW]@[$LRED]No results for: [$LGREEN]'{Namelib}'"))
            sys.exit()

    def StyleData(self):
        data = self.GetNames()
        out = ''
        index = 0
        options = {}
        sq = Square()
        sq.SETTINGS['square'] = ['╭─', '┝[$CYAN]─', '╰─', '─', '╯', '┥', '╮', '─']
        sq.SETTINGS['color'] = "[$LCYAN]"
        M = max([len(k + v['version']) for k, v in data.items()])
        for k, v in data.items():
            Num = '0' + str(index + 1) if index + 1 <= 9 else str(index + 1)
            out += f"[$LRED]([$NORMAL]{Num}[$LRED])[$LYELLOW]{k}:[$LGREEN]{v['version']}[$CYAN]{'─' * (M - len(k + v['version']))}\n"
            options[int(Num)] = v['href']
            index += 1
            if index >= 20:
                break
        return [sq.base(Color().reader(out[:-1])), options]

    def Choices(self):
        @ThreadAnimation()
        def rcv(Thread):
            out = self.StyleData()
            Thread.kill = True
            return out
        return rcv()

# دالة التثبيت
def GetComand(arg):
    @ThreadAnimation()
    def Get(Thread):
        soup = Soup(requests.get(arg).text, 'html.parser')
        for Form in soup.find_all('p', {'class': 'package-header__pip-instructions'}):
            for Name in Form.find_all('span', {'id': 'pip-command'}):
                Thread.kill = True
                return Name.text
    return Get()

# قائمة المفضلات
favorites = []

# دالة لتثبيت مكتبة أو إصدار محدد
def install_library(library_command):
    if args.version:
        os.system(f"pip install {library_command}=={args.version}")
    elif args.latest:
        os.system(f"pip install {library_command} --upgrade")
    else:
        os.system(f"pip install {library_command}")

# مدخل للأوامر
def main():
    if Namelib:
        get = Search_in_Pypi(Namelib).Choices()
        Choices = get[0]
        options = get[1]
        print(Choices)

    while True:
        command = input(Color().reader('[$LRED]Command[$GREEN]~[$LWIHTE]: ')).strip().lower()
        
        if command == "choices" and Namelib:
            print(Choices)
        elif command.startswith("install"):
            try:
                arg = command.split()[1]
                library_command = GetComand(options[int(arg)])
                print(Color().reader('[$YELLOW]@[$LBLUE]Installing...[$NORMAL]'))
                install_library(library_command)
            except (KeyError, ValueError, IndexError):
                print(f'Invalid library number: {arg}')
        elif command == "exit":
            break
        elif command.startswith("info"):
            try:
                arg = command.split()[1]
                library_url = options[int(arg)]
                print(f"More info at: {library_url}")
            except (KeyError, ValueError, IndexError):
                print(f'Invalid library number: {arg}')
        elif command.startswith("fav"):
            try:
                arg = command.split()[1]
                favorites.append(options[int(arg)])
                print(f"Library {arg} added to favorites.")
            except (KeyError, ValueError, IndexError):
                print(f'Invalid library number: {arg}')
        elif command == "showfav":
            if favorites:
                for i, fav in enumerate(favorites, 1):
                    print(f"{i}. {fav}")
            else:
                print("No favorites added yet.")
        elif command == "list":
            os.system("pip list")
        elif command.startswith("uninstall"):
            try:
                library_name = command.split()[1]
                os.system(f"pip uninstall -y {library_name}")
            except IndexError:
                print("Please provide the library name to uninstall.")
        else:
            print("Unknown command. Available commands: choices, install <number>, info <number>, fav <number>, showfav, list, uninstall <name>, exit")

if __name__ == "__main__":
    main()
