import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup
import gspread
from google.oauth2.service_account import Credentials

# =====================================================
# НАСТРОЙКИ БОТА
# =====================================================

try:
    from config import *
except ImportError:
    # Если config.py не найден, используем значения по умолчанию
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ADMIN_CHANNEL_ID = "YOUR_ADMIN_CHANNEL_ID"
    GOOGLE_CREDENTIALS_PATH = "google_credentials.json"
    GOOGLE_SHEET_ID = "YOUR_GOOGLE_SHEET_ID"
    DEFAULT_ADMINS = [7533811917]  # Админ по умолчанию
    CONGRATULATIONS_IMAGE_PATH = "congratulations_image.png"

# =====================================================
# СОСТОЯНИЯ FSM
# =====================================================

class RegistrationForm(StatesGroup):
    waiting_for_city = State()
    waiting_for_name = State()
    waiting_for_phone = State()

# =====================================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# =====================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# =====================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С GOOGLE ТАБЛИЦАМИ
# =====================================================

def init_google_sheets():
    """Инициализация подключения к Google Таблицам"""
    try:
        # Определяем область доступа
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Загружаем учетные данные
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=scopes
        )
        
        # Создаем клиент
        client = gspread.authorize(credentials)
        
        # Открываем таблицу
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        
        return sheet
    except Exception as e:
        logging.error(f"Ошибка инициализации Google Sheets: {e}")
        return None

def get_cities_and_addresses():
    """Получение списка городов и адресов из листа 'Города'"""
    try:
        # Определяем область доступа
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Загружаем учетные данные
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=scopes
        )
        
        # Создаем клиент
        client = gspread.authorize(credentials)
        
        # Открываем таблицу и лист "Города"
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        cities_sheet = spreadsheet.worksheet("Города")
        
        # Получаем данные из столбцов A и B начиная со второй строки
        cities_data = cities_sheet.get('A2:B')
        
        # Создаем словарь {город: адрес}
        cities_dict = {}
        cities_list = []
        
        for row in cities_data:
            if row and len(row) >= 1 and row[0].strip():  # Проверяем что город не пустой
                city = row[0].strip()
                address = row[1].strip() if len(row) >= 2 else "Адрес не указан"
                cities_dict[city] = address
                cities_list.append(city)
        
        return cities_list, cities_dict
        
    except Exception as e:
        logging.error(f"Ошибка получения списка городов: {e}")
        return [], {}

def get_spreadsheet_info():
    """Получение информации о всей таблице и всех листах"""
    try:
        # Определяем область доступа
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Загружаем учетные данные
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=scopes
        )
        
        # Создаем клиент
        client = gspread.authorize(credentials)
        
        # Открываем таблицу
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        info = {
            'title': spreadsheet.title,
            'id': spreadsheet.id,
            'url': spreadsheet.url,
            'sheets': []
        }
        
        # Получаем информацию о всех листах
        for sheet in spreadsheet.worksheets():
            sheet_info = {
                'title': sheet.title,
                'id': sheet.id,
                'rows': sheet.row_count,
                'cols': sheet.col_count,
                'is_active': sheet == spreadsheet.sheet1
            }
            info['sheets'].append(sheet_info)
        
        return info
        
    except Exception as e:
        logging.error(f"Ошибка получения информации о таблице: {e}")
        return None

