import os
from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, jsonify
from redis import Redis
from redis.exceptions import RedisError

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4096
db = Redis(host=os.getenv('REDIS_HOST', 'datos'), port=6379,
           decode_responses=True, socket_connect_timeout=3, socket_timeout=3)

@app.errorhandler(RedisError)
def database_error(error):
    return 'No se pudo conectar con el contenedor de datos. Revisa docker compose ps y los registros.', 503

@app.get('/')
def index():
    tasks = [{'id': key, 'title': value} for key, value in sorted(db.hgetall('tareas').items())]
    return render_template('index.html', tasks=tasks)

@app.post('/tareas')
def create():
    title = request.form.get('titulo', '').strip()
    if not title or len(title) > 120:
        return 'Escribe una tarea entre 1 y 120 caracteres.', 400
    db.hset('tareas', uuid4().hex, title)
    return redirect(url_for('index'), code=303)

@app.post('/tareas/<task_id>/eliminar')
def delete(task_id):
    db.hdel('tareas', task_id)
    return redirect(url_for('index'), code=303)

@app.get('/salud')
def health():
    db.ping()
    return jsonify(estado='ok', conexion_datos='ok', tareas=db.hlen('tareas'))
