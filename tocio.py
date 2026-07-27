import asyncio
import logging
from datetime import datetime
import pytz
import os
import re
from aiogram import Bot, Dispatcher, typesfrom aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from supabase import create_client, Client

API_TOKEN = '8778491120:AAH8i-eqCEu8sD_N3CodImVe2LJxneNvrrs'

# ========== ПРОДАВЦЫ ==========
SELLER_SMIR = 8187401606
SELLER_SAKHAR = 8486571400
SELLER_IDS = [SELLER_SMIR, SELLER_SAKHAR]

# ========== ПОДКЛЮЧЕНИЕ К SUPABASE ==========
SUPABASE_URL = 'https://onngeuzbcjtfswmyukog.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ubmdldXpiY2p0ZnN3bXl1a29nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUxNDQyMTYsImV4cCI6MjEwMDcyMDIxNn0.RPDpxj2z9B9fw2efwYttYuu-SutSFt5p0CFRmCW7znI'

if not SUPABASE_URL or not SUPABASE_KEY:
    logging.error("SUPABASE_URL или SUPABASE_KEY не заданы!")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def is_working_hours() -> bool:
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    return 8 <= now.hour < 22

# ========== ПРОВЕРКА РЕГИОНА ==========
def validate_region(region: str) -> bool:
    region = region.strip()
    if len(region) < 2 or len(region) > 50:
        return False
    if region.isdigit():
        return False
    vowels = 'аеёиоуыэюяaeiou'
    if not any(char in region.lower() for char in vowels):
        return False
    if len(set(region)) < 3:
        return False
    return True

# ========== БАЗА ГОРОДОВ ==========
CITY_DIFFICULTY = {
    'москва': 1, 'санкт-петербург': 1, 'сочи': 1, 'владивосток': 1,
    'екатеринбург': 1, 'новосибирск': 1, 'казань': 1, 'краснодар': 1,
    'нижний новгород': 1, 'челябинск': 1, 'самара': 1, 'омск': 1,
    'ростов-на-дону': 1, 'уфа': 1, 'красноярск': 1, 'пермь': 1,
    'воронеж': 1, 'волгоград': 1, 'тюмень': 1, 'иркутск': 1,
    'хабаровск': 1, 'новокузнецк': 1, 'кемерово': 1, 'томск': 1,
    'ярославль': 2, 'рязань': 2, 'липецк': 2, 'тула': 2,
    'калуга': 2, 'тверь': 2, 'владимир': 2, 'иваново': 2,
    'кострома': 2, 'псков': 2, 'новгород': 2, 'смоленск': 2,
    'брянск': 2, 'курск': 2, 'орёл': 2, 'белгород': 2,
    'тамбов': 2, 'пенза': 2, 'ульяновск': 2, 'саратов': 2,
    'астрахань': 2, 'ижевск': 2, 'киров': 2, 'йошкар-ола': 2,
    'чебоксары': 2, 'саранск': 2, 'владикавказ': 2, 'нальчик': 2,
    'черкесск': 2, 'майкоп': 2, 'ставрополь': 2, 'севастополь': 2,
    'бийск': 3, 'рубцовск': 3, 'барнаул': 3, 'горно-алтайск': 3,
    'абакан': 3, 'минусинск': 3, 'кызыл': 3, 'улан-удэ': 3,
    'чита': 3, 'благовещенск': 3, 'комсомольск-на-амуре': 3,
    'петропавловск-камчатский': 3, 'магадан': 3, 'анадырь': 3,
    'мурманск': 3, 'архангельск': 3, 'петрозаводск': 3,
    'сыктывкар': 3, 'воткинск': 3, 'грозный': 3, 'махачкала': 3,
    'назрань': 3, 'элиста': 3, 'королев': 3, 'мытищи': 3,
    'люберцы': 3, 'подольск': 3, 'дзержинск': 3, 'арзамас': 3,
}

def get_delivery_time(region: str) -> str:
    region_lower = region.lower().strip()
    difficulty = CITY_DIFFICULTY.get(region_lower, 3)
    if difficulty == 1:
        return "1–2 дня"
    elif difficulty == 2:
        return "2–3 дня"
    elif difficulty == 3:
        return "3–5 дней"
    else:
        return "5–7 дней"

# ========== ОСТАЛЬНОЙ КОД ==========
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Магазин'), KeyboardButton(text='Корзина')],
        [KeyboardButton(text='Чат с продавцом'), KeyboardButton(text='Мои заказы')],
    ],
    resize_keyboard=True
)

