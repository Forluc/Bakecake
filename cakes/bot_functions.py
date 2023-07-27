import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from bot_other import bot, chats, client_markup, markup_choose_cake
import time

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bakecake.settings")
django.setup()

from cakes.models import Cake


def start_bot(message: telebot.types.Message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}.')
    chats[message.chat.id] = {
        'ready_cake': None,
        'level': None,
        'form': None,
        'topping': None,
        'berry': None,
        'decor': None,
        'inscription': None,
        'agreement': None,
        'delivery': None,
        'address': None,
        'delivery_time': None,
        'comment': None,
    }
    show_main_menu(message.chat.id)


def show_main_menu(chat_id):  # TODO Добавить данные по надобности(фото или описание)
    bot.send_photo(chat_id,
                   r'https://media.istockphoto.com/id/625726848/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%B2%D0%BD%D0%B5-%D1%81%D0%B5%D0%B1%D1%8F-%D0%BE%D1%82-%D1%80%D0%B0%D0%B4%D0%BE%D1%81%D1%82%D0%B8-%D0%BF%D0%BE%D0%B6%D0%B8%D0%BB%D1%8B%D0%B5-%D0%BB%D1%8E%D0%B4%D0%B8-%D0%BF%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D1%83%D1%8E%D1%82-%D0%B4%D0%B5%D0%BD%D1%8C-%D1%80%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D1%81-%D1%82%D0%BE%D1%80%D1%82%D0%BE%D0%BC-%D0%B8-%D0%B2%D0%BE%D0%B7%D0%B4%D1%83%D1%88%D0%BD%D1%8B%D0%BC-%D1%88%D0%B0%D1%80%D0%BE%D0%BC.jpg?s=612x612&w=is&k=20&c=v8gc5liS19KsGnm3Fi3iosDcWEQj13k4eCh3gsoQEmk=',
                   'Вы знали, что у нас самые лучшие торты, попробуйте заказать', reply_markup=client_markup)


def promotions(message: telebot.types.Message):  # TODO Добавить данные по надобности(фото или описание)
    bot.send_photo(message.chat.id,
                   r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcImnndASe8l1YxGEWAtTBcy_muhX-c0KTHg&usqp=CAU',
                   'На сегодня нет акций, посмотрите завтра')
    time.sleep(2)
    show_main_menu(message.chat.id)


