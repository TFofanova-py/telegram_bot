import telebot
from telebot import types, TeleBot
from PIL import Image
import os
import pandas as pd
import requests
import urllib
import json
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

token = "2085631034:AAFdxr3MiZ6gkkvtkdlSDxmI37ClVp0tAGg"
bot: TeleBot = telebot.TeleBot(token)


# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=["start"])
def send_keyboard(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # наша клавиатура
    itembtn1 = types.KeyboardButton("Отчет за сегодня")  # создадим кнопку
    itembtn2 = types.KeyboardButton("Отчет за неделю")
    itembtn3 = types.KeyboardButton("Поместить логотип на картинку")
    itembtn4 = types.KeyboardButton("Список подрядчиков")
    itembtn5 = types.KeyboardButton("Пока все")

    keyboard.add(itembtn1, itembtn2)  # добавим кнопки
    keyboard.add(itembtn3, itembtn4)
    keyboard.add(itembtn5)

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.chat.id,
                           text=text, reply_markup=keyboard)

    bot.register_next_step_handler(msg, callback_worker)


def callback_worker(call):
    if call.text == "Поместить логотип на картинку":
        msg = bot.send_message(call.chat.id, 'Отлично, загрузи фото')
        bot.register_next_step_handler(msg, add_logo)

    elif call.text == "Отчет за неделю":
        today = datetime(2021, 10, 13).date()
        n_days = today.weekday() + 1
        grouped_data = get_done_jobs(n_days)
        create_report(call, grouped_data)

    elif call.text == "Отчет за сегодня":
        grouped_data = get_done_jobs(1)
        create_report(call, grouped_data)

    elif call.text == "Список подрядчиков":
        selected_jobs = ("Разработка котлована", "Бетонная подготовка",
                         "Армирование фундаментной  (125 кг/м3)",
                         "Бетонирование фундаментной плиты")
        job_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for j in selected_jobs:
            job_keyboard.add(types.KeyboardButton(j))

        msg = bot.send_message(call.chat.id,
                               text="Выбери вид работ",
                               reply_markup=job_keyboard)
        bot.register_next_step_handler(msg, get_workers)

    elif call.text == "Пока все":
        msg = bot.send_message(call.chat.id, "Пока!")

    else:
        msg = bot.send_message(call.chat.id, text="Не понимаю :(")
        send_keyboard(msg, "Чем еще могу помочь?")


def test_callback(msg):
    msg = bot.send_message(msg.chat.id, "Test from test")
    send_keyboard(msg, "Call keyboard")


# добавление логотипа на картинку
def add_logo(msg):
    photo_id = msg.photo[-1].file_id
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    pic_name = f"pic{msg.from_user.id}.jpg"
    with open(pic_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.send_message(msg.chat.id, "Спасибо, сейчас добавлю лого!")
    logo_file = "logoColliers.jpg"
    logo_im = Image.open(logo_file)
    logo_width, logo_height = logo_im.size

    im = Image.open(f"pic{msg.from_user.id}.jpg")
    width, height = im.size
    im.paste(logo_im, tuple([width - logo_width, height - logo_height, width, height]))
    msg = bot.send_photo(msg.chat.id, im)
    os.remove(pic_name)

    send_keyboard(msg, "Чем еще могу помочь?")


# создание датафрейма из .xslx файла с я.диска
def create_dataframe():
    api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='  # апи диска
    folder_url = urllib.parse.quote_plus('https://disk.yandex.ru/d/pnJSIkrpcEmGHg')  # паблик ссылка на сам файл
    url_file = api_url + folder_url  # генерим ссылку для запроса ссылки на скачивание
    req_url = requests.get(url_file)  # отправляем запрос - и получаем в ответ метаинформацию о файле
    download_url = json.loads(req_url.text)['file']  # парсим респонс - и выделяем из него ссылку для загрузки файла
    new_df = pd.read_excel(download_url, sheet_name='sheet_1')  # используя пандас, считываем файл в датафрейм
    return new_df


# отбор отлеживаемых работ (строк) в датафрейме
def select_jobs(data, selected_jobs=("Разработка котлована", "Бетонная подготовка",
                                     "Армирование фундаментной  (125 кг/м3)",
                                     "Бетонирование фундаментной плиты")):
    data["job"] = data["job_raw"].apply(lambda x: x.strip())
    data.drop(["job_raw"], axis=1, inplace=True)

    mask = data["job"].apply(lambda x: x in selected_jobs)
    return data[mask]


# создание датафрейма с агрегированными данными по работам
# за последние n_last_days дней
def get_done_jobs(n_last_days):
    start = datetime(2021, 8, 30).date()
    today = datetime(2021, 10, 13).date()
    days_from_start = (today - start).days

    df = pd.read_excel("Book2.xlsx", skiprows=5, header=None,
                       usecols=[2] + list(range(20, 21 + days_from_start)))
    # df = create_dataframe().iloc[5:, [2] + list(range(20, 21 + days_from_start))]

    cols = ["job_raw", ]
    for d in (start + timedelta(days=i) for i in range(days_from_start + 1)):
        cols += [d.isoformat()]
    df.columns = cols

    df = select_jobs(df)
    df = df.iloc[:, -n_last_days - 1:]

    df_long = df.melt(id_vars=["job"], var_name="date")
    grouped = df_long.groupby(["job", "date"]).sum().apply(lambda x: round(x, 2))
    grouped["date"] = grouped.index.get_level_values(1)
    grouped["job"] = grouped.index.get_level_values(0)
    return grouped


def create_report(msg, gr_data):
    # сохранение графика в картинку
    ax = sns.barplot(x="date", y="value", hue="job", data=gr_data)
    ax.set(xlabel="Дата", ylabel="Объем работ", title="Выполненные работы")

    chart_name = f"chart{msg.from_user.id}.png"
    plt.savefig(chart_name)
    plt.clf()

    msg = bot.send_photo(msg.chat.id,
                         photo=open(chart_name, "rb"))
    os.remove(chart_name)

    send_keyboard(msg, "Чем еще могу помочь?")


# получение списка подрядчиков
def get_workers(msg):
    job = msg.text
    # df = create_dataframe().iloc[5:, [2, 19]]
    # df.columns = ["job_raw", "worker"]
    df = pd.read_excel("Book2.xlsx", skiprows=5, header=None,
                       usecols=[2, 19], names=["job_raw", "worker"])
    df = select_jobs(df, (job, ))
    text = f"Подрядчики по работам {job}: \n"
    for i, w in enumerate(df["worker"].unique()):
        text += f"{i + 1}) {w}\n"

    msg = bot.send_message(msg.chat.id, text)
    send_keyboard(msg, "Чем еще могу помочь?")


# отслеживание сообщений с хештегом #работы_ (не используется)
@bot.message_handler(regexp=r"^#работы_")
def handle_message(msg):
    text = f"Вижу, {msg.from_user.first_name} {msg.from_user.last_name} постит работы {msg.text}"

    msg = bot.send_message(msg.chat.id, text=text)


bot.polling(none_stop=True)
