import telebot
from telebot import types
from PIL import Image
import os

token = "2085631034:AAFdxr3MiZ6gkkvtkdlSDxmI37ClVp0tAGg"
bot = telebot.TeleBot(token)


# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=["start", "help"])
def send_keyboard(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup()  # наша клавиатура
    itembtn1 = types.KeyboardButton("Поместить логотип на картинку")  # создадим кнопку
    keyboard.add(itembtn1)  # добавим кнопку

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.chat.id,
                           text=text, reply_markup=keyboard)

    bot.register_next_step_handler(msg, callback_worker)


def callback_worker(call):
    if call.text == "Поместить логотип на картинку":
        msg = bot.send_message(call.chat.id, 'Отлично, загрузите фото')
        bot.register_next_step_handler(msg, add_logo)


# добавление логотипа на картинку
def add_logo(msg):
    photo_id = msg.photo[-1].file_id
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(f"pic{msg.from_user.id}.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.send_message(msg.chat.id, "Спасибо, сейчас добавлю лого!")
    logo_file = "logoColliers.jpg"
    logo_im = Image.open(logo_file)
    logo_width, logo_height = logo_im.size

    im = Image.open(f"pic{msg.from_user.id}.jpg")
    width, height = im.size
    im.paste(logo_im, tuple([width - logo_width, height - logo_height, width, height]))
    bot.send_photo(msg.chat.id, im)

    os.remove(f"pic{msg.from_user.id}.jpg")


@bot.message_handler(regexp=r"^#работы_")
def handle_message(msg):
    text = f"Вижу, {msg.from_user.first_name} {msg.from_user.last_name} постит работы {msg.text}"

    msg = bot.send_message(msg.chat.id, text=text)


@bot.message_handler(commands=["report"])
def handle_message(msg):
    text = "Скоро вы сможете увидеть отчет, сейчас - нет("

    msg = bot.send_message(msg.chat.id, text=text)


bot.polling(none_stop=True)

# подкдючимся к api яндекс.диска

import pandas as pd
import requests
import urllib
import json
import io

api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='

# Важно! ниже ссылка на файл, с которым мы работаем, её нужно поменять, пока я залила тестовый файл
source_url = urllib.parse.quote_plus('https://disk.yandex.ru/d/pnJSIkrpcEmGHg')

url_file = api_url + source_url

# Запрашиваю урл 
req_url = requests.get(url_file) 

# Распарсим полученный урл и выделим урл загрузки
download_url = json.loads(req_url.text)['file'] 

# Создаем датафрейм
# Важно! уточнить у Лёши название листа и диапазон, который хотим залить в датафрейм. Или при построении графика - поменять диапазон
xl_df = pd.read_excel(download_url, sheet_name = 'sheet_1')



