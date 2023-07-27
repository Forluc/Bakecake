from environs import Env
import telebot
from telebot.util import quick_markup
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

Env().read_env()
token = Env().str('TG_TOKEN')
bot = telebot.TeleBot(token)

# empty
chats = {}

# buttons
ready_cake = KeyboardButton(text='Готовый торт')
new_cake = KeyboardButton(text='Новый торт')


# markups
markup_choose_cake = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
markup_choose_cake.add(ready_cake, new_cake)

# quick markup
client_markup = quick_markup({
    'Заказать торт': {'callback_data': 'get_cake'},
    'Акции и промо': {'callback_data': 'promotions'},
})
