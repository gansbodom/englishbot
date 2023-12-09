import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
import random
from create_db2 import *

TOKEN = '6515278611:AAFtXWXvJtpUQvyRpbACYcPeVv9eH37CsSs'
bot = telebot.TeleBot(TOKEN)

userStep = {}
buttons = []

