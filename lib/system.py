# File: lib/system.py | Language: Python
import os
import sys
import json
import pathlib
from typing import List

# إضافة المسار الحالي لضمان الوصول إلى الوحدات الأخرى في نفس المجلد
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))

class System:
    """
    فئة توفر معلومات حول بيئة النظام والأداة.
    """
    TOOL_NAME: str = 'py-env'
    BASE_PATH: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
    SUPPORTED_EXTENSIONS = ['.c', '.py', '.sh', '.dart', '.java', '.php', '.js', '.pyc', '.cpp']

    @property
    def BIN_PATH(self) -> str:
        """
        يحصل على مسار مجلد bin الخاص ببيئة Python الحالية.
        """
        return str(pathlib.Path(sys.executable).parent)

    @property
    def TOOL_PATH(self) -> str:
        """
        يحصل على المسار الأساسي للأداة.
        """
        return str(self.BASE_PATH)

    @property
    def PLATFORM(self) -> str:
        """
        يحدد نظام التشغيل الحالي (win, macosx, termux, linux).
        """
        if sys.platform in ('win32', 'cygwin'):
            return 'win'
        if sys.platform == 'darwin':
            return 'macosx'
        if 'com.termux' in os.environ.get('PWD', ''):
            return 'termux'
        if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
            return 'linux'
        return 'unknown'

    @property
    def SYSTEM_PACKAGES(self) -> List[str]:
        """
        يسرد الملفات التنفيذية في مسار bin الخاص بالنظام.
        """
        try:
            return os.listdir(self.BIN_PATH)
        except FileNotFoundError:
            return []

    def get_hackermode_packages(self) -> List[str]:
        """
        يجمع قائمة بجميع الأدوات والسكربتات القابلة للتشغيل ضمن المشروع.
        """
        packages = set()
        
        # مسارات البحث عن الحزم
        bin_path = self.BASE_PATH / 'bin'
        tools_path = self.BASE_PATH / 'tools'

        # البحث في مجلد bin
        if bin_path.is_dir():
            for file_name in os.listdir(bin_path):
                name, ext = os.path.splitext(file_name)
                if ext in self.SUPPORTED_EXTENSIONS:
                    packages.add(name)

        # البحث في مجلد tools
        if tools_path.is_dir():
            for tool_name in os.listdir(tools_path):
                if (tools_path / tool_name).is_dir():
                    packages.add(tool_name)
        
        return list(packages)

class DataBase:
    """
    فئة للتعامل مع قاعدة بيانات Firebase.
    """
    def __init__(self):
        # !! تحذير أمني: تم إزالة المفاتيح الصلبة !!
        # يجب تخزين هذه المعلومات في متغيرات البيئة أو ملف إعدادات آمن.
        self.config = {
            "apiKey": os.environ.get("FIREBASE_API_KEY"),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
        }

        if not self.config["apiKey"]:
            raise ValueError("Firebase API Key not found. Please set the FIREBASE_API_KEY environment variable.")

        try:
            import pyrebase
            import requests
            self.requests = requests
            self.firebase = pyrebase.initialize_app(self.config)
            self.auth = self.firebase.auth()
        except ImportError:
            print("Error: 'pyrebase' or 'requests' library not found. Please install it using 'pip install pyrebase4 requests'")
            sys.exit(1)

    def sign_in(self, email, password):
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            return {'status_code': 200, 'data': user}
        except self.requests.exceptions.HTTPError as e:
            return {'status_code': 400, 'data': json.loads(e.strerror)}

    # ... باقي دوال Firebase ...

# إنشاء نسخة واحدة من الكلاس لاستخدامها في المشروع
System = System()