weapons = {
    'barret_m82': {'name': 'Barret M82', 'price': 3500000, 'stock': 1, 'category': 'Оружие'},
    'm4a1': {'name': 'M4A1', 'price': 1500000, 'stock': 12, 'category': 'Оружие'},
    'svd': {'name': 'CВД', 'price': 1500000, 'stock': 3, 'category': 'Оружие'},
    'ak74': {'name': 'AK-74', 'price': 1500000, 'stock': 32, 'category': 'Оружие'},
    'mp5': {'name': 'MP5', 'price': 800000, 'stock': 15, 'category': 'Оружие'},
    'aks74u': {'name': 'AKC-74У', 'price': 800000, 'stock': 8, 'category': 'Оружие'},
    'pb_silencer': {'name': 'ПБ (c глyшитeлeм)', 'price': 600000, 'stock': 6, 'category': 'Оружие'},
    'remington870': {'name': 'Remington 870', 'price': 500000, 'stock': 10, 'category': 'Оружие'},
    'glock17': {'name': 'Glock-17', 'price': 300000, 'stock': 45, 'category': 'Оружие'},
    'glock18': {'name': 'Glock-18', 'price': 250000, 'stock': 14, 'category': 'Оружие'},
    'kedr': {'name': 'Кeдp (ПП-91)', 'price': 250000, 'stock': 9, 'category': 'Оружие'},
    'tt': {'name': 'ТТ', 'price': 150000, 'stock': 20, 'category': 'Оружие'},
    'pm': {'name': 'ПM', 'price': 80000, 'stock': 50, 'category': 'Оружие'},
    'obrez': {'name': 'Обpeз', 'price': 80000, 'stock': 25, 'category': 'Оружие'},
    'silencer': {'name': 'Глyшитeль 9x19', 'price': 80000, 'stock': 30, 'category': 'Оружие'},
    'grenade': {'name': 'Гpaнaтa Ф-1', 'price': 12500, 'stock': 120, 'category': 'Оружие'},
    'digital_scan': {'name': 'Цифровой скан', 'price': 1500, 'stock': None, 'category': 'Документы'},
    'personal_data': {'name': 'Данные личности', 'price': 7000, 'stock': None, 'category': 'Документы'},
    'drivers_license': {'name': 'Права (пластик)', 'price': 52800, 'stock': None, 'category': 'Документы'},
    'passport_rf': {'name': 'Паспорт РФ', 'price': 178000, 'stock': None, 'category': 'Документы'},
    'foreign_passport_no_chip': {'name': 'Зарубежка (без чипа)', 'price': 350000, 'stock': None, 'category': 'Документы'},
    'foreign_passport_chip': {'name': 'Зарубежка (с чипом)', 'price': 950000, 'stock': None, 'category': 'Документы'},
    'marijuana': {'name': 'Марихуана', 'price': 2000, 'stock': None, 'category': 'Химия'},
    'hashish': {'name': 'Гашиш', 'price': 3000, 'stock': None, 'category': 'Химия'},
    'methamphetamine': {'name': 'Метамфетамин', 'price': 5000, 'stock': None, 'category': 'Химия'},
    'cocaine': {'name': 'Кокаин', 'price': 10000, 'stock': None, 'category': 'Химия'},
    'simple_signs': {'name': 'Простые знаки', 'price': 10000, 'stock': None, 'category': 'Авто-угон'},
    'elite_duplicates': {'name': 'Элитные дубликаты', 'price': 15000, 'stock': None, 'category': 'Авто-угон'},
    'lockpick_kit': {'name': 'Комплект отмычек и сканер', 'price': 35000, 'stock': 15, 'category': 'Авто-угон'},
    'anti_tracker': {'name': 'Программа-антитрекер', 'price': 70000, 'stock': 8, 'category': 'Авто-угон'},
    'burner_phone': {'name': 'Одноразовый телефон (Burner Phone)', 'price': 10000, 'stock': 25, 'category': 'Связь'},
    'jammer': {'name': 'Портативная глушилка сигнала', 'price': 120000, 'stock': 5, 'category': 'Связь'},
    'sportiki': {'name': 'Спортики (Силовой выезд)', 'price': 150000, 'stock': None, 'category': 'Услуги'},
}

user_sessions = {}
user_carts = {}
user_forms = {}

def save_user(user_id: int, username: str = None):
    try:
        supabase.table('users').upsert({'id': user_id, 'username': username}).execute()
    except Exception as e:
        logging.error(f"Ошибка сохранения пользователя: {e}")

def assign_user_to_seller(user_id: int, seller_id: int):
    try:
        supabase.table('clients_sellers').upsert({
            'client_id': user_id,
            'seller_id': seller_id
        }).execute()
        supabase.rpc('increment_clients', {'seller_id': seller_id}).execute()
    except Exception as e:
        logging.error(f"Ошибка назначения продавца: {e}")

def get_worker_percentage(profit: int) -> int:
    if profit < 80000:
        return 70
    elif profit < 200000:
        return 75
    elif profit < 500000:
        return 80
    elif profit < 1000000:
        return 85
    else:
        return 90

def save_order(client_id: int, seller_id: int, items: str, category: str, total: int):
    try:
        stats = get_seller_stats(seller_id)
        current_profit = stats.get('total_profit', 0)
        worker_percent = get_worker_percentage(current_profit)
        creator_percent = 100 - worker_percent
        worker_amount = int(total * worker_percent / 100)
        creator_amount = int(total * creator_percent / 100)
        result = supabase.table('orders').insert({
            'client_id': client_id,
            'seller_id': seller_id,
            'items': items,
            'category': category,
            'total': total,
            'status': 'pending',
            'worker_percent': worker_percent,
            'creator_percent': creator_percent,
            'worker_amount': worker_amount,
            'creator_amount': creator_amount
        }).execute()
        supabase.rpc('increment_orders', {
            'seller_id': seller_id, 
            'profit': total
        }).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]['id']
        return None
    except Exception as e:
        logging.error(f"Ошибка сохранения заказа: {e}")
        return None

def update_order_status(order_id: int, status: str):
    try:
        supabase.table('orders').update({'status': status}).eq('id', order_id).execute()
    except Exception as e:
        logging.error(f"Ошибка обновления статуса заказа: {e}")

