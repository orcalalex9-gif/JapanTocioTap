import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '8778491120:AAH8i-eqCEu8sD_N3CodImVe2LJxneNvrrs'
SELLER_ID = 8187401606

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ========== ГЛАВНОЕ МЕНЮ ==========
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мaгaзин'), KeyboardButton(text='Кopзинa')],
        [KeyboardButton(text='Чaт c пpoдaвцoм'), KeyboardButton(text='Moи зaкaзы')],
        [KeyboardButton(text='Koнтaкты')]
    ],
    resize_keyboard=True
)

# ========== ТОВАРЫ ==========
weapons = {
    'barret_m83': {'name': 'Barret M83', 'price': 3500000, 'stock': 1, 'category': 'Оружие'},
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
    'tt': {'name': 'TT', 'price': 150000, 'stock': 20, 'category': 'Оружие'},
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
}

# ========== БАЗЫ ДАННЫХ ==========
user_sessions = {}
user_orders = {}
user_carts = {}
# Храним состояние анкеты для каждого пользователя
user_forms = {}

# ========== КЛАВИАТУРЫ ==========
def get_shop_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оружие", callback_data="cat_Оружие")],
        [InlineKeyboardButton(text="Документы", callback_data="cat_Документы")],
        [InlineKeyboardButton(text="Назад", callback_data="back_main")]
    ])
    return kb

def get_items_kb(category):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    index = 1
    for key, data in weapons.items():
        if data['category'] == category:
            stock_text = "∞" if data['stock'] is None else data['stock']
            kb.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{index}. {data['name']} — {data['price']:,} руб. | Остаток: {stock_text}".replace(',', ' '),
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

# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========
@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_carts[user_id] = {}
    await message.answer(
        "<b>Добро пожаловать.</b>\n"
        "<i>Здесь можно заказать вооружение и документы.</i>\n"
        "Выберите действие:",
        reply_markup=main_kb
    )

@dp.message(lambda msg: msg.text == 'Мaгaзин')
async def shop(message: types.Message):
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
    user_sessions[user_id] = 'chat_mode'
    await message.answer(
        "<b>Вы в чате с продавцом.</b>\n"
        "<i>Напишите сообщение или вставьте готовый текст заказа.</i>\n"
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
        "<b>Основной контакт:</b> @SmirAgent\n"
        "<b>Запасной:</b> @smirspambot"
    )

@dp.message(lambda msg: msg.text and not msg.text.startswith('/'))
async def handle_user_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Если пользователь в режиме заполнения анкеты
    if user_id in user_forms:
        form_data = user_forms[user_id]
        # Проверяем, какой шаг анкеты
        if 'region' not in form_data:
            form_data['region'] = text
            await message.answer(
                "<b>Укажите тип тайника:</b>\n"
                "<i>Магнит / Тайник в лесу / Прикоп</i>"
            )
            return
        elif 'hideout' not in form_data:
            form_data['hideout'] = text
            await message.answer(
                "<b>Укажите удобное время для забора:</b>\n"
                "<i>День / Ночь / Не имеет значения</i>"
            )
            return
        elif 'time' not in form_data:
            form_data['time'] = text
            await message.answer(
                "<b>Укажите способ оплаты:</b>\n"
                "<i>Крипта / Перевод на карту</i>"
            )
            return
        elif 'payment' not in form_data:
            form_data['payment'] = text
            
            # Анкета заполнена — отправляем продавцу
            username = message.from_user.username if message.from_user.username else "Нет"
            order_text = (
                f"<b>Новый заказ (анкета):</b>\n"
                f"——————————\n"
                f"Товар: {form_data['items']}\n"
                f"Регион / Район: {form_data['region']}\n"
                f"Тип тайника: {form_data['hideout']}\n"
                f"Время забора: {form_data['time']}\n"
                f"Способ оплаты: {form_data['payment']}\n"
                f"——————————\n"
                f"Покупатель: {user_id} (@{username})"
            )
            
            try:
                await bot.send_message(SELLER_ID, order_text)
                await message.answer(
                    "<b>Заказ успешно отправлен.</b>\n"
                    "Ожидайте подтверждения в чате с продавцом.\n"
                    "Для связи используйте 'Чат с продавцом'."
                )
                # Сохраняем в историю
                if user_id not in user_orders:
                    user_orders[user_id] = []
                user_orders[user_id].append(f"Анкета — {form_data['items']}")
                # Очищаем корзину
                user_carts[user_id] = {}
                # Удаляем состояние анкеты
                del user_forms[user_id]
            except Exception as e:
                await message.answer("<i>Ошибка отправки заказа. Попробуйте позже.</i>")
            return
    
    # Обычный режим чата с продавцом
    if user_id in user_sessions and user_sessions[user_id] == 'chat_mode':
        try:
            await bot.send_message(
                SELLER_ID,
                f"<b>Сообщение от покупателя</b> (ID: {user_id}, Юзepнeйм: @{message.from_user.username if message.from_user.username else 'Нет'}):\n{text}"
            )
            await message.answer("<b>Сообщение отправлено продавцу.</b> Ожидайте ответа.")
        except Exception as e:
            await message.answer("<i>Ошибка отправки. Продавец недоступен.</i>")

