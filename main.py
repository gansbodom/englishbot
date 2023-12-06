import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
import random
from create_db2 import *

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

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


@bot.message_handler(commands=['cards', 'start'])
def start_bot(message):
    add_user_to_db(message.chat.id) #Добавляем пользователя в таблицу USERS БД Postgres

    for w, t in words.items(): #Добавляем 4 базовых слова для пользователя
        add_word(w, t, message.chat.id)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    #получаем слова из БД
    words_dct = get_words(message.chat.id)
    print(words_dct)
    # russian_word = words_dct[0]['translation']
    # target_word = words_dct[0]['word']
    #other_words = []
    #for wrd in range(3):
        #other_words.append(words_dct[wrd]['word'])

    russian_word = 'Мир'
    target_word = 'Peace'

    target_word_btn = types.KeyboardButton(target_word)
    other_words = ['Green', 'Car', 'Hello']
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
    else:
        bot.send_message(message.chat.id, 'Ошибка')


if __name__ == '__main__':
    print('Bot is running')
    bot.polling()
