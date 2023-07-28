import datetime

from environs import Env
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import telebot
import django
import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bakecake.settings")
django.setup()
from cakes.models import Level, Shape, Topping, Berry, Decor, Inscription, Cake, Order, OrderStatus

Env().read_env()
token = Env().str('TG_TOKEN')
bot = telebot.TeleBot(token)

chats = {}


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message.chat.id not in chats:
        # Если пользователя еще нет в словаре, создаем запись для него
        chats[call.message.chat.id] = {}
    # Кнопка основного меню
    if call.data == 'main':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Заказать новый торт', callback_data='new'))
        markup.add(InlineKeyboardButton(text='Заказать классические торты', callback_data='ready'))
        markup.add(InlineKeyboardButton(text='Промо акции', callback_data='promo'))
        bot.send_photo(call.message.chat.id,
                       r'https://media.istockphoto.com/id/625726848/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%B2%D0%BD%D0%B5-%D1%81%D0%B5%D0%B1%D1%8F-%D0%BE%D1%82-%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8-%D0%BF%D0%BE%D0%B6%D0%B8%D0%BB%D1%8B%D0%B5-%D0%BB%D1%8E%D0%B4%D0%B8-%D0%BF%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D1%83%D1%8E%D1%82-%D0%B4%D0%B5%D0%BD%D1%8C-%D1%80%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D1%82%D0%BE%D1%80%D1%82%D0%BE%D0%BC-%D0%B8-%D0%B2%D0%BE%D0%B7%D0%B4%D1%83%D1%88%D0%BD%D1%8B%D0%BC-%D1%88%D0%B0%D1%80%D0%BE%D0%BC.jpg?s=612x612&w=is&k=20&c=v8gc5liS19KsGnm3Fi3iosDcWEQj13k4eCh3gsoQEmk=',
                       'Вы знали, что у нас самые лучшие торты, попробуйте заказать', reply_markup=markup)
    # Кнопка акций
    if call.data == 'promo':
        promotions(call.message)
    # Кнопка для создания нового торта
    if call.data == 'new':
        get_cake(call.message, 1)
    # Кнопка для выбора существующего торта с возможностью добавить что-то еще
    if call.data == 'ready':
        markup = ReplyKeyboardMarkup()
        ready_cakes = Cake.objects.filter(is_custom=False)
        for cake in ready_cakes:
            markup.add(KeyboardButton(f'{cake.name}, Цена: {cake.price}'))
        msg = bot.send_message(call.message.chat.id, 'Торты доступные к заказу:', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 4)


@bot.message_handler(commands=['start'])
# Начало работы бота
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Конечно', callback_data='main'))
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. Хочешь тортик?', reply_markup=markup)
    chats[message.chat.id] = {
        'ready_cake': None,
        'level': None,
        'shape': None,
        'topping': None,
        'berry': None,
        'decor': None,
        'inscription': None,
        'agreement': None,
        'delivery': None,
        'address': None,
        'delivery_time': None,
        'comment': None,
        'customer_name': message.from_user.first_name,
        'cake_id': None
    }


# Функция для просмотра акций
def promotions(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='На главную', callback_data='main'))
    bot.send_photo(message.chat.id,
                   r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcImnndASe8l1YxGEWAtTBcy_muhX-c0KTHg&usqp=CAU',
                   'На сегодня нет акций, посмотрите завтра', reply_markup=markup)
    return


# Функция основного меню
def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Заказать новый торт', callback_data='new'))
    markup.add(InlineKeyboardButton(text='Заказать классические торты', callback_data='ready'))
    markup.add(InlineKeyboardButton(text='Промо акции', callback_data='promo'))
    bot.send_photo(chat_id,
                   r'https://media.istockphoto.com/id/625726848/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%B2%D0%BD%D0%B5-%D1%81%D0%B5%D0%B1%D1%8F-%D0%BE%D1%82-%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8-%D0%BF%D0%BE%D0%B6%D0%B8%D0%BB%D1%8B%D0%B5-%D0%BB%D1%8E%D0%B4%D0%B8-%D0%BF%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D1%83%D1%8E%D1%82-%D0%B4%D0%B5%D0%BD%D1%8C-%D1%80%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D1%82%D0%BE%D1%80%D1%82%D0%BE%D0%BC-%D0%B8-%D0%B2%D0%BE%D0%B7%D0%B4%D1%83%D1%88%D0%BD%D1%8B%D0%BC-%D1%88%D0%B0%D1%80%D0%BE%D0%BC.jpg?s=612x612&w=is&k=20&c=v8gc5liS19KsGnm3Fi3iosDcWEQj13k4eCh3gsoQEmk=',
                   'Вы знали, что у нас самые лучшие торты, попробуйте заказать', reply_markup=markup)


