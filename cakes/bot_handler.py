from bot_other import telebot, bot
import bot_functions as calls

calls_map = {
    'get_cake': calls.get_cake,
    'promotions': calls.promotions,
}


@bot.message_handler(commands=['start'])
def command_menu(message: telebot.types.Message):
    calls.start_bot(message)


@bot.callback_query_handler(func=lambda call: call.data)
def handle_buttons(call):
    calls_map[call.data](call.message)


bot.polling(none_stop=True)
