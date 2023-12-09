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