@dp.message(Command('exit_chat'))
async def exit_chat(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
        await message.answer("<b>Вы вышли из чата с продавцом.</b>", reply_markup=main_kb)
    else:
        await message.answer("<i>Вы не находитесь в чате.</i>")

# ========== КОЛБЭКИ ==========
@dp.callback_query(lambda cb: cb.data.startswith('cat_'))
async def show_category(callback: types.CallbackQuery):
    category = callback.data.replace('cat_', '')
    await callback.message.answer(
        f"<b>Категория: {category}</b>",
        reply_markup=get_items_kb(category)
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_categories')
async def back_categories(callback: types.CallbackQuery):
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
    
    stock_text = "∞ (неограничено)" if stock is None else stock
    
    await callback.message.answer(
        f"<b>{name}</b>\n"
        f"Цена: <b>{price:,}</b> руб.\n"
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
    
    if key in user_carts[user_id]:
        user_carts[user_id][key]['qty'] += 1
    else:
        user_carts[user_id][key] = {'price': data['price'], 'qty': 1}
    
    await callback.message.answer(
        f"<b>{data['name']}</b> добавлен в корзину.\n"
        f"Текущее количество: <b>{user_carts[user_id][key]['qty']}</b>"
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'checkout')
async def checkout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, {})
    
    if not cart:
        await callback.message.answer("<b>Корзина пуста.</b>")
        await callback.answer()
        return
    
    # Формируем список товаров для анкеты
    items_list = []
    for key, data in cart.items():
        name = weapons[key]['name']
        qty = data['qty']
        items_list.append(f"{name} x{qty}")
    
    items_text = ", ".join(items_list)
    
    # Сохраняем состояние анкеты
    user_forms[user_id] = {
        'items': items_text,
        'cart': cart.copy()
    }
    
    await callback.message.answer(
        "<b>АНКЕТА ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА</b>\n"
        "——————————\n"
        f"Товар и количество: {items_text}\n"
        "——————————\n"
        "<i>Заполните и отправьте ответным сообщением:</i>\n\n"
        "<b>Укажите регион / район:</b>\n"
        "<i>(например: Центральный, Приморский)</i>"
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'clear_cart')
async def clear_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_carts[user_id] = {}
    await callback.message.answer("<b>Корзина очищена.</b>")
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_shop')
async def back_shop(callback: types.CallbackQuery):
    await callback.message.answer(
        "<b>Выберите категорию:</b>",
        reply_markup=get_shop_kb()
    )
    await callback.answer()

@dp.callback_query(lambda cb: cb.data == 'back_main')
async def back_main(callback: types.CallbackQuery):
    await callback.message.answer("<b>Возврат в главное меню.</b>", reply_markup=main_kb)
    await callback.answer()

# ========== ЗАПУСК ==========
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
