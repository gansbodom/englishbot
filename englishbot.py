import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup


print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = '1693269053:AAFz2VNZhzKQHQA8laNCH3B0TLpz4QQdLWg'
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, "Первичная инициализация БД слов")
        bot.send_message(cid, "Hello, stranger, let study English...")
    else:
        bot.send_message(message.chat.id,)
    markup = types.ReplyKeyboardMarkup(row_width=2)

    target_word = 'Peace'
    translate = 'Мир'
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = ['Green', 'White', 'Hello', 'Car']
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
    markup.add(*buttons)
    bot.send_message(message.chat.id, target_word, reply_markup=markup)


if __name__ == '__main__':
    print('Bot is running')
    bot.polling()

