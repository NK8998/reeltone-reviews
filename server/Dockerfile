FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY api ./api
COPY db/util/create.py /tmp/reviews-schema.py
RUN useradd --uid 1000 --create-home --user-group app \
    && install -d -o app -g app /app/db \
    && cd /app/db \
    && python -c 'import runpy; runpy.run_path("/tmp/reviews-schema.py")["createTables"]()' \
    && chown app:app /app/db/reeltone.db

USER app
EXPOSE 8888
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "app:app"]
