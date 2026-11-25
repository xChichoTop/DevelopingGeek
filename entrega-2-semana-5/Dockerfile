FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home estudiante
COPY app.py ./
COPY templates ./templates
COPY ci/pruebas_ci.py ci/persistencia.py ./ci/
USER estudiante
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
