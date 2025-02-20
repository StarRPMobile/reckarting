import time
from typing import Optional

import telebot as tb # Импортируем библиотеку telebot(Для бота Телеграм)
from telebot import types # Импортирует из telebot типы данных
import ultralytics # Позволяет работать и обучать нейросеть
import cv2 # Обрабатывает фотографии, визуализирует работу нейросети
import numpy # Занимается математикой
import os # Организует взаимосвязь с ОС
import sqlite3 # Реализует базу данных
import requests # Позволяет отправлять HTTP запросы на API
from googletrans import Translator # Google переводчик в коде

import log # Импортирует функции для логирования

import Settings as Sett # Импортируем настройки из файла Settings.py

log.warn(' Создатели: группа учащихся 10Б класса ГБОУ школы №1449\n Создано при поддержке Департамента образования города Москвы\n')

log.error(' Бот является частной интеллектуальной собственностью, кража данных из него наказуема законом!')


# Подключаемся к серверам Telegram
try:
    bot = tb.TeleBot(token=Sett.token)
except Exception as e:
    log.error(' Не удалось подключиться к Telegram!')
    log.error(' Ошибка: ' + str(e))
    exit()
# Создаём модель YOLO
try:
    Neuro = ultralytics.YOLO(Sett.bestptpath)
except Exception as e:
    log.error(' Не удалось создать модель нейросети!')
    log.error(' Ошибка: ' + str(e))
    exit()

try:
    translator = Translator()
except Exception as e:
    log.error(' Не удалось создать модель нейросети!')
    log.error(' Ошибка: ' + str(e))
    exit()


# Подключаем базу данных
try:
    con = sqlite3.connect('users.db', check_same_thread=False)
    cur = con.cursor()
except Exception as e:
    log.error(' Не удалось подключить базу данных!')
    log.error(' Ошибка: ' + str(e))
    exit()

log.line()
log.ok(' Telegram подключен, модель нейросети создана и исправна')
log.line()
log.ok(' Бот готов к работе!')
log.line()

scan = []
names = [['Egg', 'Яйца'], ['Tomato', 'Томаты'], ['Apple', 'Яблоко'], ['Carrot','Морковь'], ['Cabbagge','Капуста']] # Наименования классов
headers = {
	"x-rapidapi-key": "83bea0c1aemshf3acc255469d487p11e045jsn542c6a5fc5ec",
	"x-rapidapi-host": "recipe-by-api-ninjas.p.rapidapi.com"
}


# Класс для работы с изображением
def process(image_path: Optional[str]):
    """Функция используется для обработки изображения, на выход подаются данные полученные при обработке в формате: [{ClassName:Count}]

    :param image_path: Ссылка на картинку в виде текста.
    :type image_path: Optional[str]

    :return: Классы и количество объектов в них
    """
    # Загрузка изображения
    img = cv2.imread(image_path)
    log.ok('Загружено изображение ' + image_path)
    # Обработка изображения нейросетью
    results = Neuro(img, verbose=False)[0] # verbose=False отключает ненужный вывод в output
    log.ok('Изображение ' + image_path + ' успешно обработано нейросетью')
    # Классы
    classes = results.boxes.cls.cpu().numpy()
    # Все найденные классы в виде квадратиков(их координат в формате x1, y1, x2, y2)
    boxes = results.boxes.xyxy.cpu().numpy().astype(numpy.int32)
    # Подготовка словаря для группировки результатов по классам
    grouped_objects = {}

    # Рисование рамок и группировка результатов
    for class_id, box in zip(classes, boxes): # Для каждого выделенного квадратика
        # Переменные для работы
        class_name = Sett.names[int(class_id)] # Назначаем имя класса
        color = Sett.colors[int(class_id) % len(Sett.colors)]  # Выбираем цвет квадратика

        # Если имя класса ещё не объявлено в grouped_objects, то добавляем его пустым массивом
        if class_name not in grouped_objects:
            grouped_objects[class_name] = []
        # Добавляем в grouped_objects квадратик, указывая его координаты(box)
        grouped_objects[class_name].append(box)

        # Переменные хранящие в себе координаты квадратика
        x1, y1, x2, y2 = box
        # Рисование квадратика
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        # Рисование текста обозначающего имя класса
        cv2.putText(img, class_name, (x1, y1 - 8), cv2.FONT_HERSHEY_COMPLEX, 0.6, (15, 15, 15), 1)
    log.ok('Классы были успешно отрисованы')
    # Сохранение измененного изображения
    cv2.imwrite(os.path.splitext(image_path)[0] + '_yolo' + os.path.splitext(image_path)[1], img)
    # Сохранение данных в текстовый файл
    classes_name = []
    with open(os.path.splitext(image_path)[0] + '_data.txt', 'w') as file:
        for class_name, details in grouped_objects.items(): # Перебираем классы
            classes_name.append([class_name, 0])
            file.write(f"{class_name}:\n") # Записываем имя класса
            for detail in details: # Перебираем квадратики
                for i in classes_name:
                    if i[0] == class_name:
                        i[1] += 1
                file.write(f"Coordinates: ({detail[0]}, {detail[1]}, {detail[2]}, {detail[3]})\n")
    log.warn('Обработанная информация записана в файлы:')
    log.warn(f'Исходное изображение: /{image_path}')
    log.warn(f'Конечное изображение: /{os.path.splitext(image_path)[0]}_yolo{os.path.splitext(image_path)[1]}')
    log.warn(f'Данные о классах: /{os.path.splitext(image_path)[0]}_data.txt')
    return classes_name