def get_seller_stats(seller_id: int):
    try:
        result = supabase.table('seller_stats').select('*').eq('seller_id', seller_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return {'clients_count': 0, 'orders_count': 0, 'total_profit': 0}
    except:
        return {'clients_count': 0, 'orders_count': 0, 'total_profit': 0}

def get_user_orders(user_id: int):
    try:
        result = supabase.table('orders').select('*').eq('client_id', user_id).order('created_at', desc=True).execute()
        return result.data if result.data else []
    except:
        return []

def get_seller_for_user(user_id: int) -> int:
    try:
        result = supabase.table('clients_sellers').select('seller_id').eq('client_id', user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]['seller_id']
        return None
    except:
        return None

def get_shop_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оружие", callback_data="cat_Оружие")],
        [InlineKeyboardButton(text="Документы", callback_data="cat_Документы")],
        [InlineKeyboardButton(text="Химия", callback_data="cat_Химия")],
        [InlineKeyboardButton(text="Авто-угон", callback_data="cat_Авто-угон")],
        [InlineKeyboardButton(text="Связь", callback_data="cat_Связь")],
        [InlineKeyboardButton(text="Услуги", callback_data="cat_Услуги")],
        [InlineKeyboardButton(text="Назад", callback_data="back_main")]
    ])
    return kb

def get_items_kb(category):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    index = 1
    for key, data in weapons.items():
        if data['category'] == category:
            stock_text = "∞" if data['stock'] is None else data['stock']
            price_text = f"{data['price']:,} руб." if data['price'] != 150000 else f"от {data['price']:,} руб."
            kb.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{index}. {data['name']} — {price_text} | Остаток: {stock_text}".replace(',', ' '),
                    callback_data=f"buy_{key}"
                )
            ])
            index += 1
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Назад в категории", callback_data="back_categories")
    ])
    return kb

def get_cart_kb(user_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    cart = user_carts.get(user_id, {})
    if cart:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")
        ])
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Назад в магазин", callback_data="back_categories")
    ])
    return kb

def get_cart_item_kb(key):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="-", callback_data=f"dec_{key}"),
            InlineKeyboardButton(text="+", callback_data=f"inc_{key}")
        ],
        [InlineKeyboardButton(text="Назад в корзину", callback_data="back_to_cart")]
    ])
    return kb

def get_cart_item_text(key: str, user_id: int) -> str:
    cart = user_carts.get(user_id, {})
    if key not in cart:
        return None
    data = cart[key]
    name = weapons[key]['name']
    price = data['price']
    qty = data['qty']
    subtotal = price * qty
    return (
        f"<b>Корзина — {name}</b>\n"
        f"Цена: {price:,} руб.\n"
        f"Количество: {qty}\n"
        f"Сумма: {subtotal:,} руб.\n"
        f"——————————\n"
        f"<i>Используйте кнопки + и - для изменения количества.</i>"
    )

def get_form_template(category: str, items_text: str) -> tuple:
    templates = {
        'Оружие': {
            'text': (
                "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (Оружие)</b>\n"
                "——————————\n"
                f"Товар и количество: {items_text}\n"
                "——————————\n"
                "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
                "<b>Укажите регион / район:</b>"
            ),
            'fields': ['region', 'hideout', 'time', 'payment'],
            'prompts': [
                "<b>Укажите тип тайника:</b>\n<i>Магнит / Тайник в лесу / Прикоп</i>",
                "<b>Укажите удобное время для забора:</b>\n<i>День / Ночь / Не имеет значения</i>",
                "<b>Укажите способ оплаты:</b>\n<i>Крипта / Перевод на карту</i>"
            ]
        },
        'Документы': {
            'text': (
                "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (Документы)</b>\n"
                "——————————\n"
                f"Товар и количество: {items_text}\n"
                "——————————\n"
                "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
                "<b>Укажите регион / район:</b>"
            ),
            'fields': ['region', 'full_name', 'birth_date', 'doc_series', 'payment'],
            'prompts': [
                "<b>Укажите ФИО полностью:</b>",
                "<b>Укажите дату рождения:</b>",
                "<b>Укажите серию и номер документа:</b>",
                "<b>Укажите способ оплаты:</b>\n<i>Крипта / Перевод на карту</i>"
            ]
        },
        'Химия': {
            'text': (
                "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (Химия)</b>\n"
                "——————————\n"
                f"Товар и количество: {items_text}\n"
                "——————————\n"
                "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
                "<b>Укажите регион / район:</b>"
            ),
            'fields': ['region', 'hideout', 'time', 'payment'],
            'prompts': [
                "<b>Укажите тип тайника:</b>\n<i>Магнит / Тайник в лесу / Прикоп</i>",
                "<b>Укажите удобное время для забора:</b>\n<i>День / Ночь / Не имеет значения</i>",
                "<b>Укажите способ оплаты:</b>\n<i>Крипта / Перевод на карту</i>"
            ]
        },
        'Авто-угон': {
            'text': (
                "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (Авто-угон)</b>\n"
                "——————————\n"
                f"Товар и количество: {items_text}\n"
                "——————————\n"
                "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
                "<b>Укажите регион / район:</b>"
            ),
            'fields': ['region', 'car_brand', 'car_year', 'payment'],
            'prompts': [
                "<b>Укажите марку и модель авто:</b>",
                "<b>Укажите год выпуска:</b>",
                "<b>Укажите способ оплаты:</b>\n<i>Крипта / Перевод на карту</i>"
            ]
        },
        'Связь': {
            'text': (
                "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (Связь и спецсредства)</b>\n"
                "——————————\n"
                f"Товар и количество: {items_text}\n"
                "——————————\n"
                "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
                "<b>Укажите регион / район:</b>"
            ),
            'fields': ['region', 'extra', 'payment'],
            'prompts': [
                "<b>Дополнительные пожелания:</b>",
                "<b>Укажите способ оплаты:</b>\n<i>Крипта / Перевод на карту</i>"
            ]
        },
        'Услуги': {
            'text': (
                "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА (Силовой выезд)</b>\n"
                "——————————\n"
                f"Услуга: {items_text}\n"
                "——————————\n"
                "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
                "<b>Укажите регион / район:</b>"
            ),
            'fields': ['region', 'target_name', 'target_address', 'task_desc', 'payment'],
            'prompts': [
                "<b>Укажите ФИО цели:</b>",
                "<b>Укажите адрес цели:</b>",
                "<b>Опишите задачу подробно:</b>",
                "<b>Укажите способ оплаты:</b>\n<i>Крипта / Перевод на карту</i>"
            ]
        }
    }
    template = templates.get(category, templates['Оружие'])
    return template['text'], template['fields'], template['prompts']