def setup_google_sheet_headers():
    """Настройка заголовков в Google Таблице (можно вызвать отдельно для проверки)"""
    try:
        sheet = init_google_sheets()
        if not sheet:
            return False
        
        # Получаем информацию о листе
        print(f"📋 Название листа: '{sheet.title}'")
        print(f"📊 ID листа: {sheet.id}")
        print(f"📏 Размер листа: {sheet.row_count} строк x {sheet.col_count} столбцов")
        
        all_values = sheet.get_all_values()
        
        # Проверяем наличие правильных заголовков (с городом)
        headers = ['Город', 'Имя', 'Телефон', 'Username', 'User ID', 'Дата']
        
        print(f"\n🔍 Проверка заголовков...")
        print(f"📝 Ожидаемые заголовки: {headers}")
        
        if not all_values:
            print("📄 Таблица пустая")
            print("📝 Создание заголовков...")
            sheet.append_row(headers)
        else:
            print(f"📋 Текущие заголовки: {all_values[0]}")
            
            if all_values[0] != headers:
                print("⚠️ Заголовки не соответствуют ожидаемым")
                print("📝 Создание правильных заголовков...")
                
                # Если есть данные, но нет заголовков - вставляем их в начало
                if all_values:
                    sheet.insert_row(headers, 1)
                    print("✅ Заголовки вставлены в первую строку")
                else:
                    sheet.append_row(headers)
                    print("✅ Заголовки добавлены в пустую таблицу")
            else:
                print("✅ Заголовки уже существуют и корректны")
        
        # Форматируем заголовки
        try:
            sheet.format('A1:F1', {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                "horizontalAlignment": "CENTER"
            })
            print("🎨 Заголовки отформатированы")
        except Exception as format_error:
            print(f"⚠️ Заголовки созданы, но форматирование не удалось: {format_error}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка настройки заголовков: {e}")
        return False

async def save_to_google_sheets(name: str, phone: str, username: str, user_id: int, city: str):
    """Сохранение данных в Google Таблицы"""
    try:
        sheet = init_google_sheets()
        if sheet:
            # Проверяем наличие заголовков и создаем их если нужно
            all_values = sheet.get_all_values()
            
            # Обновленные заголовки с городом
            headers = ['Город', 'Имя', 'Телефон', 'Username', 'User ID', 'Дата']
            
            # Если таблица пустая или первая строка не содержит заголовки
            if not all_values or (all_values and all_values[0] != headers):
                logging.info("Создание заголовков в Google Таблице...")
                
                # Если есть данные, но нет заголовков - вставляем их в начало
                if all_values:
                    sheet.insert_row(headers, 1)
                else:
                    # Если таблица пустая - просто добавляем заголовки
                    sheet.append_row(headers)
                
                # Форматируем заголовки (делаем жирными)
                try:
                    sheet.format('A1:F1', {
                        "textFormat": {
                            "bold": True
                        },
                        "backgroundColor": {
                            "red": 0.9,
                            "green": 0.9,
                            "blue": 0.9
                        }
                    })
                except Exception as format_error:
                    logging.warning(f"Не удалось отформатировать заголовки: {format_error}")
            
            # Добавляем новую строку с данными
            from datetime import datetime
            current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
            sheet.append_row([city, name, phone, username or "Не указан", user_id, current_date])
            
            logging.info(f"Данные сохранены в Google Таблицы: {city}, {name}, {phone}")
            return True
    except Exception as e:
        logging.error(f"Ошибка сохранения в Google Sheets: {e}")
        return False

# =====================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С АДМИНАМИ
# =====================================================

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id in DEFAULT_ADMINS

