1) Запуск сервера "flask --app ./acme/api.py run
2) Тестирование API через curl
curl -X POST -d "2024-12-31|Новый Год|Праздничный ужин в 20:00" http://localhost:5000/api/v1/calendar/items

# Попытка создать дубликат (должна вернуть ошибку 409)
curl -X POST -d "2024-12-31|Повтор|Тестовая запись" http://localhost:5000/api/v1/calendar/items

# Некорректный формат даты (ошибка 400)
curl -X POST -d "2024-13-01|Ошибка|Тест" http://localhost:5000/api/v1/calendar/items
3)Установка зависимостей "pip install flask"