@bot.message_handler(commands=['start']) #Функция вызывается, когда пользователь использует команду start(То есть при нажатии кнопки "Старт")
def start(message):
    #bot.delete_message(message.chat.id,message.id)
    chat_id = message.chat.id
    message_id = message.message_id-1
    for i in range(1, 50):
        # noinspection PyBroadException
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        message_id = message_id - 1
    bot.delete_message(chat_id, message.message_id)
    res = cur.execute(f"SELECT * FROM users WHERE id = \'{message.from_user.id}\'")
    if res.fetchone():
        keyboard = types.InlineKeyboardMarkup()
        key_menu = types.InlineKeyboardButton(text='Меню', callback_data='menu')
        keyboard.add(key_menu)
        bot.send_message(message.chat.id, '<b>Приветствую! Я уже знаю тебя, нажми кнопку Меню, чтобы перейти в меню!</b>', parse_mode='HTML', reply_markup=keyboard)
        return
    cur.execute(f"INSERT INTO users VALUES ('','',{message.from_user.id})")
    con.commit()
    log.ok(f'Новый пользователь: {message.from_user.first_name} {message.from_user.last_name}')
    txt = 'Приветствую! Я бот, который может подобрать рецепт из любого набора продуктов!\nЧто мне нужно для работы? Сначала пройди небольшое анкетирование, а затем уже сможем начинать'
    keyboard = types.InlineKeyboardMarkup() # Клавиатура
    key_go = types.InlineKeyboardButton(text='Заполнить анкету', callback_data='anketa_start')
    keyboard.add(key_go)
    bot.send_message(message.chat.id, txt, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'anketa_start' or call.data == 'anketa_kuxna')
def anketa_kuxna(call):
    txt = 'Расскажи о том, какую кухню ты любишь:\nВыбери среди представленных ту, которую хочешь получить'
    keyboard = types.InlineKeyboardMarkup()
    key_russian = types.InlineKeyboardButton(text='🇷🇺Русская', callback_data='russian')
    key_usa = types.InlineKeyboardButton(text='🇺🇸Американская', callback_data='usa')
    key_france = types.InlineKeyboardButton(text='🇫🇷Французская', callback_data='france')
    keyboard.add(key_russian, key_usa, key_france)
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'russian')
def russian(call):
    cur.execute(f"UPDATE users SET kuxna = 'russian' WHERE id = {call.from_user.id}")
    con.commit()
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} выбрал Русскую кухню')
    txt = 'Ты выбрал Русскую кухню, всё верно, или необходимо что-то исправить?'
    keyboard = types.InlineKeyboardMarkup()
    key_ok = types.InlineKeyboardButton(text='Всё верно', callback_data='ok_kuxna')
    key_error = types.InlineKeyboardButton(text='Исправить', callback_data='error_kuxna')
    keyboard.add(key_ok, key_error)
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'usa')
def usa(call):
    cur.execute(f"UPDATE users SET kuxna = 'usa' WHERE id = {call.from_user.id}")
    con.commit()
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} выбрал Американскую кухню')
    txt = 'Ты выбрал Американскую кухню, всё верно, или необходимо что-то исправить?'
    keyboard = types.InlineKeyboardMarkup()
    key_ok = types.InlineKeyboardButton(text='Всё верно', callback_data='ok_kuxna')
    key_error = types.InlineKeyboardButton(text='Исправить', callback_data='error_kuxna')
    keyboard.add(key_ok, key_error)
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'usa')
def usa(call):
    cur.execute(f"UPDATE users SET kuxna = 'usa' WHERE id = {call.from_user.id}")
    con.commit()
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} выбрал Американскую кухню')
    txt = 'Ты выбрал Американскую кухню, всё верно, или необходимо что-то исправить?'
    keyboard = types.InlineKeyboardMarkup()
    key_ok = types.InlineKeyboardButton(text='Всё верно', callback_data='ok_kuxna')
    key_error = types.InlineKeyboardButton(text='Исправить', callback_data='error_kuxna')
    keyboard.add(key_ok, key_error)
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'france')
def france(call):
    cur.execute(f"UPDATE users SET kuxna = 'france' WHERE id = {call.from_user.id}")
    con.commit()
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} выбрал Французскую кухню')
    txt = 'Ты выбрал Французскую кухню, всё верно, или необходимо что-то исправить?'
    keyboard = types.InlineKeyboardMarkup()
    key_ok = types.InlineKeyboardButton(text='Всё верно', callback_data='ok_kuxna')
    key_error = types.InlineKeyboardButton(text='Исправить', callback_data='error_kuxna')
    keyboard.add(key_ok, key_error)
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'ok_kuxna')
def ok_kuxna(call):
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} подтвердил выбор кухни')
    bot.edit_message_text('Отлично, раз всё окей то погнали дальше!', call.message.chat.id, call.message.message_id)
    time.sleep(1.5)
    bot.register_next_step_handler(call.message, anketa_allergia(call))

