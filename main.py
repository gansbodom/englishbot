import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
import random
from create_db2 import *

TOKEN = '6515278611:AAFtXWXvJtpUQvyRpbACYcPeVv9eH37CsSs'
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

userStep = {}
buttons = []


class Commands:
    ADD_WORD = 'Добавить слово➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_word = State()
    added_word = State()# Добавляемое слово
    added_translation = State()# Перевод добавляемого слова


@bot.message_handler(commands=['cards', 'start'])
def start_bot(message):
    if not check_user(message.chat.id): #Проверяем - есть ли пользователь в БД Postgres
        add_user_to_db(message.chat.id) #Добавляем новго пользователя в таблицу USERS БД Postgres
        for w, t in words.items(): #Добавляем 4 базовых слова для пользователя
            add_word(w, t, message.chat.id)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    #получаем слова из БД
    words_dct = get_words(message.chat.id)
    print(words_dct)
    russian_word = words_dct[0]['translation']
    target_word = words_dct[0]['word']
    other_words = []
    for wrd in [1,2,3]:
        other_words.append(words_dct[wrd]['word'])

    ##russian_word = 'Мир'
    ##target_word = 'Peace'

    target_word_btn = types.KeyboardButton(target_word)
    #other_words = ['Green', 'Car', 'Hello']
    other_words_buttons = [types.KeyboardButton(word) for word in other_words]
    buttons = [target_word_btn] + other_words_buttons
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Commands.NEXT)
    add_word_btn = types.KeyboardButton(Commands.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Commands.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    bot.send_message(message.chat.id, f'Угадай слово {russian_word}', reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = russian_word
        data['other_words'] = other_words


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
    if message.text == target_word:
        bot.send_message(message.chat.id, 'Всё правильно')
        start_bot(message)

    elif message.text == Commands.NEXT:
        bot.send_message(message.chat.id, 'Следующее слово')
        start_bot(message)

    elif message.text == Commands.ADD_WORD:
        bot.send_message(message.chat.id, 'Введите слово:')
        bot.register_next_step_handler(message, new_word)

    elif message.text == Commands.DELETE_WORD:
        bot.send_message(message.chat.id, 'Удалить слово')

    else:
        bot.send_message(message.chat.id, 'Ошибка')


def new_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['added_word'] = message.text
    bot.send_message(message.chat.id, 'Введите перевод:')
    bot.register_next_step_handler(message, new_translation)


def new_translation(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['added_translation'] = message.text
    bot.send_message(message.chat.id, data['added_word'])
    bot.send_message(message.chat.id, data['added_translation'])
    add_word(data['added_word'], data['added_translation'], message.chat.id)

# @bot.message_handler(state=MyStates.added_word)
# def new_function(message):
#     bot.send_message(message.chat.id, 'Мы внутри')

# @bot.message_handler(commands=['add'])
# def add_word(message):
#     bot.send_message(message.chat.id, 'Добаfffвьте слово:')
#     bot.set_state(message.from_user.id, MyStates.added_word, message.chat.id)
#
#
# @bot.message_handler(state=MyStates.added_word)
# def addd_word(message):
#     """
#     Шаг 1. Получаем от пользователя слово, которое необходимо добавить в БД
#     """
#     bot.send_message(message.chat.id, 'Теперь введите перевод слова:')
#     bot.set_state(message.from_user.id, MyStates.added_translation, message.chat.id)
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data['added_word'] = message.text
#
#
# @bot.message_handler(state=MyStates.added_translation)
# def add_translation(message):
#     """
#     Шаг 2. Получаем от пользователя перевод слова, которое необходимо добавить в БД
#     """
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         data['added_translation'] = message.text
#         msg = ("Ready, take a look:\n<b>"
#                 f"Слово: {data['added_word']}\n"
#                 f"Перевод: {data['added_translation']}</b>")
#         bot.send_message(message.chat.id, msg, parse_mode="html")
#         bot.delete_state(message.from_user.id, message.chat.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))

if __name__ == '__main__':
    print('Bot is running')
    #bot.polling()
    bot.infinity_polling(skip_pending=True)
