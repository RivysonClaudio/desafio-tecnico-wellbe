import os
import sys
import django
from dotenv import load_dotenv

def init():
    load_dotenv()
    
    # Sobe dois níveis para achar a raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
        
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.settings')
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    
    django.setup()