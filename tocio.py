import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '8778491120:AAH8i-eqCEu8sD_N3CodImVe2LJxneNvrrs'

# ========== ПРОДАВЦЫ ==========
SELLER_SMIR = 8187401606     # Смир
SELLER_SAKHAR = 8486571400   # С

SELLER_IDS = [SELLER_SMIR, SELLER_SAKHAR]  # Для проверки

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ========== ГЛАВНОЕ МЕНЮ (БЕЗ ВЫБОРА ПРОДАВЦА) ==========
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мaгaзин'), KeyboardButton(text='Кopзинa')],
        [KeyboardButton(text='Чaт c пpoдaвцoм'), KeyboardButton(text='Moи зaкaзы')],
        [KeyboardButton(text='Koнтaкты')]
    ],
    resize_keyboard=True
)

# ========== ТОВАРЫ (ОБЩИЕ ДЛЯ ВСЕХ) ==========
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

# ========== БАЗЫ ДАННЫХ ==========
user_sessions = {}          # chat_mode
user_orders = {}            # история заказов
user_carts = {}             # корзины
user_forms = {}             # анкеты
user_seller = {}            # { user_id: seller_id } — к кому привязан клиент
pending_assignments = {}    # { admin_id: [user_id, ...] } — ожидают назначения

# ========== КЛАВИАТУРЫ ==========
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

# ========== ФУНКЦИИ ДЛЯ АНКЕТ ==========
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

# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========
@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_carts[user_id] = {}
    
    # Если это администратор (Смир или Сахар) — не перенаправляем
    if user_id in SELLER_IDS:
        await message.answer(
            "<b>Админ-панель.</b>\n"
            "Вы продавец. Используйте магазин для тестов.",
            reply_markup=main_kb
        )
        return
    
    # Отправляем админам уведомление о новом клиенте
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет юзернейма"
    for admin_id in SELLER_IDS:
        try:
            assign_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Назначить Смиру", callback_data=f"assign_{user_id}_{SELLER_SMIR}")],
                [InlineKeyboardButton(text="Назначить Сахару", callback_data=f"assign_{user_id}_{SELLER_SAKHAR}")]
            ])
            await bot.send_message(
                admin_id,
                f"<b>Новый клиент!</b>\n"
                f"ID: {user_id}\n"
                f"Юзернейм: {username}\n"
                f"Нажмите кнопку, чтобы назначить продавца:",
                reply_markup=assign_kb
            )
        except:
            pass
    
    # Временное сообщение клиенту
    await message.answer(
        "<b>Добро пожаловать!</b>\n"
        "<i>Ваш запрос обрабатывается. Ожидайте подтверждения.</i>\n"
        "Обычно это занимает не более минуты."
    )

