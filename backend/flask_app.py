from flask import Flask
import os
import sys

# Add Django project to path
sys.path.insert(0, '/home/ubuntu/ceres_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ceres_project.settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
django_app = get_wsgi_application()

app = Flask(__name__)

@app.route('/')
def index():
    return "CERES Backend API - Django running on Flask"

@app.route('/api/<path:path>')
def django_api(path):
    # Proxy to Django
    from django.test import Client
    client = Client()
    response = client.get(f'/api/{path}')
    return response.content, response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