@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_carts[user_id] = {}
    save_user(user_id, message.from_user.username)
    if user_id in SELLER_IDS:
        await message.answer(
            "<b>Панель управления.</b>\n"
            "<i>Вы продавец. Используйте магазин для тестов.</i>\n"
            "——————————\n"
            "<b>Правило системы:</b>\n"
            "Процент воркера зависит от профита:\n"
            "• до 80к → 70%\n"
            "• 80–200к → 75%\n"
            "• 200–500к → 80%\n"
            "• 500к–1млн → 85%\n"
            "• от 1млн → 90%\n"
            "<i>Отказ от правил = отключение от системы.</i>\n"
            "——————————\n"
            "<b>Инструкция:</b>\n"
            "При назначении клиента отправьте его юзернейм @SmirAgent и скриншот в ЛС.\n"
            "——————————\n"
            "<b>Команды для админов:</b>\n"
            "/assortiment — полный ассортимент\n"
            "/anketa — анкета для заказа\n"
            "/short — краткий ассортимент\n"
            "——————————\n"
            "<b>Команда для статистики:</b>\n"
            "/stats — ваша статистика (клиенты, заказы, профит)",
            reply_markup=main_kb
        )
        return
    if not is_working_hours():
        await message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        return
    existing_seller = get_seller_for_user(user_id)
    if existing_seller is not None:
        seller_name = "Smir" if existing_seller == SELLER_SMIR else "Сахар"
        await message.answer(
            f"<b>Добро пожаловать.</b>\n"
            f"<i>Ваш продавец — {seller_name}.</i>\n"
            "Выберите действие:",
            reply_markup=main_kb
        )
        return
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    for admin_id in SELLER_IDS:
        try:
            assign_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назначить Smir", callback_data=f"assign_{user_id}_{SELLER_SMIR}")],
                [InlineKeyboardButton(text="Назначить Сахар", callback_data=f"assign_{user_id}_{SELLER_SAKHAR}")]
            ])
            await bot.send_message(
                admin_id,
                f"<b>Новый клиент!</b>\n"
                f"ID: {user_id}\n"
                f"Юзернейм: {username}\n"
                f"Нажмите кнопку, чтобы назначить продавца:",
                reply_markup=assign_kb
            )
        except Exception as e:
            logging.error(f"Ошибка отправки уведомления продавцу {admin_id}: {e}")
    await message.answer(
        "<b>Добро пожаловать.</b>\n"
        "<i>Ваш запрос обрабатывается. Ожидайте подтверждения.</i>"
    )

@dp.message(Command('stats'))
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    if user_id not in SELLER_IDS:
        await message.answer("<i>У вас нет прав для этой команды.</i>")
        return
    stats = get_seller_stats(user_id)
    clients_count = stats.get('clients_count', 0)
    orders_count = stats.get('orders_count', 0)
    total_sum = stats.get('total_profit', 0)
    worker_percent = get_worker_percentage(total_sum)
    creator_percent = 100 - worker_percent
    seller_name = "Smir" if user_id == SELLER_SMIR else "Сахар"
    next_levels = [
        (80000, 75, "80 000"),
        (200000, 80, "200 000"),
        (500000, 85, "500 000"),
        (1000000, 90, "1 000 000")
    ]
    next_text = ""
    for threshold, percent, label in next_levels:
        if total_sum < threshold:
            need = threshold - total_sum
            next_text = f"Следующий уровень: {percent}% при профите {label} руб.\nОсталось заработать: {need:,} руб."
            break
    if not next_text:
        next_text = "Вы достигли максимального уровня (90%)!"
    text = (
        f"<b>Статистика продавца {seller_name}:</b>\n"
        f"——————————\n"
        f"Назначено клиентов: <b>{clients_count}</b>\n"
        f"Заказов выполнено: <b>{orders_count}</b>\n"
        f"Общий профит: <b>{total_sum:,} руб.</b>\n"
        f"——————————\n"
        f"Текущая доля воркера: <b>{worker_percent}%</b>\n"
        f"Ваша доля ({worker_percent}%): <b>{int(total_sum * worker_percent / 100):,} руб.</b>\n"
        f"Доля создателя ({creator_percent}%): <b>{int(total_sum * creator_percent / 100):,} руб.</b>\n"
        f"——————————\n"
        f"{next_text}"
    )
    await message.answer(text)

