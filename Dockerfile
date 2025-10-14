FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd -m myuser
COPY --from=builder /root/.local /home/myuser/.local

COPY . .
ENV PATH=/home/myuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
USER myuser
EXPOSE 8000
CMD ["gunicorn","--bind","0.0.0.0:8000","learnflow_backend.wsgi:application"]
