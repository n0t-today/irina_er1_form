#!/bin/bash

# Скрипт для запуска бота Levi's

echo "🚀 Запуск Telegram бота Levi's..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3."
    exit 1
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка создания виртуального окружения."
        echo "💡 Установите python3-venv: sudo apt install python3-venv"
        exit 1
    fi
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден."
    exit 1
fi

# Устанавливаем зависимости в виртуальном окружении
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Проверяем конфигурацию
if [ ! -f "config.py" ]; then
    echo "⚠️  Файл config.py не найден."
    echo "📝 Скопируйте config_example.py в config.py и заполните настройки."
    echo "cp config_example.py config.py"
    exit 1
fi

# Проверяем наличие ключей Google
if [ ! -f "google_credentials.json" ]; then
    echo "⚠️  Файл google_credentials.json не найден."
    echo "📝 Создайте Service Account в Google Cloud и сохраните ключи."
fi

# Запускаем бота в виртуальном окружении
echo "🤖 Запуск бота..."
python bot.py
 