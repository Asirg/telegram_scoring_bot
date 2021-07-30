from sql import get_application, get_last_applications
from dotenv import dotenv_values, load_dotenv, set_key, find_dotenv

from telebot import types, TeleBot

from model import models

import pandas as pd
import threading
import pickle
import time
import os

bot = TeleBot(dotenv_values()['token'])

def send_applications():
    """ Функция для асинхронной проверки анкет и публикации их при необходимости """
    while True:
        update(dotenv_values()['chatid'])
        time.sleep(120)

def checkNone(string:str) -> str:
    """ Функция проверки на None """
    return "" if string is None else string

def scoring_code(id:int, model:str) -> float:
    """ Функция проверки анкеты с помощью скоринговой модели,
    и на основе результата, выдачи ей соотвествующего кода   """
    application = pd.DataFrame(get_application(id))
    pred = models[model].predict(pd.DataFrame(application))
    pred = 0 if pred < 0 else 1 if pred > 1 else pred
    for index, value in zip(range(1,6), [0.2, 0.4, 0.6, 0.8, 1]): # Присвоение кода
        if pred <= value:
            return index

def get_inline_keyboard():
    """ Функция создание inline-кнопки для принятие заявки """
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text = "Забрать заявку", callback_data="application")
    keyboard.add(button)
    return keyboard

def update(chat_id:int):
    """ Функция вывода иформации о заявках на кредит """
    with open("log", 'rb') as file:
        last_user_id = pickle.load(file)
    applications = get_last_applications()
    for user in applications:
        if not user['id'] in last_user_id:
            text =  f"Заявка: {user['id']} \n"\
                    f"Пользователь: {user['user_id']}\n"\
                    f"ИНН:  {user['social_number'] if not user['social_number'] is None else 0}\n"\
                    f"ФИО: {checkNone(user['last_name'])} {checkNone(user['first_name'])} {checkNone(user['other_name'])}\n"\
                    f"Создана: {user['created_at']}\n"\
                    f"Статус заявки: {user['status_id']}\n"\
                    f"Email: {user['email']}\n"\
                    f"Телефон: {user['phone_number']}\n"\
                    f"Новый/Повторный: {user['new_repeat']}\n"\
                    f"Код: {scoring_code(user['id'], user['new_repeat'])} \n"

            bot.send_message(chat_id, text=text, reply_markup=get_inline_keyboard())
    with open("log", 'wb') as file:
        pickle.dump([app['id'] for app in applications], file)
    print("Update")

@bot.message_handler(func = lambda x: True)
def add_comment(message):
    """ Обработка сообщений пользователя """
    if message.reply_to_message: # Добавления комментаря к заявке на кредит, если на нее был дан ответ
        reply_markup = {} if '✅' in message.reply_to_message.text else get_inline_keyboard()
        new_text = message.reply_to_message.text + f"\nКомментарий: {message.text} ({message.from_user.first_name}, {message.from_user.username})"
        bot.edit_message_text(new_text, chat_id = message.chat.id , message_id = message.reply_to_message.id, reply_markup = reply_markup)

    else: # обычные сообщения, не ответы                       
        if message.text == '/chatid': # команда на получение chat_id
            bot.reply_to(message, f"ID этого чата = {message.chat.id}")
        if message.text == '/start': # команда запуска в чате бота
            dotenv_file = find_dotenv()
            load_dotenv(dotenv_file)
            set_key(dotenv_file, "chatid", str(message.chat.id))
            bot.reply_to(message, f"Успешное подключение")
            annunciator = threading.Thread(target=send_applications)
            annunciator.start()


@bot.callback_query_handler(lambda call: True)
def callback_applications(call):
    """ Обработка callback-ов"""
    if call.data == "application": # Обработка нажания кноки "забрать заявку"
        new_text = call.message.text + f"\n✅ Заявка взята {call.from_user.first_name} ({call.from_user.username})"
        bot.edit_message_text(new_text, chat_id = call.message.chat.id , message_id = call.message.id)

if __name__ == "__main__":
    if not os.path.exists('log'): # Проверка на наличие лога с id проверенных заявок
        with open('log', 'wb') as file:
            pickle.dump([], file)

    if  dotenv_values()["chatid"] != "": # Если задан chat id, то на этот чат мы запускаем ассинхронное обновления заявок
        annunciator = threading.Thread(target=send_applications)
        annunciator.start()
    print('!!!! Start bot !!!!')
    bot.polling()