# ========== КОМАНДЫ ДЛЯ АДМИНОВ ==========
@dp.message(Command('assortiment'))
async def assortiment(message: types.Message):
    user_id = message.from_user.id
    if user_id not in SELLER_IDS:
        await message.answer("<i>У вас нет прав для этой команды.</i>")
        return
    
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>АССОРТИМЕНТ (полный):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>ДОКУМЕНТЫ:</b>\n"
        "• Цифровой скан — 1 500 руб.\n"
        "• Данные личности — 7 000 руб.\n"
        "• Права (пластик) — 52 800 руб.\n"
        "• Паспорт РФ — 178 000 руб.\n"
        "• Зарубежка (без чипа) — 350 000 руб.\n"
        "• Зарубежка (с чипом) — 950 000 руб.\n\n"
        "<b>ЖЕЛЕЗО:</b>\n"
        "• Barret M82 — 3 500 000 руб. (Остаток: 1)\n"
        "• M4A1 — 1 500 000 руб. (Остаток: 12)\n"
        "• СВД — 1 500 000 руб. (Остаток: 3)\n"
        "• АК-74 — 1 500 000 руб. (Остаток: 32)\n"
        "• MP5 — 800 000 руб. (Остаток: 15)\n"
        "• АКС-74У — 800 000 руб. (Остаток: 8)\n"
        "• ПБ (с глушителем) — 600 000 руб. (Остаток: 6)\n"
        "• Remington 870 — 500 000 руб. (Остаток: 10)\n"
        "• Glock-17 — 300 000 руб. (Остаток: 45)\n"
        "• Glock-18 — 250 000 руб. (Остаток: 14)\n"
        "• Кедр (ПП-91) — 250 000 руб. (Остаток: 9)\n"
        "• ТТ — 150 000 руб. (Остаток: 20)\n"
        "• ПМ — 80 000 руб. (Остаток: 50)\n"
        "• Обрез — 80 000 руб. (Остаток: 25)\n"
        "• Глушитель 9х19 — 80 000 руб. (Остаток: 30)\n"
        "• Граната Ф-1 — 12 500 руб. (от 2 ед.) (Остаток: 120)\n\n"
        "<b>ХИМИЯ:</b>\n"
        "• Марихуана — 2 000 руб./г\n"
        "• Гашиш — 3 000 руб./г\n"
        "• Метамфетамин — 5 000 руб./г\n"
        "• Кокаин — 10 000 руб./г\n\n"
        "<b>АВТО-УГОН:</b>\n"
        "• Простые знаки — 10 000 руб.\n"
        "• Элитные дубликаты — 15 000 руб.\n"
        "• Комплект отмычек и сканер — 35 000 руб. (Остаток: 15)\n"
        "• Программа-антитрекер — 70 000 руб. (Остаток: 8)\n\n"
        "<b>СВЯЗЬ И СПЕЦСРЕДСТВА:</b>\n"
        "• Одноразовый телефон (Burner Phone) — 10 000 руб. (Остаток: 25)\n"
        "• Портативная глушилка сигнала — 120 000 руб. (Остаток: 5)\n\n"
        "<b>УСЛУГИ:</b>\n"
        "• Спортики (Силовой выезд) — от 150 000 руб. (за задачу)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Для связи и оформления заказов:</b> @SmirAgent"
    )
    await message.answer(text)

@dp.message(Command('anketa'))
async def anketa(message: types.Message):
    user_id = message.from_user.id
    if user_id not in SELLER_IDS:
        await message.answer("<i>У вас нет прав для этой команды.</i>")
        return
    
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
        "• <b>Товар и количество:</b> (что именно покупаете)\n"
        "• <b>Регион / Район:</b> (укажите удобный район города)\n"
        "• <b>Тип тайника:</b> (Магнит / Тайник в лесу / Прикоп)\n"
        "• <b>Удобное время для забора:</b> (День / Ночь / Не имеет значения)\n"
        "• <b>Способ оплаты:</b> (Крипта / Перевод на карту)"
    )
    await message.answer(text)

@dp.message(Command('short'))
async def short(message: types.Message):
    user_id = message.from_user.id
    if user_id not in SELLER_IDS:
        await message.answer("<i>У вас нет прав для этой команды.</i>")
        return
    
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>КРАТКИЙ АССОРТИМЕНТ:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>ДОКУМЕНТЫ:</b>\n"
        "• Цифровой скан — 1 500 руб.\n"
        "• Данные личности — 7 000 руб.\n"
        "• Права (пластик) — 52 800 руб.\n"
        "• Паспорт РФ — 178 000 руб.\n"
        "• Зарубежка (без чипа) — 350 000 руб.\n"
        "• Зарубежка (с чипом) — 950 000 руб.\n\n"
        "<b>ЖЕЛЕЗО:</b>\n"
        "• Barret M82 — 3 500 000 руб.\n"
        "• M4A1 — 1 500 000 руб.\n"
        "• СВД — 1 500 000 руб.\n"
        "• АК-74 — 1 500 000 руб.\n"
        "• MP5 — 800 000 руб.\n"
        "• АКС-74У — 800 000 руб.\n"
        "• ПБ (с глушителем) — 600 000 руб.\n"
        "• Remington 870 — 500 000 руб.\n"
        "• Glock-17 — 300 000 руб.\n"
        "• Glock-18 — 250 000 руб.\n"
        "• Кедр (ПП-91) — 250 000 руб.\n"
        "• ТТ — 150 000 руб.\n"
        "• ПМ — 80 000 руб.\n"
        "• Обрез — 80 000 руб.\n"
        "• Глушитель 9х19 — 80 000 руб.\n"
        "• Граната Ф-1 — 12 500 руб. (от 2 шт.)\n\n"
        "<b>ХИМИЯ:</b>\n"
        "• Марихуана — 2 000 руб./г\n"
        "• Гашиш — 3 000 руб./г\n"
        "• Метамфетамин — 5 000 руб./г\n"
        "• Кокаин — 10 000 руб./г\n\n"
        "<b>ПЛАСТИНЫ:</b>\n"
        "• Простые знаки — 10 000 руб.\n"
        "• Элитные дубликаты — 15 000 руб."
    )
    await message.answer(text)