@bot.callback_query_handler(func=lambda call: call.data == 'error_kuxna')
def error_kuxna(call):
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} отменил выбор кухни')
    bot.edit_message_text('Попробуй выбрать ещё раз', call.message.chat.id, call.message.message_id)
    time.sleep(1.5)
    anketa_kuxna(call)

def anketa_allergia(call):
    res = cur.execute(f"SELECT allergia FROM users WHERE id = {call.from_user.id}")
    fetch = str(res.fetchone()[0])
    if fetch is None:
        return
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} начал заполнять аллергии')
    txt = 'На этом этапе тебе нужно будет указать все алергии, которые у тебя есть, чтобы мы могли не выдавать рецепты с этими продуктами\nВыбери те продукты, на которые у тебя аллергия\nТы выбрал:'
    keyboard = types.InlineKeyboardMarkup()
    key_orex = types.InlineKeyboardButton(text='Орехи', callback_data='allerg_orexi')
    key_moloko = types.InlineKeyboardButton(text='Молоко', callback_data='allerg_moloko')
    key_vse = types.InlineKeyboardButton(text='Всё выбрал', callback_data='allerg_vse')
    keyboard.add(key_orex, key_moloko, key_vse)
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'allerg_orexi' or call.data == 'allerg_moloko')
def allerg_all(call):
    ss = {'orexi':'Орехи', 'moloko':'Молоко'}
    txt2 = 'На этом этапе тебе нужно будет указать все алергии, которые у тебя есть, чтобы мы могли не выдавать рецепты с этими продуктами\nВыбери те продукты, на которые у тебя аллергия\nТы выбрал:'
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} выбрал аллергию {ss[call.data.split('_')[1]]}')
    allergia = cur.execute(f"SELECT allergia FROM users WHERE id = {call.from_user.id}").fetchone()[0]
    print(1)
    print(allergia)
    if not allergia.__contains__(call.data.split('_')[1]):
        allergia += call.data.split('_')[1]+' '
        print(allergia)
    else:
        print(2)
        allergia = allergia.replace(call.data.split('_')[1]+' ', '')
        print(allergia)
    print(allergia)
    time.sleep(0.5)
    cur.execute(f'UPDATE users SET allergia = \'{allergia}\' WHERE id = {call.from_user.id} ')
    con.commit()
    print(allergia.split(' '))
    for i in allergia.split(' '):
        if i:
            txt2 += str(ss[i])
    keyboard = types.InlineKeyboardMarkup()
    key_orex = types.InlineKeyboardButton(text='Орехи', callback_data='allerg_orexi')
    key_moloko = types.InlineKeyboardButton(text='Молоко', callback_data='allerg_moloko')
    key_vse = types.InlineKeyboardButton(text='Всё выбрал', callback_data='allerg_vse')
    keyboard.add(key_orex, key_moloko, key_vse)
    bot.edit_message_text(txt2, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, '', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'allerg_vse')
def allerg_vse(call):
    log.ok(f'{call.from_user.first_name} {call.from_user.last_name} завершил выбор аллергии')
    bot.edit_message_text('Аллергии были успешно выбраны, переход в меню...', call.message.chat.id, call.message.message_id)
    time.sleep(1.5)
    menu(call)

@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def menu(call):
    keyboard = types.InlineKeyboardMarkup()
    key_profile = types.InlineKeyboardButton(text='Мой профиль', callback_data='profile')
    key_scan = types.InlineKeyboardButton(text='Сканировать', callback_data='scan')
    keyboard.add(key_profile, key_scan)
    bot.edit_message_text(f'<b>Это основное меню бота</b>\nЧтобы отсканировать продукты жми "Сканировать"', call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'profile')
