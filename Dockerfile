# Используем официальный Python-образ
FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем код и зависимости
COPY . /app

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Запускаем бота
CMD ["python", "main.py"]