@dp.callback_query(lambda cb: cb.data.startswith('assign_'))
async def assign_seller(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    user_id = int(parts[1])
    seller_id = int(parts[2])
    if callback.from_user.id not in SELLER_IDS:
        await callback.answer("У вас нет прав.", show_alert=True)
        return
    assign_user_to_seller(user_id, seller_id)
    seller_name = "Smir" if seller_id == SELLER_SMIR else "Сахар"
    await bot.send_message(
        user_id,
        f"<b>Добро пожаловать.</b>\n"
        f"<i>Ваш продавец — {seller_name}.</i>\n"
        "Выберите действие:",
        reply_markup=main_kb
    )
    try:
        chat = await bot.get_chat(user_id)
        username = f"@{chat.username}" if chat.username else "Нет юзернейма"
    except:
        username = "Неизвестно"
    await bot.send_message(
        seller_id,
        f"<b>Новый клиент назначен вам.</b>\n"
        f"ID: {user_id}\n"
        f"Юзернейм: {username}\n"
        "——————————\n"
        f"Текущая доля: {get_worker_percentage(get_seller_stats(seller_id).get('total_profit', 0))}%.\n"
        "Чем больше заказов, тем выше твой процент."
    )
    await callback.message.edit_text(
        f"✅ Покупатель {user_id} назначен продавцу {seller_name}."
    )
    await callback.answer()

@dp.message(lambda msg: msg.text == 'Магазин')
async def shop(message: types.Message):
    user_id = message.from_user.id
    seller = get_seller_for_user(user_id)
    if seller is None and user_id not in SELLER_IDS:
        await message.answer("<i>Вы ещё не подключены к продавцу. Напишите /start.</i>")
        return
    if user_id not in SELLER_IDS and not is_working_hours():
        await message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        return
    await message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )

@dp.message(lambda msg: msg.text == 'Корзина')
async def view_cart(message: types.Message):
    user_id = message.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        return
    cart = user_carts.get(user_id, {})
    if not cart:
        await message.answer(
            "<b>Корзина пуста.</b>\n"
            "<i>Перейдите в магазин и добавьте товары.</i>"
        )
        return
    text = "<b>Ваша корзина:</b>\n"
    text += "——————————\n"
    total = 0
    for i, (key, data) in enumerate(cart.items(), 1):
        price = data['price']
        qty = data['qty']
        name = weapons[key]['name']
        subtotal = price * qty
        total += subtotal
        text += f"{i}. {name}\n"
        text += f"   Цена: {price:,} руб. x {qty} = {subtotal:,} руб.\n"
    text += "——————————\n"
    text += f"<b>Итого: {total:,} руб.</b>"
    await message.answer(text, reply_markup=get_cart_kb(user_id))

@dp.message(lambda msg: msg.text == 'Чат с продавцом')
async def chat_with_seller(message: types.Message):
    user_id = message.from_user.id
    seller = get_seller_for_user(user_id)
    if seller is None:
        await message.answer("<i>Вы ещё не подключены к продавцу. Напишите /start.</i>")
        return
    if user_id not in SELLER_IDS and not is_working_hours():
        await message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        return
    user_sessions[user_id] = 'chat_mode'
    await message.answer(
        "<b>Вы в чате с продавцом.</b>\n"
        "<i>Напишите сообщение.</i>\n"
        "Для выхода напишите /exit_chat"
    )

@dp.message(lambda msg: msg.text == 'Мои заказы')
async def my_orders(message: types.Message):
    user_id = message.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        return
    orders = get_user_orders(user_id)
    if not orders:
        await message.answer(
            "<b>У вас нет заказов.</b>\n"
            "<i>Перейдите в магазин для оформления.</i>"
        )
        return
    text = "<b>Ваши заказы:</b>\n"
    text += "——————————\n"
    status_map = {
        'pending': '⏳ На рассмотрении',
        'approved': '✅ Подтверждён',
        'rejected': '❌ Отклонён'
    }
    for i, order in enumerate(orders, 1):
        status_text = status_map.get(order['status'], order['status'])
        text += f"{i}. {order['items']} — {order['total']:,} руб. ({status_text})\n"
    text += "——————————"
    await message.answer(text)

