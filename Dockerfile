FROM python:3.13

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Запуск (замените `myproject.wsgi` на ваш путь к WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "cocktails_analytics.wsgi:application"]