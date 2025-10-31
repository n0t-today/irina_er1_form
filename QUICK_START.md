# 🚀 Быстрый старт Levi's Bot

## 1️⃣ Быстрая настройка (5 минут)

### Шаг 1: Настройка виртуального окружения
```bash
./setup_venv.sh
```

### Шаг 2: Копируйте конфигурацию
```bash
cp config_example.py config.py
```

### Шаг 3: Отредактируйте config.py
```python
# Основные настройки
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # От @BotFather
ADMIN_CHANNEL_ID = "-1001234567890"  # ID канала админов
GOOGLE_SHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
```

### Шаг 3: Добавьте google_credentials.json
1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API
3. Создайте Service Account
4. Скачайте JSON ключ как `google_credentials.json`

### Шаг 4: Добавьте изображение
```bash
# Поместите изображение для поздравления
cp your_image.png congratulations_image.png
```

## 2️⃣ Запуск

### Автоматический запуск:
```bash
./start_bot.sh
```

### Ручной запуск:
```bash
pip3 install -r requirements.txt
python3 bot.py
```

## 3️⃣ Проверка работы

### Тестирование Google Таблиц:
```bash
python3 test_sheets.py
```

### Проверка бота:
1. Найдите бота в Telegram
2. Отправьте `/start`
3. Проверьте админ команды: `/admin`, `/stats`, `/setup_sheet`

## 4️⃣ Что получится

- ✅ Пользователь вводит имя и телефон
- ✅ Получает поздравление с картинкой
- ✅ Данные сохраняются в Google Таблицы
- ✅ Админы получают уведомления

## 🔧 Админ команды

- `/admin` - Панель администратора
- `/stats` - Статистика заявок  
- `/setup_sheet` - Настройка заголовков Google Таблицы
- `/table_info` - Полная информация о таблице и листах

---

**Админ по умолчанию:** 7533811917  
**Поддержка:** excelrnpwz@gmail.com
