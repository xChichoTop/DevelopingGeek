"""Verificación previa con procesos locales de Gunicorn y Redis en Linux."""
import argparse
import importlib.metadata
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def wait_url(url, process):
    for _ in range(150):
        if process.poll() is not None:
            raise RuntimeError('El servicio terminó antes de iniciar')
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise TimeoutError('El servicio no respondió dentro del tiempo de espera')


def run(output, redis_server):
    project = Path(__file__).resolve().parents[1]
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    server = redis_server or shutil.which('redis-server')
    if not server:
        raise RuntimeError('Indica un ejecutable real de Redis mediante --redis-server o instala redis-server')
    server = str(Path(server).resolve())
    redis_port, web_port = free_port(), free_port()
    env = {**os.environ, 'REDIS_HOST': '127.0.0.1', 'REDIS_PORT': str(redis_port),
           'WEB_URL': f'http://127.0.0.1:{web_port}'}
    with tempfile.TemporaryDirectory(prefix='gestor-ci-') as tmp:
        args = [server, '--bind', '127.0.0.1', '--port', str(redis_port), '--dir', tmp,
                '--appendonly', 'yes', '--appendfsync', 'always', '--save', '']
        processes = []
        with (output / 'redis.log').open('w') as redis_log, (output / 'gunicorn.log').open('w') as web_log:
            try:
                redis = subprocess.Popen(args, stdout=redis_log, stderr=redis_log)
                processes.append(redis)
                web = subprocess.Popen([sys.executable, '-m', 'gunicorn', '--bind', f'127.0.0.1:{web_port}',
                                        '--workers', '2', '--access-logfile', '-', 'app:app'], cwd=project,
                                       env=env, stdout=web_log, stderr=web_log)
                processes.append(web)
                wait_url(env['WEB_URL'] + '/salud', web)
                subprocess.run([sys.executable, str(project / 'ci/pruebas_ci.py'), '--salida', str(output)],
                               env=env, check=True)
                seed = [sys.executable, str(project / 'ci/persistencia.py')]
                subprocess.run([*seed, 'guardar', '--salida', str(output)], env=env, check=True)
                redis.terminate()
                redis.wait(timeout=10)
                redis = subprocess.Popen(args, stdout=redis_log, stderr=redis_log)
                processes.append(redis)
                wait_url(env['WEB_URL'] + '/salud', web)
                subprocess.run([*seed, 'verificar', '--salida', str(output)], env=env, check=True)
                manifest = {
                    'fecha_utc': datetime.now(timezone.utc).isoformat(),
                    'entorno': 'Procesos locales de Gunicorn y Redis sin contenedores',
                    'python': sys.version.split()[0],
                    'flask': importlib.metadata.version('flask'),
                    'redis_cliente': importlib.metadata.version('redis'),
                    'gunicorn': importlib.metadata.version('gunicorn'),
                    'redis_servidor': subprocess.check_output([server, '--version'], text=True).strip(),
                    'pruebas_http_redis': 12,
                    'pruebas_persistencia': 1,
                    'resultado': 'APROBADA'
                }
                (output / 'entorno.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
                print(json.dumps(manifest, ensure_ascii=False, indent=2))
            finally:
                for process in reversed(processes):
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--salida', type=Path, default=Path('reportes/local'))
    parser.add_argument('--redis-server')
    args = parser.parse_args()
    raise SystemExit(run(args.salida, args.redis_server))
