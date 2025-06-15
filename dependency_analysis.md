# Análise de Dependências Identificadas

## Bibliotecas Externas Encontradas nos Imports:

### Processamento de Imagem e OCR:
- PIL (Pillow) - para processamento de imagem
- cv2 (opencv-python) - para visão computacional
- pytesseract - para OCR
- numpy - para operações numéricas

### Processamento de Documentos:
- PyPDF2 - para manipulação de PDFs
- magic (python-magic) - para detecção de tipos de arquivo

### Fuzzy Matching:
- fuzzywuzzy - para correspondência difusa de strings

### Async e WebSocket:
- aiohttp - para requisições HTTP assíncronas
- channels - para WebSocket support
- channels.db, channels.generic.websocket

### Task Queue:
- celery - para processamento assíncrono

### Configuração:
- decouple - para configuração via variáveis de ambiente
- dj_database_url - para configuração de banco via URL

### Monitoramento:
- psutil - para monitoramento do sistema

### Cache:
- redis - para cache e broker do Celery

### HTTP:
- requests - para requisições HTTP
- aiohttp - para requisições assíncronas

### Testing:
- pytest - para testes
- unittest.mock - built-in Python

### Utilities:
- xml.etree.ElementTree - built-in Python
- base64, hashlib, io, json, logging, mimetypes, os, sys, tempfile, threading, time, uuid, urllib.parse - built-in Python

## Status no requirements.txt atual:
✅ Presentes: django-extensions, django-debug-toolbar, requests, redis, django-redis, psycopg2-binary, dj-database-url, python-decouple
❌ Faltando: Pillow, opencv-python, pytesseract, numpy, PyPDF2, python-magic, fuzzywuzzy, aiohttp, channels, channels-redis, celery, psutil, pytest

