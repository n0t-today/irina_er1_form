#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Google Таблицам
Запустите этот скрипт для проверки настроек
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bot import setup_google_sheet_headers, init_google_sheets, get_spreadsheet_info
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("💡 Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
    sys.exit(1)

def test_google_sheets():
    """Тестирование подключения к Google Таблицам"""
    print("🧪 Тестирование подключения к Google Таблицам...\n")
    
    # Тест 1: Проверка подключения
    print("1️⃣ Проверка подключения...")
    sheet = init_google_sheets()
    if sheet:
        print("✅ Подключение к Google Таблицам установлено")
        print(f"📋 Название листа: '{sheet.title}'")
        print(f"🆔 ID листа: {sheet.id}")
        print(f"📏 Размер листа: {sheet.row_count} строк x {sheet.col_count} столбцов")
    else:
        print("❌ Не удалось подключиться к Google Таблицам")
        print("\n🔧 Проверьте:")
        print("• Файл google_credentials.json существует")
        print("• ID таблицы в config.py корректный")
        print("• Service Account имеет доступ к таблице")
        return False
    
    # Тест 1.5: Полная информация о таблице
    print("\n1️⃣.5️⃣ Полная информация о таблице...")
    info = get_spreadsheet_info()
    if info:
        print(f"📊 Название таблицы: '{info['title']}'")
        print(f"🆔 ID таблицы: {info['id']}")
        print(f"🔗 URL: {info['url']}")
        print(f"📄 Количество листов: {len(info['sheets'])}")
        
        for i, sheet_info in enumerate(info['sheets'], 1):
            status = "🟢 Активный" if sheet_info['is_active'] else "⚪ Неактивный"
            print(f"  {i}. {sheet_info['title']} {status} (ID: {sheet_info['id']}, {sheet_info['rows']}x{sheet_info['cols']})")
    else:
        print("⚠️ Не удалось получить полную информацию о таблице")
    
    # Тест 2: Проверка заголовков
    print("\n2️⃣ Проверка и настройка заголовков...")
    if setup_google_sheet_headers():
        print("✅ Заголовки настроены корректно")
    else:
        print("❌ Ошибка настройки заголовков")
        return False
    
    # Тест 3: Проверка содержимого
    print("\n3️⃣ Информация о таблице...")
    try:
        all_values = sheet.get_all_values()
        if all_values:
            print(f"📊 Всего строк: {len(all_values)}")
            print(f"📋 Заголовки: {all_values[0] if all_values else 'Отсутствуют'}")
            if len(all_values) > 1:
                print(f"📈 Записей с данными: {len(all_values) - 1}")
            else:
                print("📝 Записей с данными: 0")
        else:
            print("📄 Таблица пустая")
    except Exception as e:
        print(f"❌ Ошибка чтения таблицы: {e}")
        return False
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("💡 Google Таблицы готовы к работе с ботом")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🔬 ТЕСТИРОВАНИЕ GOOGLE ТАБЛИЦ")
    print("=" * 50)
    
    success = test_google_sheets()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("🚀 Можете запускать бота: ./start_bot.sh")
    else:
        print("❌ ТЕСТИРОВАНИЕ НЕУСПЕШНО")
        print("🔧 Исправьте ошибки и запустите тест снова")
    print("=" * 50)
