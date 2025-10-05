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
parser.add_argument('library', type=str, help="The name of the Python package to search for")
args = parser.parse_args()

Namelib = args.library

class Search_in_Pypi:
    def __init__(self, text):
        self.url = f'https://pypi.org/search/?q={Namelib.replace(" ", "+")}&o='
        self.MainLink = 'https://pypi.org'
        self.session = requests.Session()  # تحسين السرعة باستخدام الجلسة

    def getcode(self, page=1):
        # تحسين دقة البحث بجلب النتائج مع دعم صفحات متعددة
        url_with_page = f"{self.url}&page={page}"
        response = self.session.get(url_with_page)
        return Soup(response.text, 'html.parser')

    def GetNames(self):
        page = 1
        data = {}
        while True:
            soup = self.getcode(page)
            packages = soup.find_all('a', {'class': 'package-snippet'})
            if not packages:  # التوقف إذا لم تكن هناك المزيد من النتائج
                break
            for Form in packages:
                name = Form.find('span', {'class': 'package-snippet__name'}).text
                version = Form.find('span', {'class': 'package-snippet__version'}).text
                href = self.MainLink + Form.get('href')
                data[name] = {'version': version + ' ', 'href': href}
            page += 1
            if len(data) >= 20:  # إظهار أول 20 نتيجة فقط لتحسين الأداء
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
            if index >= 20:  # عرض أول 20 نتيجة فقط
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

# مدخل للأوامر
def main():
    get = Search_in_Pypi(Namelib).Choices()
    Choices = get[0]
    options = get[1]
    print(Choices)
    
    while True:
        command = input(Color().reader('[$LRED]Command[$GREEN]~[$LWIHTE]: ')).strip().lower()
        if command == "choices":
            print(Choices)
        elif command.startswith("install"):
            try:
                arg = command.split()[1]
                command = GetComand(options[int(arg)])
                print(Color().reader('[$YELLOW]@[$LBLUE]Installing...[$NORMAL]'))
                os.system(command)
            except (KeyError, ValueError, IndexError):
                print(f'Invalid library number: {arg}')
        elif command == "exit":
            break
        else:
            print("Unknown command. Available commands: choices, install <number>, exit")

if __name__ == "__main__":
    main()