@dp.message(lambda msg: msg.text and not msg.text.startswith('/'))
async def handle_user_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    if user_id in SELLER_IDS:
        if user_id in user_sessions and user_sessions[user_id].startswith('reply_to_'):
            buyer_id = int(user_sessions[user_id].replace('reply_to_', ''))
            try:
                await bot.send_message(buyer_id, f"<b>Ответ продавца:</b>\n{text}")
                await message.answer("✅ Сообщение отправлено покупателю.")
                user_sessions[user_id] = 'admin_mode'
            except:
                await message.answer("❌ Ошибка отправки. Возможно, покупатель заблокировал бота.")
            return
        else:
            await message.answer(
                "<i>Вы в режиме админа. Чтобы ответить покупателю — используйте кнопку 'Ответить' под его сообщением.</i>"
            )
            return
    seller = get_seller_for_user(user_id)
    if seller is None:
        await message.answer("<i>Вы ещё не подключены к продавцу. Напишите /start.</i>")
        return
    if not is_working_hours():
        await message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        return
    if user_id in user_sessions and user_sessions[user_id] == 'chat_mode':
        reply_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{user_id}")]
        ])
        await bot.send_message(
            seller,
            f"<b>Сообщение от покупателя</b> (ID: {user_id}):\n{text}\n"
            "——————————\n"
            f"<b>Правило:</b> Твой процент — {get_worker_percentage(get_seller_stats(seller).get('total_profit', 0))}%.",
            reply_markup=reply_kb
        )
        await message.answer("<b>Сообщение отправлено продавцу.</b> Ожидайте ответа.")
        return
    if user_id in user_forms:
        form_data = user_forms[user_id]
        fields = form_data['fields']
        prompts = form_data['prompts']
        step = form_data['step']
        current_field = fields[step]
        form_data[current_field] = text
        form_data['step'] = step + 1
        if form_data['step'] >= len(fields):
            category = form_data['category']
            items_text = form_data['items']
            order_lines = [f"Товар: {items_text}"]
            for field in fields:
                label_map = {
                    'region': 'Регион / Район',
                    'hideout': 'Тип тайника',
                    'time': 'Время забора',
                    'payment': 'Способ оплаты',
                    'full_name': 'ФИО',
                    'birth_date': 'Дата рождения',
                    'doc_series': 'Серия и номер документа',
                    'car_brand': 'Марка и модель авто',
                    'car_year': 'Год выпуска',
                    'extra': 'Дополнительные пожелания',
                    'target_name': 'ФИО цели',
                    'target_address': 'Адрес цели',
                    'task_desc': 'Описание задачи'
                }
                label = label_map.get(field, field)
                order_lines.append(f"{label}: {form_data.get(field, '—')}")
            username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
            order_total = 0
            for key, data in form_data['cart'].items():
                order_total += data['price'] * data['qty']
            delivery_time = get_delivery_time(form_data['region'])
            order_text = (
                f"<b>Новый заказ ({category}):</b>\n"
                f"——————————\n"
                + "\n".join(order_lines) +
                f"\n——————————\n"
                f"Покупатель: {user_id} ({username})\n"
                f"Сумма заказа: <b>{order_total:,} руб.</b>\n"
                f"Примерное время закладки: {delivery_time}\n"
                "——————————\n"
                f"<b>Правило:</b> Твой процент — {get_worker_percentage(get_seller_stats(seller).get('total_profit', 0))}%."
            )
            order_id = save_order(user_id, seller, items_text, category, order_total)
            if order_id:
                confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{order_id}_{user_id}")],
                    [InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_{order_id}_{user_id}")]
                ])
                try:
                    await bot.send_message(seller, order_text, reply_markup=confirm_kb)
                    await message.answer(
                        "<b>Заказ успешно отправлен.</b>\n"
                        "Ожидайте подтверждения."
                    )
                    user_carts[user_id] = {}
                    del user_forms[user_id]
                except:
                    await message.answer("<i>Ошибка отправки заказа. Попробуйте позже.</i>")
            else:
                await message.answer("<i>Ошибка сохранения заказа. Попробуйте позже.</i>")
            return
        next_prompt = prompts[form_data['step'] - 1]
        await message.answer(next_prompt)
        return
    await message.answer(
        "<i>Используйте кнопки меню для навигации.</i>"
    )

@dp.callback_query(lambda cb: cb.data.startswith('approve_') or cb.data.startswith('reject_'))
async def handle_order_decision(callback: types.CallbackQuery):
    action, order_id, client_id = callback.data.split('_')
    order_id = int(order_id)
    client_id = int(client_id)
    seller_id = callback.from_user.id
    if seller_id not in SELLER_IDS:
        await callback.answer("У вас нет прав.", show_alert=True)
        return
    client_seller = get_seller_for_user(client_id)
    if client_seller != seller_id:
        await callback.answer("Это не ваш клиент.", show_alert=True)
        return
    if action == 'approve':
        update_order_status(order_id, 'approved')
        if seller_id == SELLER_SMIR:
            contact = "@SmirAgent"
        else:
            contact = "@nosugarzero"
        await bot.send_message(
            client_id,
            f"<b>✅ Продавец подтвердил вашу анкету!</b>\n"
            f"Свяжитесь с ним для дальнейших инструкций:\n"
            f"{contact}"
        )
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ Заказ подтверждён."
        )
        await callback.answer("Заказ подтверждён.")
    elif action == 'reject':
        update_order_status(order_id, 'rejected')
        await bot.send_message(
            client_id,
            "<b>❌ Ваша анкета отклонена.</b>\n"
            "Вы можете оформить новый заказ через магазин."
        )
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ Заказ отклонён."
        )
        await callback.answer("Заказ отклонён.")

@dp.callback_query(lambda cb: cb.data.startswith('reply_'))
async def reply_to_buyer(callback: types.CallbackQuery):
    buyer_id = int(callback.data.replace('reply_', ''))
    seller_id = callback.from_user.id
    if seller_id not in SELLER_IDS:
        await callback.answer("У вас нет прав.")
        return
    user_sessions[seller_id] = f'reply_to_{buyer_id}'
    await callback.message.answer(
        f"<b>Ответ покупателю (ID: {buyer_id})</b>\n"
        "<i>Напишите текст ответа:</i>"
    )
    await callback.answer()

