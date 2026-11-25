"""Guardar y verificar un registro al recrear Redis sin borrar su volumen."""
import argparse
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from redis import Redis


def main(action, output):
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / 'registro-persistencia.json'
    db = Redis(host=os.getenv('REDIS_HOST', 'datos'), port=int(os.getenv('REDIS_PORT', '6379')),
               decode_responses=True, socket_connect_timeout=3, socket_timeout=3)
    status, detail = 'APROBADA', ''
    state = None
    try:
        if action == 'guardar':
            state = {'clave': 'ci-persistencia-' + uuid4().hex, 'valor': 'Verificar persistencia ' + uuid4().hex}
            state_path.write_text(json.dumps(state), encoding='utf-8')
            db.hset('tareas', state['clave'], state['valor'])
            if db.hget('tareas', state['clave']) != state['valor']:
                raise AssertionError('El registro inicial no coincide')
            print('Registro de persistencia guardado')
            return 0
        state = json.loads(state_path.read_text(encoding='utf-8'))
        actual = db.hget('tareas', state['clave'])
        if actual != state['valor']:
            raise AssertionError('Redis no conservó el registro esperado')
        base = os.getenv('WEB_URL', 'http://127.0.0.1:5000').rstrip('/')
        with urllib.request.urlopen(base + '/', timeout=10) as response:
            if state['valor'] not in response.read().decode():
                raise AssertionError('La aplicación no consulta el registro conservado')
    except Exception as error:
        status, detail = 'FALLIDA', str(error)
    finally:
        if action == 'verificar' and state is not None:
            try:
                db.hdel('tareas', state['clave'])
            except Exception as error:
                status, detail = 'FALLIDA', detail + ' Error de limpieza: ' + str(error)
        db.close()
    report = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'prueba': 'Persistencia de Redis',
              'resultado': status, 'detalle': detail}
    (output / 'persistencia.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    root = ET.Element('testsuite', name='Persistencia', tests='1', failures='0' if status == 'APROBADA' else '1', errors='0')
    case = ET.SubElement(root, 'testcase', classname='Persistencia', name='conservar_registro_al_recrear_redis')
    if status != 'APROBADA':
        ET.SubElement(case, 'failure').text = detail
    ET.ElementTree(root).write(output / 'junit-persistencia.xml', encoding='utf-8', xml_declaration=True)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if status == 'APROBADA' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=['guardar', 'verificar'])
    parser.add_argument('--salida', type=Path, default=Path('/tmp/reportes'))
    args = parser.parse_args()
    raise SystemExit(main(args.accion, args.salida))
