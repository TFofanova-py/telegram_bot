import telebot
from telebot import types

bot = telebot.TeleBot("2085631034:AAFdxr3MiZ6gkkvtkdlSDxmI37ClVp0tAGg")


# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=["start", "help"])
def send_keyboard(message, text="Привет, я бот, который собирает информацию о продвижении дел на нашей стройке:)"):
    keyboard = types.ReplyKeyboardMarkup()  # наша клавиатура
    itembtn1 = types.KeyboardButton("Ок, понятно")  # создадим кнопку
    keyboard.add(itembtn1)  # добавим кнопку

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)


@bot.message_handler(regexp=r"^#работы_")
def handle_message(msg):
    text = f"Вижу, {msg.from_user.first_name} {msg.from_user.last_name} постит работы {msg.text}"

    msg = bot.send_message(msg.chat.id, text=text)


@bot.message_handler(commands=["report"])
def handle_message(msg):
    text = "Скоро вы сможете увидеть отчет, сейчас - нет("

    msg = bot.send_message(msg.chat.id, text=text)


bot.polling(none_stop=True)