@dp.message(Command('exit_chat'))
async def exit_chat(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
        await message.answer("<b>Вы вышли из чата.</b>", reply_markup=main_kb)
    else:
        await message.answer("<i>Вы не находитесь в чате.</i>")

@dp.callback_query(lambda cb: cb.data.startswith('cat_'))
async def show_category(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    category = callback.data.replace('cat_', '')
    await callback.message.delete()
    await callback.message.answer(
        f"<b>Категория: {category}</b>",
        reply_markup=get_items_kb(category)
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_categories')
async def back_categories(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    await callback.message.delete()
    await callback.message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data.startswith('buy_'))
async def buy_weapon(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    key = callback.data.replace('buy_', '')
    data = weapons.get(key)
    if not data:
        await callback.answer("Товар не найден")
        return
    name = data['name']
    price = data['price']
    stock = data['stock']
    if stock is not None and stock <= 0:
        await callback.message.delete()
        await callback.message.answer(
            f"<b>{name}</b>\n"
            f"Цена: <b>{price:,}</b> руб.\n"
            f"<i>Статус: нет в наличии</i>"
        )
        await callback.answer()
        return
    action_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_cart_{key}")],
        [InlineKeyboardButton(text="Назад в категории", callback_data="back_categories")]
    ])
    stock_text = "∞" if stock is None else stock
    price_text = f"{price:,} руб." if price != 150000 else f"от {price:,} руб."
    await callback.message.delete()
    await callback.message.answer(
        f"<b>{name}</b>\n"
        f"Цена: <b>{price_text}</b>\n"
        f"Остаток: <b>{stock_text}</b>\n\n"
        f"<i>Выберите действие:</i>",
        reply_markup=action_kb
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data.startswith('add_cart_'))
async def add_to_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    key = callback.data.replace('add_cart_', '')
    data = weapons.get(key)
    if not data:
        await callback.answer("Товар не найден")
        return
    if user_id not in user_carts:
        user_carts[user_id] = {}
    stock = data['stock']
    current_qty = user_carts[user_id].get(key, {}).get('qty', 0)
    if stock is not None and current_qty >= stock:
        await callback.message.delete()
        await callback.message.answer(
            f"<b>Ошибка.</b>\n"
            f"Вы достигли лимита на товар <b>{data['name']}</b>.\n"
            f"Доступно на складе: <b>{stock}</b> шт.\n"
            f"У вас уже добавлено: <b>{current_qty}</b> шт."
        )
        await callback.answer()
        return
    if key in user_carts[user_id]:
        user_carts[user_id][key]['qty'] += 1
    else:
        user_carts[user_id][key] = {'price': data['price'], 'qty': 1}
    text = get_cart_item_text(key, user_id)
    if text:
        await callback.message.edit_text(
            text,
            reply_markup=get_cart_item_kb(key)
        )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data.startswith('inc_') or cb.data.startswith('dec_'))
async def change_cart_quantity(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    action = callback.data[:3]
    key = callback.data[4:]
    cart = user_carts.get(user_id, {})
    if key not in cart:
        await callback.answer("Товар не найден в корзине")
        return
    stock = weapons[key]['stock']
    current_qty = cart[key]['qty']
    if action == 'inc':
        if stock is not None and current_qty >= stock:
            await callback.message.delete()
            await callback.message.answer(
                f"<b>Ошибка.</b>\n"
                f"Вы достигли лимита на товар <b>{weapons[key]['name']}</b>.\n"
                f"Доступно на складе: <b>{stock}</b> шт.\n"
                f"У вас уже добавлено: <b>{current_qty}</b> шт."
            )
            await callback.answer()
            return
        cart[key]['qty'] += 1
    elif action == 'dec':
        if cart[key]['qty'] > 1:
            cart[key]['qty'] -= 1
        else:
            del cart[key]
            await callback.message.edit_text(
                "<b>Товар удалён из корзины.</b>\n"
                "<i>Вы можете вернуться в корзину или продолжить покупки.</i>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Назад в корзину", callback_data="back_to_cart")]
                ])
            )
            await callback.answer()
            return
    text = get_cart_item_text(key, user_id)
    if text:
        await callback.message.edit_text(
            text,
            reply_markup=get_cart_item_kb(key)
        )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_to_cart')
async def back_to_cart_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    await callback.message.delete()
    await view_cart(callback.message)
    await callback.answer()

async def view_cart(message: types.Message):
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    cart = user_carts.get(user_id, {})
    if not cart:
        await message.answer(
            "<b>Корзина пуста.</b>\n"
            "<i>Перейдите в магазин и добавьте товары.</i>"
        )
        return
    text = "<b>Ваша корзина:</b>\n"
    text += "——————————\n"
    total = 0
    for i, (key, data) in enumerate(cart.items(), 1):
        price = data['price']
        qty = data['qty']
        name = weapons[key]['name']
        subtotal = price * qty
        total += subtotal
        text += f"{i}. {name}\n"
        text += f"   Цена: {price:,} руб. x {qty} = {subtotal:,} руб.\n"
    text += "——————————\n"
    text += f"<b>Итого: {total:,} руб.</b>"
    await message.answer(text, reply_markup=get_cart_kb(user_id))

@dp.callback_query(lambda cb: cb.data == 'checkout')
async def checkout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    cart = user_carts.get(user_id, {})
    if not cart:
        await callback.message.answer("<b>Корзина пуста.</b>")
        await callback.answer()
        return
    first_key = list(cart.keys())[0]
    category = weapons[first_key]['category']
    items_list = []
    for key, data in cart.items():
        name = weapons[key]['name']
        qty = data['qty']
        items_list.append(f"{name} x{qty}")
    items_text = ", ".join(items_list)
    form_text, fields, prompts = get_form_template(category, items_text)
    user_forms[user_id] = {
        'items': items_text,
        'category': category,
        'fields': fields,
        'prompts': prompts,
        'step': 0,
        'cart': cart.copy()
    }
    await callback.message.delete()
    await callback.message.answer(form_text)
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'clear_cart')
async def clear_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    user_carts[user_id] = {}
    await callback.message.delete()
    await callback.message.answer("<b>Корзина очищена.</b>")
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_shop')
async def back_shop(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    await callback.message.delete()
    await callback.message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_main')
async def back_main(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in SELLER_IDS and not is_working_hours():
        await callback.message.answer(
            "<b>Бот работает только с 08:00 до 22:00 (МСК).</b>\n"
            "<i>Напишите позже.</i>"
        )
        await callback.answer()
        return
    await callback.message.delete()
    await callback.message.answer("<b>Возврат в главное меню.</b>", reply_markup=main_kb)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
