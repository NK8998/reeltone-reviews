FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py migrate.py ./
COPY api ./api
COPY db/migrations ./db/migrations
RUN useradd --uid 1000 --create-home --user-group app

USER app
EXPOSE 8888
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "app:app"]