@dp.callback_query(lambda cb: cb.data.startswith('assign_'))
async def assign_seller(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    user_id = int(parts[1])
    seller_id = int(parts[2])
    
    # Проверяем, что нажал именно администратор
    if callback.from_user.id not in SELLER_IDS:
        await callback.answer("У вас нет прав.", show_alert=True)
        return
    
    # Назначаем продавца
    user_seller[user_id] = seller_id
    
    # Отправляем клиенту приветствие от его продавца
    seller_name = "Смир" if seller_id == SELLER_SMIR else "Сахар"
    await bot.send_message(
        user_id,
        f"<b>Добро пожаловать!</b>\n"
        f"<i>Ваш продавец — {seller_name}.</i>\n"
        "Выберите действие:",
        reply_markup=main_kb
    )
    
    # Уведомляем админа, что назначение выполнено
    await callback.message.edit_text(
        f"✅ Покупатель {user_id} назначен продавцу {seller_name}."
    )
    await callback.answer()

@dp.message(lambda msg: msg.text == 'Мaгaзин')
async def shop(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_seller and user_id not in SELLER_IDS:
        await message.answer("<i>Вы ещё не подключены к продавцу. Напишите /start.</i>")
        return
    await message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )

@dp.message(lambda msg: msg.text == 'Кopзинa')
async def view_cart(message: types.Message):
    user_id = message.from_user.id
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

@dp.message(lambda msg: msg.text == 'Чaт c пpoдaвцoм')
async def chat_with_seller(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_seller:
        await message.answer("<i>Вы ещё не подключены к продавцу. Напишите /start.</i>")
        return
    user_sessions[user_id] = 'chat_mode'
    await message.answer(
        "<b>Вы в чате с продавцом.</b>\n"
        "<i>Напишите сообщение.</i>\n"
        "Для выхода напишите /exit_chat"
    )

@dp.message(lambda msg: msg.text == 'Moи зaкaзы')
async def my_orders(message: types.Message):
    user_id = message.from_user.id
    orders = user_orders.get(user_id, [])
    
    if not orders:
        await message.answer(
            "<b>У вас нет заказов.</b>\n"
            "<i>Перейдите в магазин для оформления.</i>"
        )
        return
    
    text = "<b>Ваши заказы:</b>\n"
    text += "——————————\n"
    for i, order in enumerate(orders, 1):
        text += f"{i}. {order}\n"
    text += "——————————"
    
    await message.answer(text)

@dp.message(lambda msg: msg.text == 'Koнтaкты')
async def contacts(message: types.Message):
    await message.answer(
        "<b>Основной контакт:</b> @SmirAgent"
    )

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@dp.message(lambda msg: msg.text and not msg.text.startswith('/'))
async def handle_user_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Если пользователь — администратор (продавец) — пересылаем сообщение его клиенту
    if user_id in SELLER_IDS:
        # Проверяем, есть ли у него активный режим ответа
        if user_id in user_sessions and user_sessions[user_id].startswith('reply_to_'):
            buyer_id = int(user_sessions[user_id].replace('reply_to_', ''))
            try:
                await bot.send_message(buyer_id, f"<b>Ответ продавца:</b>\n{text}")
                await message.answer("✅ Сообщение отправлено покупателю.")
                # После ответа возвращаемся в обычный режим
                user_sessions[user_id] = 'admin_mode'
            except:
                await message.answer("❌ Ошибка отправки. Возможно, покупатель заблокировал бота.")
            return
        else:
            await message.answer(
                "<i>Вы в режиме админа. Чтобы ответить покупателю — используйте кнопку 'Ответить' под его сообщением.</i>"
            )
            return
    
    # Если пользователь не админ и не привязан к продавцу
    if user_id not in user_seller:
        await message.answer("<i>Вы ещё не подключены к продавцу. Напишите /start.</i>")
        return
    
    # Чат с продавцом (клиент пишет продавцу)
    if user_id in user_sessions and user_sessions[user_id] == 'chat_mode':
        seller_id = user_seller[user_id]
        reply_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{user_id}")]
        ])
        await bot.send_message(
            seller_id,
            f"<b>Сообщение от покупателя</b> (ID: {user_id}):\n{text}",
            reply_markup=reply_kb
        )
        await message.answer("<b>Сообщение отправлено продавцу.</b> Ожидайте ответа.")
        return
    
    # АНКЕТА
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
            
            order_text = (
                f"<b>Новый заказ ({category}):</b>\n"
                f"——————————\n"
                + "\n".join(order_lines) +
                f"\n——————————\n"
                f"Покупатель: {user_id}"
            )
            
            seller_id = user_seller[user_id]
            try:
                await bot.send_message(seller_id, order_text)
                await message.answer(
                    "<b>Заказ успешно отправлен.</b>\n"
                    "Ожидайте подтверждения."
                )
                if user_id not in user_orders:
                    user_orders[user_id] = []
                user_orders[user_id].append(f"{category} — {form_data['items']}")
                user_carts[user_id] = {}
                del user_forms[user_id]
            except:
                await message.answer("<i>Ошибка отправки заказа. Попробуйте позже.</i>")
            return
        
        next_prompt = prompts[form_data['step'] - 1]
        await message.answer(next_prompt)
        return
    
    await message.answer(
        "<i>Используйте кнопки меню для навигации.</i>"
    )

# ========== КОЛБЭКИ ==========
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
    category = callback.data.replace('cat_', '')
    await callback.message.delete()
    await callback.message.answer(
        f"<b>Категория: {category}</b>",
        reply_markup=get_items_kb(category)
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_categories')
async def back_categories(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data.startswith('buy_'))
async def buy_weapon(callback: types.CallbackQuery):
    key = callback.data.replace('buy_', '')
    data = weapons.get(key)
    if not data:
        await callback.answer("Товар не найден")
        return
    
    name = data['name']
    price = data['price']
    stock = data['stock']
    user_id = callback.from_user.id
    
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
    key = callback.data.replace('add_cart_', '')
    data = weapons.get(key)
    if not data:
        await callback.answer("Товар не найден")
        return
    
    user_id = callback.from_user.id
    if user_id not in user_carts:
        user_carts[user_id] = {}
    
    stock = data['stock']
    current_qty = user_carts[user_id].get(key, {}).get('qty', 0)
    
    if stock is not None and current_qty >= stock:
        await callback.message.delete()
        await callback.message.answer(
            f"<b>Ошибка!</b>\n"
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
    action = callback.data[:3]
    key = callback.data[4:]
    user_id = callback.from_user.id
    
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
                f"<b>Ошибка!</b>\n"
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
    user_carts[user_id] = {}
    await callback.message.delete()
    await callback.message.answer("<b>Корзина очищена.</b>")
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_shop')
async def back_shop(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_main')
async def back_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("<b>Возврат в главное меню.</b>", reply_markup=main_kb)
    await callback.answer()

# ========== ЗАПУСК ==========
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