async def notify_admins(text: str):
    """Уведомление всех админов"""
    for admin_id in DEFAULT_ADMINS:
        try:
            await bot.send_message(chat_id=admin_id, text=text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")

# =====================================================
# ОБРАБОТЧИКИ КОМАНД И СООБЩЕНИЙ
# =====================================================

# Словарь для отслеживания пользователей, которые уже получили приветствие
welcomed_users = set()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()
    
    welcome_text = (
        """🎉 <b>Добро пожаловать!</b>

Для участия <b>в программе лояльности Levi's</b> нам необходимо узнать некоторую информацию о вас.

📍 <b>Для начала выберите ваш город:</b>"""
    )
    
    # Получаем список городов
    cities_list, cities_dict = get_cities_and_addresses()
    
    if not cities_list:
        await message.answer(
            "❌ <b>Ошибка загрузки списка городов.</b>\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.",
            parse_mode="HTML"
        )
        return
    
    # Создаем инлайн клавиатуру с городами (по 2 кнопки в ряду)
    keyboard_buttons = []
    row = []
    for i, city in enumerate(cities_list):
        row.append(InlineKeyboardButton(text=city, callback_data=f"city:{city}"))
        if len(row) == 2 or i == len(cities_list) - 1:
            keyboard_buttons.append(row)
            row = []
    
    city_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(welcome_text, reply_markup=city_keyboard, parse_mode="HTML")
    await state.set_state(RegistrationForm.waiting_for_city)

# =====================================================
# ОБРАБОТЧИК ВЫБОРА ГОРОДА
# =====================================================

@dp.callback_query(F.data.startswith("city:"), StateFilter(RegistrationForm.waiting_for_city))
async def process_city_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора города через инлайн кнопку"""
    await callback.answer()
    
    # Извлекаем название города из callback_data
    selected_city = callback.data.split(":", 1)[1]
    
    # Получаем актуальный список городов и адресов
    cities_list, cities_dict = get_cities_and_addresses()
    
    # Проверяем, что город есть в списке
    if selected_city not in cities_dict:
        await callback.message.answer(
            "❌ <b>Ошибка выбора города. Попробуйте снова.</b>",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем город и адрес в состоянии
    await state.update_data(city=selected_city, address=cities_dict[selected_city])
    
    # Редактируем сообщение и переходим к запросу имени
    await callback.message.edit_text(
        f"✅ <b>Отлично! Город: {selected_city}</b>\n\n"
        "📝 <b>Теперь введите ваше имя:</b>",
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationForm.waiting_for_name)

# =====================================================
# ОБРАБОТЧИК ВВОДА ИМЕНИ
# =====================================================

@dp.message(StateFilter(RegistrationForm.waiting_for_name))
async def process_name(message: types.Message, state: FSMContext):
    """Обработка ввода имени"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer(
            """❌ <b>Имя слишком короткое.</b>

Пожалуйста, введите корректное имя:""",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем имя в состоянии
    await state.update_data(name=name)
    
    # Создаем клавиатуру для запроса контакта
    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"✅ <b>Отлично, {name}!</b>\n\n"
        "📞 <b>Теперь нам нужен Ваш номер телефона.</b>\n"
        "Вы можете поделиться им автоматически или ввести вручную:",
        reply_markup=contact_keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationForm.waiting_for_phone)

