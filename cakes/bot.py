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
    if call.data == 'main':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Заказать новый торт', callback_data='new'))
        markup.add(InlineKeyboardButton(text='Заказать классические торты', callback_data='ready'))
        markup.add(InlineKeyboardButton(text='Промо акции', callback_data='promo'))
        bot.send_photo(call.message.chat.id,
                       r'https://media.istockphoto.com/id/625726848/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%B2%D0%BD%D0%B5-%D1%81%D0%B5%D0%B1%D1%8F-%D0%BE%D1%82-%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8-%D0%BF%D0%BE%D0%B6%D0%B8%D0%BB%D1%8B%D0%B5-%D0%BB%D1%8E%D0%B4%D0%B8-%D0%BF%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D1%83%D1%8E%D1%82-%D0%B4%D0%B5%D0%BD%D1%8C-%D1%80%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D1%82%D0%BE%D1%80%D1%82%D0%BE%D0%BC-%D0%B8-%D0%B2%D0%BE%D0%B7%D0%B4%D1%83%D1%88%D0%BD%D1%8B%D0%BC-%D1%88%D0%B0%D1%80%D0%BE%D0%BC.jpg?s=612x612&w=is&k=20&c=v8gc5liS19KsGnm3Fi3iosDcWEQj13k4eCh3gsoQEmk=',
                       'Вы знали, что у нас самые лучшие торты, попробуйте заказать', reply_markup=markup)

    if call.data == 'promo':
        promotions(call.message)
    if call.data == 'new':
        get_cake(call.message, 1)
    if call.data == 'ready':
        markup = ReplyKeyboardMarkup()
        cakes = Cake.objects.all()
        for cake in cakes:
            markup.add(KeyboardButton(f'{cake.name}, Цена: {cake.price}'))
        msg = bot.send_message(call.message.chat.id, 'Торты доступные к заказу:', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 4)


@bot.message_handler(commands=['start'])
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


def promotions(message):  # TODO Добавить данные по надобности(фото или описание)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='На главную', callback_data='main'))
    bot.send_photo(message.chat.id,
                   r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcImnndASe8l1YxGEWAtTBcy_muhX-c0KTHg&usqp=CAU',
                   'На сегодня нет акций, посмотрите завтра', reply_markup=markup)
    return


def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Заказать новый торт', callback_data='new'))
    markup.add(InlineKeyboardButton(text='Заказать классические торты', callback_data='ready'))
    markup.add(InlineKeyboardButton(text='Промо акции', callback_data='promo'))
    bot.send_photo(chat_id,
                   r'https://media.istockphoto.com/id/625726848/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%B2%D0%BD%D0%B5-%D1%81%D0%B5%D0%B1%D1%8F-%D0%BE%D1%82-%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8-%D0%BF%D0%BE%D0%B6%D0%B8%D0%BB%D1%8B%D0%B5-%D0%BB%D1%8E%D0%B4%D0%B8-%D0%BF%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D1%83%D1%8E%D1%82-%D0%B4%D0%B5%D0%BD%D1%8C-%D1%80%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D1%82%D0%BE%D1%80%D1%82%D0%BE%D0%BC-%D0%B8-%D0%B2%D0%BE%D0%B7%D0%B4%D1%83%D1%88%D0%BD%D1%8B%D0%BC-%D1%88%D0%B0%D1%80%D0%BE%D0%BC.jpg?s=612x612&w=is&k=20&c=v8gc5liS19KsGnm3Fi3iosDcWEQj13k4eCh3gsoQEmk=',
                   'Вы знали, что у нас самые лучшие торты, попробуйте заказать', reply_markup=markup)
    return


