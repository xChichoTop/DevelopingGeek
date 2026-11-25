"""Pruebas de integración HTTP y Redis con informes JUnit y JSON."""
import argparse
import json
import os
import time
import traceback
import unittest
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from redis import Redis

BASE = os.getenv('WEB_URL', 'http://127.0.0.1:5000').rstrip('/')


def connection():
    return Redis(host=os.getenv('REDIS_HOST', 'datos'),
                 port=int(os.getenv('REDIS_PORT', '6379')), decode_responses=True,
                 socket_connect_timeout=3, socket_timeout=3)


def http(path, data=None, follow=True):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect())
    payload = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with opener.open(urllib.request.Request(BASE + path, data=payload), timeout=10) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


class Integracion(unittest.TestCase):
    def setUp(self):
        self.db = connection()
        self.prefix = 'CI-' + uuid4().hex + ' '
        self.connected = False
        self.addCleanup(self.cleanup_records)
        self.db.ping()
        self.connected = True

    def cleanup_records(self):
        try:
            if self.connected:
                for key, value in self.db.hgetall('tareas').items():
                    if value.startswith(self.prefix):
                        self.db.hdel('tareas', key)
        finally:
            self.db.close()

    def create(self, title):
        status, body = http('/tareas', {'titulo': title}, follow=False)
        self.assertEqual(status, 303, body)
        return next(key for key, value in self.db.hgetall('tareas').items() if value == title.strip())

    def test_01_interfaz_disponible(self):
        status, body = http('/')
        self.assertEqual(status, 200)
        self.assertIn('Mis tareas', body)

    def test_02_salud_y_conteo_reales(self):
        status, body = http('/salud')
        data = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(data['estado'], 'ok')
        self.assertEqual(data['conexion_datos'], 'ok')
        self.assertEqual(data['tareas'], self.db.hlen('tareas'))

    def test_03_rechazar_titulo_vacio(self):
        before = self.db.hgetall('tareas')
        self.assertEqual(http('/tareas', {'titulo': '   '})[0], 400)
        self.assertEqual(self.db.hgetall('tareas'), before)

    def test_04_rechazar_mas_de_120_caracteres(self):
        before = self.db.hgetall('tareas')
        self.assertEqual(http('/tareas', {'titulo': 'a' * 121})[0], 400)
        self.assertEqual(self.db.hgetall('tareas'), before)

    def test_05_eliminar_espacios_en_extremos(self):
        title = self.prefix + 'revisar pipeline'
        key = self.create('  ' + title + '  ')
        self.assertEqual(self.db.hget('tareas', key), title)

    def test_06_aceptar_limite_de_120_caracteres(self):
        title = self.prefix + 'a' * (120 - len(self.prefix))
        key = self.create(title)
        self.assertEqual(len(self.db.hget('tareas', key)), 120)

    def test_07_crear_por_http_y_leer_en_redis(self):
        title = self.prefix + 'construir imagen'
        key = self.create(title)
        self.assertEqual(self.db.hget('tareas', key), title)

    def test_08_consultar_tarea_en_interfaz(self):
        title = self.prefix + 'consultar tarea'
        self.create(title)
        self.assertIn(title, http('/')[1])

    def test_09_escapar_html(self):
        title = self.prefix + '<script>alert(1)</script>'
        self.create(title)
        body = http('/')[1]
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', body)
        self.assertNotIn(title, body)

    def test_10_eliminar_tarea_por_http(self):
        title = self.prefix + 'eliminar tarea'
        key = self.create(title)
        self.assertEqual(http('/tareas/' + key + '/eliminar', {}, follow=False)[0], 303)
        self.assertFalse(self.db.hexists('tareas', key))
        self.assertNotIn(title, http('/')[1])

    def test_11_eliminar_identificador_inexistente(self):
        before = self.db.hgetall('tareas')
        self.assertEqual(http('/tareas/' + uuid4().hex + '/eliminar', {}, follow=False)[0], 303)
        self.assertEqual(self.db.hgetall('tareas'), before)

    def test_12_rechazar_solicitud_mayor_a_4096_bytes(self):
        before = self.db.hgetall('tareas')
        self.assertEqual(http('/tareas', {'titulo': 'a' * 5000})[0], 413)
        self.assertEqual(self.db.hgetall('tareas'), before)


class Resultado(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def startTest(self, test):
        self.started = time.monotonic()
        super().startTest(test)

    def record(self, test, status, error=None):
        detail = ''.join(traceback.format_exception(*error)) if error else ''
        previous = next((item for item in self.records if item['prueba'] == test.id()), None)
        if previous:
            if status == 'ERROR' or previous['resultado'] == 'APROBADA':
                previous['resultado'] = status
            previous['detalle'] += detail
            previous['segundos'] = round(time.monotonic() - self.started, 6)
        else:
            self.records.append({'prueba': test.id(), 'resultado': status,
                                 'segundos': round(time.monotonic() - self.started, 6), 'detalle': detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, 'APROBADA')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, 'FALLIDA', err)

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, 'ERROR', err)


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    result = unittest.TextTestRunner(verbosity=2, resultclass=Resultado).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Integracion))
    stamp = datetime.now(timezone.utc).isoformat()
    failures = sum(item['resultado'] == 'FALLIDA' for item in result.records)
    errors = sum(item['resultado'] == 'ERROR' for item in result.records)
    root = ET.Element('testsuite', name='HTTP y Redis', tests=str(result.testsRun),
                      failures=str(failures), errors=str(errors), timestamp=stamp)
    for record in result.records:
        case = ET.SubElement(root, 'testcase', classname='Integracion', name=record['prueba'].split('.')[-1],
                             time=str(record['segundos']))
        if record['resultado'] != 'APROBADA':
            node = ET.SubElement(case, 'failure' if record['resultado'] == 'FALLIDA' else 'error')
            node.text = record['detalle']
    ET.indent(root)
    ET.ElementTree(root).write(output / 'junit.xml', encoding='utf-8', xml_declaration=True)
    summary = {'fecha_utc': stamp, 'url': BASE, 'total': result.testsRun,
               'fallas': failures, 'errores': errors, 'pruebas': result.records}
    (output / 'resultados.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--salida', type=Path, default=Path('reportes'))
    raise SystemExit(run(parser.parse_args().salida))