@dp.message(StateFilter(RegistrationForm.waiting_for_phone), F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    """Обработка автоматического получения контакта"""
    phone = message.contact.phone_number
    await process_phone_data(message, state, phone)

@dp.message(StateFilter(RegistrationForm.waiting_for_phone), F.text)
async def process_phone_text(message: types.Message, state: FSMContext):
    """Обработка ручного ввода телефона"""
    phone = message.text.strip()
    
    # Простая валидация номера телефона
    import re
    phone_pattern = r'^[\+]?[0-9\s\-\(\)]{10,15}$'
    
    if not re.match(phone_pattern, phone):
        await message.answer(
            "❌ <b>Некорректный номер телефона.</b>\n"
            "Пожалуйста, введите номер в формате:\n"
            "• +7 (xxx) xxx-xx-xx\n"
            "• 8xxxxxxxxxx\n"
            "• или воспользуйтесь кнопкой выше",
            parse_mode="HTML"
        )
        return
    
    await process_phone_data(message, state, phone)

async def process_phone_data(message: types.Message, state: FSMContext, phone: str):
    """Обработка полученного номера телефона"""
    # Получаем сохраненные данные
    data = await state.get_data()
    name = data.get('name')
    city = data.get('city', 'Не указан')
    address = data.get('address', 'Не указан')
    
    # Очищаем состояние
    await state.clear()
    
    # Убираем клавиатуру
    await message.answer(
        "⏳ <b>Обрабатываем ваши данные...</b>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    
    # Отправляем заявку в канал админов
    await send_to_admin_channel(message.from_user, name, phone, city)
    
    # Сохраняем в Google Таблицы
    await save_to_google_sheets(
        name=name,
        phone=phone,
        username=message.from_user.username,
        user_id=message.from_user.id,
        city=city
    )
    
    # Отправляем поздравительное сообщение с изображением
    await send_congratulations(message, name, address)

async def send_to_admin_channel(user: types.User, name: str, phone: str, city: str):
    """Отправка заявки в канал админов"""
    try:
        admin_message = (
            "🆕 <b>НОВАЯ ЗАЯВКА</b>\n\n"
            f"📍 <b>Город:</b> {city}\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"📱 <b>Username:</b> @{user.username or 'Не указан'}\n"
            f"🔗 <b>Ссылка:</b> <a href='tg://user?id={user.id}'>Профиль</a>\n\n"
            f"📅 <b>Дата:</b> {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        await bot.send_message(
            chat_id=ADMIN_CHANNEL_ID,
            text=admin_message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
        logging.info(f"Заявка отправлена в админ канал: {name}, {phone}, {city}")
        
    except Exception as e:
        logging.error(f"Ошибка отправки в админ канал: {e}")

async def send_congratulations(message: types.Message, name: str, address: str):
    """Отправка поздравительного сообщения с изображением"""
    try:
        congratulations_text = (
            f"""🎉 <b>Поздравляем, {name}!</b>

Вы стали участником программы лояльности Levi's. Теперь Вам доступны скидки и привилегии как держателю карты. 

🛍️ <b>Ждём вас за покупками!</b>
📍 <b>{address}</b>"""
        )
        
        # Путь к изображению
        image_path = "image.png"
        
        try:
            # Отправляем изображение с подписью
            with open(image_path, 'rb') as file:
                photo = BufferedInputFile(file.read(), filename="congratulations.jpg")
                await message.answer_photo(
                    photo=photo,
                    caption=congratulations_text,
                    parse_mode="HTML"
                )
        except FileNotFoundError:
            # Если изображение не найдено, отправляем только текст
            await message.answer(
                congratulations_text,
                parse_mode="HTML"
            )
            logging.warning("Изображение для поздравления не найдено")
        
    except Exception as e:
        logging.error(f"Ошибка отправки поздравления: {e}")
        await message.answer(
            "✅ <b>Регистрация завершена!</b>\n"
            "Спасибо за участие!",
            parse_mode="HTML"
        )

# =====================================================
# КОМАНДЫ ДЛЯ АДМИНОВ
# =====================================================

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Админ панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ <b>У вас нет прав администратора.</b>", parse_mode="HTML")
        return
    
    admin_text = (
        "👨‍💼 <b>АДМИН ПАНЕЛЬ</b>\n\n"
        "📊 <b>Доступные команды:</b>\n"
        "• /stats - Статистика заявок\n"
        "• /setup_sheet - Настройка Google Таблицы\n"
        "• /table_info - Полная информация о таблице\n"
        "• /broadcast - Рассылка пользователям\n\n"
        f"🆔 <b>Ваш ID:</b> <code>{message.from_user.id}</code>\n"
        f"📅 <b>Дата:</b> {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    await message.answer(admin_text, parse_mode="HTML")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Статистика для админов"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ <b>У вас нет прав администратора.</b>", parse_mode="HTML")
        return
    
    try:
        sheet = init_google_sheets()
        if sheet:
            total_records = len(sheet.get_all_records())
            today = __import__('datetime').datetime.now().strftime('%d.%m.%Y')
            
            # Подсчет заявок за сегодня (упрощенный вариант)
            today_count = 0
            try:
                all_data = sheet.get_all_values()
                for row in all_data[1:]:  # Пропускаем заголовок
                    if len(row) >= 5 and today in row[4]:  # Проверяем дату
                        today_count += 1
            except:
                today_count = "н/д"
            
            stats_text = (
                "📊 <b>СТАТИСТИКА ЗАЯВОК</b>\n\n"
                f"📈 <b>Всего заявок:</b> {total_records}\n"
                f"📅 <b>За сегодня:</b> {today_count}\n"
                f"🕐 <b>Обновлено:</b> {__import__('datetime').datetime.now().strftime('%H:%M')}"
            )
        else:
            stats_text = "❌ <b>Ошибка подключения к Google Таблицам</b>"
            
    except Exception as e:
        stats_text = f"❌ <b>Ошибка получения статистики:</b> {str(e)}"
        logging.error(f"Ошибка получения статистики: {e}")
    
    await message.answer(stats_text, parse_mode="HTML")

@dp.message(Command("setup_sheet"))
async def cmd_setup_sheet(message: types.Message):
    """Настройка заголовков в Google Таблице"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ <b>У вас нет прав администратора.</b>", parse_mode="HTML")
        return
    
    await message.answer("🔧 <b>Проверка и настройка Google Таблицы...</b>", parse_mode="HTML")
    
    try:
        # Получаем информацию о таблице
        sheet = init_google_sheets()
        if not sheet:
            await message.answer(
                "❌ <b>Ошибка подключения к Google Таблице</b>\n\n"
                "Проверьте:\n"
                "• Файл google_credentials.json\n"
                "• ID таблицы в config.py\n"
                "• Права доступа Service Account",
                parse_mode="HTML"
            )
            return
        
        # Получаем информацию о листе
        sheet_info = (
            f"📋 <b>Информация о листе:</b>\n"
            f"• Название: <code>{sheet.title}</code>\n"
            f"• ID: <code>{sheet.id}</code>\n"
            f"• Размер: {sheet.row_count} строк x {sheet.col_count} столбцов\n\n"
        )
        
        # Проверяем заголовки
        all_values = sheet.get_all_values()
        headers = ['Город', 'Имя', 'Телефон', 'Username', 'User ID', 'Дата']
        
        if not all_values:
            headers_info = "📄 <b>Таблица пустая</b> - заголовки будут созданы"
        else:
            current_headers = all_values[0]
            if current_headers == headers:
                headers_info = "✅ <b>Заголовки корректны:</b>\n" + "\n".join([f"• {h}" for h in current_headers])
            else:
                headers_info = (
                    f"⚠️ <b>Заголовки не соответствуют:</b>\n"
                    f"Текущие: <code>{current_headers}</code>\n"
                    f"Ожидаемые: <code>{headers}</code>\n\n"
                    f"Будут созданы правильные заголовки"
                )
        
        # Настраиваем заголовки
        if setup_google_sheet_headers():
            await message.answer(
                f"{sheet_info}"
                f"{headers_info}\n\n"
                f"✅ <b>Google Таблица настроена!</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"{sheet_info}"
                f"❌ <b>Ошибка настройки заголовков</b>",
                parse_mode="HTML"
            )
            
    except Exception as e:
        await message.answer(f"❌ <b>Ошибка:</b> {str(e)}", parse_mode="HTML")
        logging.error(f"Ошибка настройки таблицы: {e}")

@dp.message(Command("table_info"))
async def cmd_table_info(message: types.Message):
    """Полная информация о Google Таблице"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ <b>У вас нет прав администратора.</b>", parse_mode="HTML")
        return
    
    await message.answer("📊 <b>Получение информации о Google Таблице...</b>", parse_mode="HTML")
    
    try:
        info = get_spreadsheet_info()
        if not info:
            await message.answer(
                "❌ <b>Ошибка получения информации о таблице</b>\n\n"
                "Проверьте настройки подключения",
                parse_mode="HTML"
            )
            return
        
        # Формируем информацию о таблице
        table_info = (
            f"📊 <b>ИНФОРМАЦИЯ О ТАБЛИЦЕ</b>\n\n"
            f"📋 <b>Название:</b> {info['title']}\n"
            f"🆔 <b>ID:</b> <code>{info['id']}</code>\n"
            f"🔗 <b>URL:</b> <a href='{info['url']}'>Открыть таблицу</a>\n\n"
            f"📄 <b>Листы ({len(info['sheets'])}):</b>\n"
        )
        
        # Добавляем информацию о каждом листе
        for i, sheet in enumerate(info['sheets'], 1):
            status = "🟢 Активный" if sheet['is_active'] else "⚪ Неактивный"
            table_info += (
                f"{i}. <b>{sheet['title']}</b> {status}\n"
                f"   • ID: <code>{sheet['id']}</code>\n"
                f"   • Размер: {sheet['rows']} x {sheet['cols']}\n\n"
            )
        
        await message.answer(table_info, parse_mode="HTML", disable_web_page_preview=True)
        
    except Exception as e:
        await message.answer(f"❌ <b>Ошибка:</b> {str(e)}", parse_mode="HTML")
        logging.error(f"Ошибка получения информации о таблице: {e}")

# =====================================================
# ОБРАБОТЧИК НЕИЗВЕСТНЫХ КОМАНД
# =====================================================

@dp.message()
async def unknown_message(message: types.Message):
    """Обработка неизвестных сообщений"""
    user_id = message.from_user.id
    
    # Если пользователь пишет впервые, отправляем приветственное сообщение
    if user_id not in welcomed_users:
        welcomed_users.add(user_id)
        
        # Создаем кнопку СТАРТ
        start_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="СТАРТ", callback_data="start_registration")]
            ]
        )
        
        welcome_text = (
            """Привет! Это бот фирменного магазина Levi's ❤️

Для того, чтобы оставить свой контакт, нажми кнопку «СТАРТ»

Нажимая кнопку «СТАРТ» ты подтверждаешь, что даешь согласие на обработку персональных данных (http://tula.leviru.com/agreement)."""
        )
        
        await message.answer(welcome_text, reply_markup=start_keyboard)
    else:
        await message.answer(
            "❓ <b>Не понимаю эту команду.</b>\n"
            "Используйте /start для начала регистрации.",
            parse_mode="HTML"
        )