def get_cake(message, step):
    user = chats[message.chat.id]
    # Выбор количества уровней
    if step == 1:
        user['ready_cake'] = None
        user['topping'] = None
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        levels = Level.objects.all()
        for level in levels:
            markup.add(KeyboardButton(f'{level.level}, (Цена: {level.price})'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id,
                             r'https://i.pinimg.com/originals/84/2e/89/842e89f178017480c87c4e530084bdca.jpg',
                             'Количество уровней:', reply_markup=markup)
        chat_id = message.chat.id  # Получаем идентификатор чата (chat_id) пользователя
        if chat_id not in chats:
            chats[chat_id] = {}  # Создаем словарь для этого пользователя, если его еще нет
        user = chats[chat_id]
        user['customer_name'] = message.from_user.first_name
        return bot.register_next_step_handler(msg, get_cake, 2)
    # Выбор формы для торта
    elif step == 2:
        user['level'] = message.text[:message.text.find(',')]
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        shapes = Shape.objects.all()
        for shape in shapes:
            markup.add(KeyboardButton(f'{shape.shape}, (Цена: {shape.price})'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id, r'https://basket-01.wb.ru/vol138/part13858/13858945/images/big/1.jpg',
                             'Форма для торта', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 3)
    # Выбор сиропа для торта
    elif step == 3:
        user['shape'] = message.text[:message.text.find(',')]
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        toppings = Topping.objects.all()
        for topping in toppings:
            markup.add(KeyboardButton(f'{topping}'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReYS9aeqwbgfu4V4CiONdNbqbiMEmLAdZDbw&usqp=CAU',
                             'Выбор сиропа', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 4)
    # Выбор ягод для торта
    elif step == 4:
        user['ready_cake'] = None
        user['topping'] = None
        for topping in Topping.objects.all():
            if message.text == str(topping):
                user['topping'] = message.text[:message.text.find(',')]
                break
        if not user['topping']:

            user['ready_cake'] = message.text
            user['cake_id'] = Cake.objects.filter(name=message.text[:message.text.find(',')]).first().id

        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        berries = Berry.objects.all()
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for berry in berries:
            markup.add(KeyboardButton(f'{berry.name}, Цена {berry.price}'))
        markup.add(KeyboardButton('Главное меню'))
        markup.add(KeyboardButton('Оформить заказ'))
        markup.add(KeyboardButton('Пропустить'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTB3VGZ1-Xpckl65Ij3AgvzEdmyedtghSLm0w&usqp=CAU',
                             'Ягоды для торта', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 5)
    # Выбор декора для торта
    elif step == 5:
        user['berry'] = message.text[:message.text.find(',')]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        elif message.text == 'Оформить заказ':
            markup.add(KeyboardButton('Подтвердить'))
            bot.send_message(message.chat.id,
                             'Подтверждая, вы принимаете условия по обработке персональных данных', reply_markup=markup)
            user['berry'] = None
            return bot.register_next_step_handler(message, get_delivery, 'order_cake')
        elif message.text == 'Пропустить':
            user['berry'] = None
        decors = Decor.objects.all()
        for decor in decors:
            markup.add(KeyboardButton(f'{decor.name}, Цена: {decor.price}'))
        markup.add(KeyboardButton('Главное меню'))
        markup.add(KeyboardButton('Оформить заказ'))
        markup.add(KeyboardButton('Пропустить'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRL0J9gnCk1PYz1zx4H3ybiYOA_aaxYmFPug&usqp=CAU',
                             'Декор для торта', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 6)
    # Выбор надписи для торта
    elif step == 6:
        user['decor'] = message.text[:message.text.find(',')]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        elif message.text == 'Оформить заказ':
            markup.add(KeyboardButton('Подтвердить'))
            bot.send_message(message.chat.id,
                             'Подтверждая, вы принимаете условия по обработке персональных данных', reply_markup=markup)
            user['decor'] = None
            return bot.register_next_step_handler(message, get_delivery, 'order_cake')
        elif message.text == 'Пропустить':
            user['decor'] = None
        markup.add(KeyboardButton('Главное меню'))
        markup.add(KeyboardButton('Оформить заказ'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJ0sDLEcxz7BzeNgpLz0dUow5DBXUnWvmhhA&usqp=CAU',
                             f'Мы можем разместить на торте любую надпись, например: «С днем рождения!»\nСтоимость {Inscription.objects.all().first().price} рублей\nДля этого введите ниже надпись',
                             reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 7)
    # Принятие оферты и создание нового торта, если был выбран создать новый
    elif step == 7:
        user['inscription'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        elif message.text == 'Оформить заказ':
            user['inscription'] = None
        markup.add(KeyboardButton('Подтвердить'))
        bot.send_message(message.chat.id,
                         'Подтверждая, вы принимаете условия по обработке персональных данных', reply_markup=markup)
        if not user['ready_cake']:
            cake = Cake.objects.create(
                # TODO Добавлять торт исходя из введенных данных пользователя
                is_custom=True,
                level=Level.objects.filter(level=user['level']).first(),
                shape=Shape.objects.filter(shape=user['shape']).first(),
            )
            user['cake_id'] = cake.id
            user['ready_cake'] = f'{cake.name},'
        return bot.register_next_step_handler(message, get_delivery, 'order_cake')


def get_delivery(message, step='order_cake'):
    user = chats[message.chat.id]
    if step == 'order_cake':
        user['agreement'] = True
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Доставка на дом'))
        markup.add(KeyboardButton('Самовывоз'))
        msg = bot.send_message(message.chat.id, 'Выберите способ получения торта', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_delivery, 'choose_delivery')

    elif step == 'choose_delivery':
        if message.text == 'Доставка на дом':
            msg = bot.send_message(message.chat.id, 'Введите адрес доставки')
            return bot.register_next_step_handler(msg, get_delivery, 'show_available_time')
        elif message.text == 'Самовывоз':
            user['delivery'] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(KeyboardButton('Отлично'))
            msg = bot.send_message(message.chat.id, 'Самовывоз доступен только на ул. Уличная, д.1, кв.1',
                                   reply_markup=markup)

            return bot.register_next_step_handler(msg, get_delivery, 'show_available_time_pickup')

    elif step == 'show_available_time':
        user['delivery'] = True
        user['address'] = message.text
        shops = {'ул. Уличная, д.1, кв.1': ['09:00-12:00', '15:00-18:00']}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for shop, times in shops.items():
            for delivery_time in times:
                markup.add(KeyboardButton(delivery_time))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpw2GptQezN2NNZKvwBTUVeVFJ1GofOD4OfA&usqp=CAU',
                             f'Адрес магазина: ул. Уличная, д.1, кв.1\nВыберите время доставки',
                             reply_markup=markup)
        return bot.register_next_step_handler(msg, get_order, 'confirmation')
    elif step == 'show_available_time_pickup':
        user['delivery'] = False
        user['address'] = 'Самовывоз'
        shops = {'ул. Уличная, д.1, кв.1': ['09:00-12:00', '15:00-18:00']}
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for shop, times in shops.items():
            for delivery_time in times:
                markup.add(KeyboardButton(delivery_time))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpw2GptQezN2NNZKvwBTUVeVFJ1GofOD4OfA&usqp=CAU',
                             f'Адрес магазина: ул. Уличная, д.1, кв.1\nВыберите время во сколько будет удобно забрать торт завтра',
                             reply_markup=markup)
        return bot.register_next_step_handler(msg, get_order, 'confirmation')


def get_order(message, step='confirmation'):
    user = chats[message.chat.id]
    if step == 'confirmation':
        user['delivery_time'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Оставить комментарий к заказу'))
        markup.add(KeyboardButton('Завершить заказ'))
        msg = bot.send_message(message.chat.id, 'Желаете ли вы оставить комментарий для кондитерской?',
                               reply_markup=markup)
        return bot.register_next_step_handler(msg, get_order, 'comment_or_finish')

    elif step == 'comment_or_finish':
        if message.text == 'Завершить заказ':
            cake = Order.objects.create(
                customer_name=user['customer_name'],
                cake=Cake.objects.get(id=user['cake_id']),
                delivery_address=user['address'],
                delivery_date=datetime.datetime.now().strftime('%Y-%m-%d'),
                delivery_time=datetime.datetime.now().strftime('%H:%M:%S'),
                status=OrderStatus.objects.get(id=1),
                inscription=user['inscription']
            )
            if cake:
                bot.send_message(message.chat.id, 'Ваш заказ оформлен')
                bot.send_message(message.chat.id,
                                 f"Имя: {user['customer_name']}\nТорт: {user['ready_cake'][:user['ready_cake'].find(',')]}\nДобавки для торта: {user['berry'] if user['berry'] else ''} {user['decor'] if user['decor'] else ''} {user['inscription'] if user['inscription'] else ''}\nАдрес доставки: {user['address']}\nВремя получения:{user['delivery_time']}\nИтоговая стоимость: {cake.total_price}")
            time.sleep(5)
            return start(message)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        msg = bot.send_message(message.chat.id, 'Напишите комментарий', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_order, 'comment_and_finish')
    elif step == 'comment_and_finish':
        user['comment'] = message.text
        cake = Order.objects.create(
            customer_name=user['customer_name'],
            comment=user['comment'],
            cake=Cake.objects.get(id=user['cake_id']),
            delivery_address=user['address'],
            delivery_date=datetime.datetime.now().strftime('%Y-%m-%d'),
            delivery_time=datetime.datetime.now().strftime('%H:%M:%S'),
            status=OrderStatus.objects.get(id=1),
            inscription=user['inscription']
        )
        if cake:
            bot.send_message(message.chat.id, 'Ваш заказ оформлен')
            bot.send_message(message.chat.id,
                             f"Имя: {user['customer_name']}\nТорт: {user['ready_cake'][:user['ready_cake'].find(',')]}\nДобавки для торта: {user['berry'] if user['berry'] else ''}{user['decor'] if user['decor'] else ''}{user['inscription'] if user['inscription'] else ''}\nАдрес доставки: {user['address']}\nВремя получения:{user['delivery_time']}\nКомментарий к заказу: {user['comment']}\nИтоговая стоимость: {cake.total_price}")
        time.sleep(5)
        return start(message)


def run_bot():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    run_bot()