def profile(call):
    ss = {'orexi': 'Орехи', 'moloko': 'Молоко'}
    kuxna = {'russian': 'Русская', 'usa':'Американская', 'france':'Французская'}
    keyboard = types.InlineKeyboardMarkup()
    key_menu = types.InlineKeyboardButton(text='Меню', callback_data='menu')
    key_kuxna = types.InlineKeyboardButton(text='Заполнить заново', callback_data='anketa_kuxna')
    keyboard.add(key_menu, key_kuxna)
    res = cur.execute(f"SELECT kuxna, allergia FROM users WHERE id = {call.from_user.id}")
    fetch = tuple(res.fetchone())
    bot.edit_message_text(f'<b>Ваш профиль:</b>\n'
                          f'Кухня: {kuxna[fetch[0]]}\n'
                          f'Аллергии: {str([ss[a] for a in fetch[1].split()])}'
                          , call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'scan')
def scaned(call):
    keyboard = types.InlineKeyboardMarkup()
    key_gotovo = types.InlineKeyboardButton(text='Готово', callback_data='gotovo')
    keyboard.add(key_gotovo)
    bot.edit_message_text(f'Твоя задача теперь:\nОтправь фото через стандартный функционал Telegram, после того как отправишь все фото - нажми кнопку \"Готово\"', call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    scan.append(call.from_user.id)

@bot.message_handler(content_types=['photo'])
def image(msg):
    if not scan.__contains__(msg.from_user.id):
        return
    log.ok('Фото от пользователя')
    file_info = bot.get_file(msg.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'img/' + msg.photo[-1].file_id + '.jpg'
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    classes_name = process(src)
    msgtxt = 'Я определил такие продукты:\n'
    print(classes_name)
    for i in classes_name:
        print(i)
        for x in names:
            print(x)
            if x[1] == i[0]:
                print(22)
                msgtxt += f"{x[1]}: {i[1]}\n"
    print(msgtxt)
    bot.send_message(msg.chat.id, msgtxt)
    msgtxt = 'Предлагаю тебе следующие рецепты:\n'
    response = requests.get("https://recipe-by-api-ninjas.p.rapidapi.com/v1/recipe", headers=headers, params={"query": "Borsh", "offset": "1"})
    js = response.json()
    print(js)
    if len(js) > 3:
        js = js[0:4]
    for i in js:
        print(i['title'])
        translation = translator.translate(i['title'], dest="ru")
        msgtxt += '<b>' + translation.text + ':</b>\n'
        translation = translator.translate(i['ingredients'], dest="ru")
        msgtxt += '<b>Ингредиенты:</b> \n' + translation.text + '\n'
        translation = translator.translate(i['servings'], dest="ru")
        msgtxt += '<b>Количество порций:</b> \n' + translation.text + '\n'
        translation = translator.translate(i['instructions'], dest="ru")
        msgtxt += '<b>Инструкция по приготовлению:</b> \n' + translation.text + '\n'
        if len(msgtxt) > 4000:
            #bot.send_message(msg.chat.id, msgtxt2, parse_mode='html')
            msgtxt = ''
            translation = translator.translate(i['title'], dest="ru")
            msgtxt += '<b>' + translation.text + ':</b>\n'
            translation = translator.translate(i['ingredients'], dest="ru")
            msgtxt += '<b>Ингредиенты:</b> \n' + translation.text + '\n'
            translation = translator.translate(i['servings'], dest="ru")
            msgtxt += '<b>Количество порций:</b> \n' + translation.text + '\n'
            translation = translator.translate(i['instructions'], dest="ru")
            msgtxt += '<b>Инструкция по приготовлению:</b> \n' + translation.text + '\n'
    #bot.send_message(msg.chat.id, msgtxt, parse_mode='html')

    bot.send_photo(msg.chat.id, types.InputFile('img/' + msg.photo[-1].file_id + '_yolo.jpg'))
    getmsg(msg)
    clearchat(msg)
    return 1


def clearchat(msg: types.Message):
    res = cur.execute(f"SELECT id FROM msg WHERE chatid = {msg.chat.id}")
    fetch = res.fetchall()
    for i in fetch:
        bot.delete_message(msg.chat.id, i[0])
    cur.execute(f"DELETE FROM msg WHERE chatid = {msg.chat.id}")
    con.commit()

@bot.message_handler()
def getmsg(msg):
    if not msg.from_user.is_bot:
        bot.delete_message(msg.chat.id, msg.message_id)

bot.polling()