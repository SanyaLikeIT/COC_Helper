import telebot
import webbrowser
import random
from telebot import types

bot = telebot.TeleBot("7487002479:AAFc42M9QOp8cavt9yBe_eTu3dOE-GB1rTI")

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, "Hello! Here is my commands:\n/upgrade - add new improving process\n/emoji - ?")
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAENhsZni5Du8ss8dlz9hdb-MVePVm630wACERgAAv564UuysbzruCnEmzYE")

@bot.message_handler(commands=['upgrade'])
def main(message):
    if (message.from_user.id == 1196215949):
        bot.send_sticker(message.chat.id,"CAACAgIAAxkBAAENhONnijA-0zfK5_ZqI_xNbesFzVumngACQk8AAuI1WUlMknoFgnM1dDYE")
    else:
        bot.send_message(message.chat.id, "Sorry, you don't have access.")
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAENhsFni4zgRorerdq-LKWh--93tPB6MwACsxAAAmxC8UtrAl3OwiBfvzYE")

@bot.message_handler(commands=['emoji'])
def main(message):
    emoji = []

bot.infinity_polling()