def get_cake(message: telebot.types.Message, step='main_menu'):
    user = chats[message.chat.id]
    if step == 'main_menu':
        msg = bot.send_message(message.chat.id, 'Закажите один из классических тортов или создайте свой',
                               reply_markup=markup_choose_cake)
        bot.register_next_step_handler(msg, get_cake, 1)
    elif step == 1:
        if message.text == 'Готовый торт':
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            ready_cakes = {  # TODO взять данные из БД
                'Бисквитный': {'Цена': 1000, 'Состав': ['Яйца', 'Вода', 'Крем']},
                'Песочный': {'Цена': 1500, 'Состав': ['Яйца', 'Вода', 'Крем']},
                'Творожный': {'Цена': 2000, 'Состав': ['Яйца', 'Вода', 'Крем']},
            }
            for cake, cake_info in ready_cakes.items():
                markup.add(KeyboardButton(f'{cake} Цена:{cake_info["Цена"]}'))
            markup.add(KeyboardButton('Главное меню'))
            msg = bot.send_message(message.chat.id, 'Торты доступные к заказу:', reply_markup=markup)
            return bot.register_next_step_handler(msg, get_cake, 4)

        cake_information = {  # TODO взять данные из БД
            '1 уровень': 400,
            '2 уровня': 750,
            '3 уровня': 1100,
        }
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for cake, cake_info in cake_information.items():
            markup.add(KeyboardButton(f'{cake} (Цена:{cake_info})'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id,
                             r'https://i.pinimg.com/originals/84/2e/89/842e89f178017480c87c4e530084bdca.jpg',
                             'Количество уровней:', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 2)
    elif step == 2:
        user['level'] = message.text
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        cake_information = {  # TODO взять данные из БД
            'Квадрат': 400,
            'Круг': 750,
            'Прямоугольник': 1100,
        }
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for cake, cake_info in cake_information.items():
            markup.add(KeyboardButton(f'{cake} (Цена:{cake_info})'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id, r'https://basket-01.wb.ru/vol138/part13858/13858945/images/big/1.jpg',
                             'Форма для торта', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 3)
    elif step == 3:
        user['form'] = message.text
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        cake_information = {  # TODO взять данные из БД
            'Белый соус': 400,
            'Карамельный сироп': 750,
            'Клубничный сироп': 1100,
        }
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for cake, cake_info in cake_information.items():
            markup.add(KeyboardButton(f'{cake} (Цена:{cake_info})'))
        markup.add(KeyboardButton('Главное меню'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReYS9aeqwbgfu4V4CiONdNbqbiMEmLAdZDbw&usqp=CAU',
                             'Выбор сиропа', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 4)
    elif step == 4:
        if message.text in ['Белый соус', ]:
            user['topping'] = message.text
        else:
            user['ready_cake'] = message.text
        if message.text == 'Главное меню':
            return show_main_menu(message.chat.id)
        cake_information = {  # TODO взять данные из БД
            'Ежевика': 400,
            'Малина': 750,
            'Клубника': 1100,
        }
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for cake, cake_info in cake_information.items():
            markup.add(KeyboardButton(f'{cake} (Цена:{cake_info})'))
        markup.add(KeyboardButton('Главное меню'))
        markup.add(KeyboardButton('Оформить заказ'))
        markup.add(KeyboardButton('Пропустить'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTB3VGZ1-Xpckl65Ij3AgvzEdmyedtghSLm0w&usqp=CAU',
                             'Ягоды для торта', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 5)
    elif step == 5:
        user['berry'] = message.text
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
        cake_information = {  # TODO взять данные из БД
            'Фисташки': 400,
            'Безе': 750,
        }
        for cake, cake_info in cake_information.items():
            markup.add(KeyboardButton(f'{cake} (Цена:{cake_info})'))
        markup.add(KeyboardButton('Главное меню'))
        markup.add(KeyboardButton('Оформить заказ'))
        markup.add(KeyboardButton('Пропустить'))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRL0J9gnCk1PYz1zx4H3ybiYOA_aaxYmFPug&usqp=CAU',
                             'Декор для торта', reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 6)
    elif step == 6:
        user['decor'] = message.text
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
                             'Мы можем разместить на торте любую надпись, например: «С днем рождения!»\nДля этого введите ниже надпись',
                             reply_markup=markup)
        bot.register_next_step_handler(msg, get_cake, 7)

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
        return bot.register_next_step_handler(message, delivery, 'order_cake')


def delivery(message: telebot.types.Message, step='order_cake'):
    user = chats[message.chat.id]
    if step == 'order_cake':
        user['agreement'] = True
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Доставка на дом'))
        markup.add(KeyboardButton('Самовывоз'))
        msg = bot.send_message(message.chat.id, 'Выберите способ получения торта', reply_markup=markup)
        bot.register_next_step_handler(msg, delivery, 'choose_delivery')

    elif step == 'choose_delivery':
        if message.text == 'Доставка на дом':
            msg = bot.send_message(message.chat.id, 'Введите адрес доставки')
            bot.register_next_step_handler(msg, delivery, 'show_available_time')
        if message.text == 'Самовывоз':
            user['delivery'] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(KeyboardButton('Отлично'))
            msg = bot.send_message(message.chat.id, 'Самовывоз доступен только на ул. Уличная, д.1, кв.1',
                                   # TODO взять данные из БД
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, delivery, 'show_available_time_pickup')

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
        bot.register_next_step_handler(msg, delivery, 'confirmation')
    elif step == 'show_available_time_pickup':
        user['delivery'] = False
        shops = {'ул. Уличная, д.1, кв.1': ['09:00-12:00', '15:00-18:00']}  # TODO наполнение из БД для доставки
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for shop, times in shops.items():
            for delivery_time in times:
                markup.add(KeyboardButton(delivery_time))
        msg = bot.send_photo(message.chat.id,
                             r'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpw2GptQezN2NNZKvwBTUVeVFJ1GofOD4OfA&usqp=CAU',
                             f'Адрес магазина: ул. Уличная, д.1, кв.1\nВыберите время во сколько будет удобно забрать торт',
                             reply_markup=markup)  # TODO наполнение из БД для доставки
        bot.register_next_step_handler(msg, delivery, 'confirmation')
    elif step == 'confirmation':
        user['delivery_time'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Оставить комментарий к заказу'))
        markup.add(KeyboardButton('Завершить заказ'))
        msg = bot.send_message(message.chat.id, 'Желаете ли вы оставить комментарий для кондитерской?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, delivery, 'comment_or_finish')
    elif step == 'comment_or_finish':
        if message.text == 'Завершить заказ':
            # TODO Занести заказ юзера в БД
            bot.send_message(message.chat.id, 'Ваш заказ оформлен')
            time.sleep(2)
            return start_bot(message)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        msg = bot.send_message(message.chat.id, 'Напишите комментарий', reply_markup=markup)
        bot.register_next_step_handler(msg, delivery, 'comment_and_finish')
    elif step == 'comment_and_finish':
        user['comment'] = message.text
        bot.send_message(message.chat.id, 'Ваш заказ оформлен')
        # TODO Занести заказ юзера в БД
        time.sleep(2)
        return start_bot(message)
