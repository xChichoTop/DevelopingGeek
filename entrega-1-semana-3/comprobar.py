"""Prueba HTTP y Redis reales. Ejecutar dentro de web con Docker Compose."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4
from redis import Redis

base = os.getenv('WEB_URL', 'http://127.0.0.1:5000')
db = Redis(host=os.getenv('REDIS_HOST', 'datos'), decode_responses=True, socket_connect_timeout=3, socket_timeout=3)
results = []

def get(path):
    with urllib.request.urlopen(base + path, timeout=10) as response:
        return response.status, response.read().decode()

def post(path, title=None):
    data = urllib.parse.urlencode({'titulo': title}).encode() if title is not None else b''
    try:
        with urllib.request.urlopen(urllib.request.Request(base + path, data=data), timeout=10) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()

def check(name, condition):
    assert condition, name
    results.append({'prueba': name, 'resultado': 'APROBADA'})

prefix = 'Prueba ' + uuid4().hex[:8]
try:
    check('Interfaz HTTP disponible', get('/')[0] == 200)
    status, health = get('/salud')
    check('Conexion real con Redis', status == 200 and json.loads(health)['conexion_datos'] == 'ok')
    check('Rechazo de tarea vacia', post('/tareas', ' ')[0] == 400)
    check('Rechazo de mas de 120 caracteres', post('/tareas', 'a' * 121)[0] == 400)
    title = prefix + ' preparar entrega'
    check('Creacion por HTTP', post('/tareas', title)[0] == 200)
    records = db.hgetall('tareas')
    key = next(k for k, v in records.items() if v == title)
    check('Lectura directa en Redis del registro creado', records[key] == title)
    check('Consulta visible en interfaz', title in get('/')[1])
    unsafe = prefix + ' <script>alert(1)</script>'
    post('/tareas', unsafe)
    check('Escape de HTML en interfaz', '&lt;script&gt;alert(1)&lt;/script&gt;' in get('/')[1] and unsafe not in get('/')[1])
    check('Eliminacion por HTTP', post('/tareas/' + key + '/eliminar')[0] == 200 and not db.hexists('tareas', key))
finally:
    for key, value in db.hgetall('tareas').items():
        if value.startswith(prefix):
            db.hdel('tareas', key)
print(json.dumps({'pruebas': results, 'total': len(results)}, ensure_ascii=False, indent=2))