@dp.callback_query(F.data == "start_registration")
async def callback_start_registration(callback: types.CallbackQuery, state: FSMContext):
    """Обработка нажатия кнопки СТАРТ"""
    await callback.answer()
    await state.clear()
    
    welcome_text = (
        """🎉 <b>Добро пожаловать!</b>

Для участия <b>в программе лояльности Levi's</b> нам необходимо узнать некоторую информацию о вас.

📍 <b>Для начала выберите ваш город:</b>"""
    )
    
    # Получаем список городов
    cities_list, cities_dict = get_cities_and_addresses()
    
    if not cities_list:
        await callback.message.edit_text(
            "❌ <b>Ошибка загрузки списка городов.</b>\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.",
            parse_mode="HTML"
        )
        return
    
    # Создаем инлайн клавиатуру с городами (по 2 кнопки в ряду)
    keyboard_buttons = []
    row = []
    for i, city in enumerate(cities_list):
        row.append(InlineKeyboardButton(text=city, callback_data=f"city:{city}"))
        if len(row) == 2 or i == len(cities_list) - 1:
            keyboard_buttons.append(row)
            row = []
    
    city_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Редактируем сообщение с инлайн клавиатурой
    await callback.message.edit_text(welcome_text, reply_markup=city_keyboard, parse_mode="HTML")
    await state.set_state(RegistrationForm.waiting_for_city)

# =====================================================
# ЗАПУСК БОТА
# =====================================================

async def main():
    """Основная функция запуска бота"""
    logging.info("Запуск бота...")
    
    # Удаляем webhook если есть
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
