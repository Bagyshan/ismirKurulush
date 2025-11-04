FROM python:3.10

ENV PYTHONIOENCODING UTF-8

# Создаем каталог для статических файлов
RUN mkdir -p /usr/src/app/static

WORKDIR /usr/src/app/

# COPY static/ /usr/src/app/static/
# RUN ls -R /usr/src/app/static/

# Устанавливаем зависимости Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY . .

# Собираем статические файлы Django
RUN python manage.py collectstatic --noinput


EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]