def get_cake(message, step):
    user = chats[message.chat.id]
    if step == 1:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        levels = Level.objects.all()
        for level in levels:
            markup.add(KeyboardButton(f'{level.level}, (Цена: {level.price})'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id,
                             r'https://i.pinimg.com/originals/84/2e/89/842e89f178017480c87c4e530084bdca.jpg',
                             'Количество уровней:', reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 2)

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
    elif step == 4:
        for topping in Topping.objects.all():
            if message.text == str(topping):
                user['topping'] = message.text[:message.text.find(',')]
                break
            else:
                user['ready_cake'] = message.text
                user['cake_id'] = Cake.objects.filter(name=message.text[:message.text.find(',')]).first().id
                break
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
            return bot.register_next_step_handler(message, delivery, 'order_cake')
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
            return bot.register_next_step_handler(message, delivery, 'order_cake')
        elif message.text == 'Пропустить':
            user['decor'] = None
        markup.add(KeyboardButton('Главное меню'))
        markup.add(KeyboardButton('Оформить заказ'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJ0sDLEcxz7BzeNgpLz0dUow5DBXUnWvmhhA&usqp=CAU',
                             f'Мы можем разместить на торте любую надпись, например: «С днем рождения!»\nСтоимость {Inscription.objects.all().first().price} рублей\nДля этого введите ниже надпись',
                             reply_markup=markup)
        return bot.register_next_step_handler(msg, get_cake, 7)

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
            Cake.objects.create(
                # TODO Торт который создастся нужно приписать к заявке, найти его id и добавить к user['cake_id']
                level=Level.objects.filter(level=user['level']).first(),
                shape=Shape.objects.filter(shape=user['shape']).first(),
                topping=Topping.objects.filter(name=user['topping']).first(),  # TODO подтянуть данные ManyToMany
                berry=Berry.objects.filter(name=user['berry']).first(),  # TODO подтянуть данные ManyToMany
                decor=Decor.objects.filter(name=user['decor']).first(),  # TODO подтянуть данные ManyToMany
            )

        return bot.register_next_step_handler(message, delivery, 'order_cake')


def delivery(message, step='order_cake'):
    user = chats[message.chat.id]
    if step == 'order_cake':
        user['agreement'] = True
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Доставка на дом'))
        markup.add(KeyboardButton('Самовывоз'))
        msg = bot.send_message(message.chat.id, 'Выберите способ получения торта', reply_markup=markup)
        return bot.register_next_step_handler(msg, delivery, 'choose_delivery')

    elif step == 'choose_delivery':
        if message.text == 'Доставка на дом':
            msg = bot.send_message(message.chat.id, 'Введите адрес доставки')
            return bot.register_next_step_handler(msg, delivery, 'show_available_time')
        elif message.text == 'Самовывоз':
            user['delivery'] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(KeyboardButton('Отлично'))
            msg = bot.send_message(message.chat.id, 'Самовывоз доступен только на ул. Уличная, д.1, кв.1',
                                   reply_markup=markup)

            return bot.register_next_step_handler(msg, delivery, 'show_available_time_pickup')

    elif step == 'show_available_time':
        user['delivery'] = True
        user['address'] = message.text
        shops = {'ул. Уличная, д.1, кв.1': ['09:00-12:00', '15:00-18:00']}  # TODO наполнение из БД для доставки
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for shop, times in shops.items():
            for delivery_time in times:
                markup.add(KeyboardButton(delivery_time))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpw2GptQezN2NNZKvwBTUVeVFJ1GofOD4OfA&usqp=CAU',
                             f'Адрес магазина: ул. Уличная, д.1, кв.1\nВыберите время доставки',
                             reply_markup=markup)  # TODO наполнение из БД для доставки
        return bot.register_next_step_handler(msg, delivery, 'confirmation')
    elif step == 'show_available_time_pickup':
        user['delivery'] = False
        user['address'] = 'Самовывоз'
        shops = {'ул. Уличная, д.1, кв.1': ['09:00-12:00', '15:00-18:00']}  # TODO наполнение из БД для доставки
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for shop, times in shops.items():
            for delivery_time in times:
                markup.add(KeyboardButton(delivery_time))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpw2GptQezN2NNZKvwBTUVeVFJ1GofOD4OfA&usqp=CAU',
                             f'Адрес магазина: ул. Уличная, д.1, кв.1\nВыберите время во сколько будет удобно забрать торт',
                             reply_markup=markup)  # TODO наполнение из БД для доставки
        return bot.register_next_step_handler(msg, delivery, 'confirmation')
    elif step == 'confirmation':
        user['delivery_time'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Оставить комментарий к заказу'))
        markup.add(KeyboardButton('Завершить заказ'))
        msg = bot.send_message(message.chat.id, 'Желаете ли вы оставить комментарий для кондитерской?',
                               reply_markup=markup)
        return bot.register_next_step_handler(msg, delivery, 'comment_or_finish')
    elif step == 'comment_or_finish':
        if message.text == 'Завершить заказ':
            Order.objects.create(
                customer_name=user['customer_name'],
                cake=Cake.objects.get(id=user['cake_id']),
                delivery_address=user['address'],
                delivery_date=datetime.datetime.now().strftime('%Y-%m-%d'),
                delivery_time=datetime.datetime.now().strftime('%H:%M:%S'),
                status=OrderStatus.objects.get(id=1),
                inscription=user['inscription']
            )
            bot.send_message(message.chat.id, 'Ваш заказ оформлен')
            time.sleep(2)
            return start(message)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        msg = bot.send_message(message.chat.id, 'Напишите комментарий', reply_markup=markup)
        return bot.register_next_step_handler(msg, delivery, 'comment_and_finish')
    elif step == 'comment_and_finish':
        user['comment'] = message.text
        bot.send_message(message.chat.id, 'Ваш заказ оформлен')
        Order.objects.create(
            customer_name=user['customer_name'],
            comment=user['comment'],
            cake=Cake.objects.get(id=user['cake_id']),
            delivery_address=user['address'],
            delivery_date=datetime.datetime.now().strftime('%Y-%m-%d'),
            delivery_time=datetime.datetime.now().strftime('%H:%M:%S'),
            status=OrderStatus.objects.get(id=1),
            inscription=user['inscription']
        )
        time.sleep(2)
        return start(message)


def run_bot():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    run_bot()
