import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import random
from create_db2 import *
from example_request import get_example

TOKEN = ''
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

buttons = []


class Commands:
    ADD_WORD = 'Добавить слово➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше⏭'
    EXAMPLE = 'Пример 🇬🇧'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_word = State()


@bot.message_handler(commands=['cards', 'start'])
def start_bot(message):
    """
    Основная функция, связывает пользователя с БД
    """
    if not check_user(message.chat.id):  # Проверяем - есть ли пользователь в БД Postgres
        add_user_to_db(message.chat.id)  # Добавляем нового пользователя в таблицу USERS БД Postgres
        for word, translation in words.items():  # Добавляем базовые слова для пользователя
            add_word(word, translation, message.chat.id)
        msg = 'Привет 👋 Давай попрактикуемся в английском языке.' \
              'У тебя есть возможность использовать тренажёр как конструктор ' \
              'и собирать свою собственную базу для обучения. Для этого' \
              ' воспрользуйся инструментами Добавить слово➕ или Удалить слово🔙. Ну что, начнём ⬇️?'
        bot.send_message(message.chat.id, msg)  # Отправляем приветственное сообщение

    markup = types.ReplyKeyboardMarkup(row_width=2)

    words_dct = get_words(message.chat.id)  # Получаем словарь с парами слово-значение из БД
    russian_word = words_dct[0]['translation']  # Выбираем одно слово для изучения, и 3 - для фона
    target_word = words_dct[0]['word']
    other_words = []
    for wrd in [1, 2, 3]:
        other_words.append(words_dct[wrd]['word'])

    target_word_btn = types.KeyboardButton(target_word)
    other_words_buttons = [types.KeyboardButton(word) for word in other_words]
    buttons = [target_word_btn] + other_words_buttons
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Commands.NEXT)
    add_word_btn = types.KeyboardButton(Commands.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Commands.DELETE_WORD)
    example_btn = types.KeyboardButton(Commands.EXAMPLE)
    buttons.extend([next_btn, add_word_btn, example_btn, delete_word_btn])

    markup.add(*buttons)

    bot.send_message(message.chat.id, f'Выбери перевод слова:\n 🇷🇺{russian_word}', reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = russian_word
        data['other_words'] = other_words


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    """
    Обрабатывает сообщения, полученные от пользователя
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        russian_word = data['translate_word']

    if message.text == target_word:
        bot.send_message(message.chat.id, f'Всё правильно👌 \n {target_word} -> {russian_word}')
        start_bot(message)

    elif message.text == Commands.ADD_WORD:
        bot.send_message(message.chat.id, 'Введите слово🇬🇧:')
        bot.register_next_step_handler(message, new_word)

    elif message.text == Commands.NEXT:
        bot.send_message(message.chat.id, 'Следующее слово')
        start_bot(message)

    elif message.text == Commands.EXAMPLE:
        bot.send_message(message.chat.id, get_example(target_word))

    elif message.text == Commands.DELETE_WORD:
        bot.send_message(message.chat.id, 'Введите слово, которое хотите удалить🇷🇺:')
        bot.register_next_step_handler(message, delete_word)

    else:
        bot.send_message(message.chat.id, 'Ошибка, попробуйте ещё раз')


def new_word(message):
    """
    Принимает от пользователя новое англ. слово
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['added_word'] = message.text
    bot.send_message(message.chat.id, 'Введите перевод🇷🇺:')
    bot.register_next_step_handler(message, new_translation)


def new_translation(message):
    """
    Принимает от пользователя перевод нового слова и добавляет пару слово-значение в БД
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['added_translation'] = message.text
    bot.send_message(message.chat.id, data['added_word'])
    bot.send_message(message.chat.id, data['added_translation'])
    add_word(data['added_word'], data['added_translation'], message.chat.id)
    words_cnt = get_words_count(message.chat.id)
    bot.send_message(message.chat.id, f'Количество изучаемых слов: {words_cnt}')
    start_bot(message)  # после добавления слова бот возвращается угадыванию слов


def delete_word(message):
    """
    Удаляет заданное слово из БД для пользователя
    Добавлена проверка на количество слов, изучаемых пользователем
    (должно быть не меньше 4-х, по количеству кнопок)
    """
    words_cnt = get_words_count(message.chat.id)
    if words_cnt > 4:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['deleted_word'] = message.text
        del_word(data['deleted_word'], message.chat.id)
    words_cnt = get_words_count(message.chat.id)
    bot.send_message(message.chat.id, f'Количество изучаемых слов: {words_cnt}')
    start_bot(message)  # после удаления слова бот возвращается угадыванию слов


if __name__ == '__main__':
    print('Bot is running')
    bot.infinity_polling(skip_pending=True)
