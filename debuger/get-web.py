from N4Tools.Design import Color
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import os
import validators
import readline
from concurrent.futures import ThreadPoolExecutor

color = Color()
commands = ['flask <flask filename="">', 'main', 'clear']

flask_template = """
# Flask - Server
from flask import Flask, render_template
from random import randint as PORT

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

app.run(port=PORT(999, 65535))
"""

def autocomplete(text, state):
    options = [cmd for cmd in commands if cmd.startswith(text)]
    return options[state] if state < len(options) else None

readline.set_completer(autocomplete)
readline.parse_and_bind("tab: complete")

url = input(f"Enter URL{color.LYELLOW}/$ ")

prompt_string = (f"{color.BLUE}┌──{color.CYAN}({color.LBLUE}hack💀sniper{color.CYAN})-[{color.LWIHTE}GET-WEB{color.BLUE}]\n"
                 f"{color.BLUE}└─{color.LRED}#{color.WIHTE} ")

def format_html_file(html_file):
    with open(html_file, 'r+', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        file.seek(0)
        file.write(soup.prettify())
        file.truncate()

def create_project_files(project_dir, template_dir, static_dir, flask_main_file):
    print(f"\n{color.LCYAN}Creating required files:\n")
    directories = [project_dir, template_dir, static_dir]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"{color.LWIHTE}[{color.LGREEN}CREATED ✓{color.LWIHTE}]: {directory}")

    if not os.path.exists(flask_main_file):
        with open(flask_main_file, "w") as main_file:
            main_file.write(flask_template)
            print(f"{color.LWIHTE}[{color.LGREEN}CREATED ✓{color.LWIHTE}]: {flask_main_file}")

def download_file(session, url, save_path):
    try:
        response = session.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(save_path, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
        print(f"{color.LWIHTE}[{color.LGREEN}DONE ✓{color.LWIHTE}] {save_path}")
    except Exception as e:
        print(f"{color.LWIHTE}[{color.LRED}FAILED ×{color.LWIHTE}] {save_path} - {e}")

def extract_and_download_resources(url, template_dir, static_dir):
    session = requests.Session()
    try:
        response = session.get(url)
    except Exception as e:
        print(f"{color.LRED}Failed to connect: {e}{color.LWIHTE}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    parsed_url = urlparse(url)
    download_file(session, url, os.path.join(template_dir, "index.html"))

    def download_resources(tag, attribute):
        resources = [(urljoin(url, resource[attribute]), os.path.join(static_dir, os.path.basename(resource[attribute])))
                     for resource in soup.find_all(tag) if resource.get(attribute)]
        return resources

    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: download_file(session, *args), 
                     download_resources('link', 'href') +
                     download_resources('script', 'src') +
                     download_resources('img', 'src') +
                     download_resources('video', 'src'))

def modify_html_paths(html_file, static_dir):
    with open(html_file, 'r+', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

        for tag in soup.find_all(['link', 'script', 'img']):
            attribute = 'href' if tag.name == 'link' else 'src'
            if tag.get(attribute):
                tag[attribute] = os.path.join(static_dir, os.path.basename(tag[attribute]))

        file.seek(0)
        file.write(str(soup))
        file.truncate()

def main(project_dir):
    template_dir = os.path.join(project_dir, 'templates')
    static_dir = os.path.join(project_dir, 'static')
    flask_main_file = os.path.join(project_dir, "__main__.py")
    index_html = os.path.join(template_dir, 'index.html')

    if not validators.url(url):
        print(f"Invalid URL: {color.LRED}{url}{color.LWIHTE}")
        return

    create_project_files(project_dir, template_dir, static_dir, flask_main_file)
    extract_and_download_resources(url, template_dir, static_dir)
    modify_html_paths(index_html, "../static")
    format_html_file(index_html)

project_dir = 'html'

if __name__ == "__main__":
    while True:
        command = input(prompt_string)
        if command == "main":
            exit()
        elif command.lower() in ['clear', 'cls', 'c']:
            os.system("clear")
        elif "flask" in command:
            soup = BeautifulSoup(command, 'html.parser')
            flask = soup.find('flask')
            project_dir = flask.get('filename')
            main(project_dir)
        elif command == 'run':
            os.system(f"python {project_dir}")
