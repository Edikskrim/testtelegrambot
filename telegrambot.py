import telebot
from telebot import types
import const
from geopy.distance import vincenty

bot = telebot.TeleBot(const.API_TOKEN)

markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn_address = types.KeyboardButton('Адрес магаза', request_location=True)
btn_payment = types.KeyboardButton('Способы оплаты')
btn_delivery = types.KeyboardButton('Способы доставки')
markup_menu.add(btn_address,btn_delivery,btn_payment)


markup_inline_payment = types.InlineKeyboardMarkup()
btn_in_cash = types.InlineKeyboardButton('Наличные', callback_data='cash')
btn_in_card = types.InlineKeyboardButton('По карте', callback_data='card')
btn_in_invoice = types.InlineKeyboardButton('Банковский перевод', callback_data='invoice')
markup_inline_payment.add(btn_in_cash,btn_in_card,btn_in_invoice)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Привет, я тест бот", reply_markup=markup_menu)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Способы доставки":
        bot.reply_to(message, "Доставка курьером почты росиии",reply_markup=markup_menu)
    elif message.text == "Способы оплаты":
        bot.reply_to(message, "В наших магазинах доступны следующие способы оплаты", reply_markup=markup_inline_payment)
    else:
	    bot.reply_to(message, message.text,reply_markup=markup_menu)

@bot.message_handler(func=lambda message: True, content_types=['location'])
def magazin_location(messege):
    lon = messege.location.longitude
    lat = messege.location.latitude

    disttance = []
    for m in const.MAGAZINS:
        result = vincenty((m['latm'],m['lonm']),(lat,lon)).kilometers
        disttance.append(result)
    index = disttance.index(min(disttance))

    bot.send_message(messege.chat.id,'Ближайший к вам магазин')
    bot.send_venue(messege.chat.id,
                                        const.MAGAZINS[index]['latm'],
                                        const.MAGAZINS[index]['lonm'],
                                        const.MAGAZINS[index]['title'],
                                        const.MAGAZINS[index]['address'])

@bot.callback_query_handler(func=lambda call: True)
def call_back_payment(call):
    if call.data == 'cash':
        bot.send_message(call.message.chat.id, text="""
        Наличная оплата производится в рублях, в кассе магазина
        """,reply_markup=markup_inline_payment)
    elif call.data == 'card':
        bot.send_message(call.message.chat.id, text="""
        Вы можете оплатить картами Visa или Matercard
        """,reply_markup=markup_inline_payment)

bot.polling()