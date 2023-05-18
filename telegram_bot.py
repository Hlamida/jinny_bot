import logging
import openai
import os
import telebot
import time

from dotenv import load_dotenv

from uii_ask import telegram_ask


load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
bot = telebot.TeleBot(os.getenv('GIN_TUR_BOT_TOKEN'))

# Логирование
if not os.path.exists('/tmp/bot_log/'):
    os.makedirs('/tmp/bot_log/')

logging.basicConfig(filename='/tmp/bot_log/log.txt',
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    )


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        'Привет!\nЯ Джин Тур-Bot\nХочешь отдохнуть в Сочи? Спроси меня: "Как?"',
    )


def generate_response(prompt):
    return telegram_ask(prompt)


# Обработчик команды /bot
@bot.message_handler(commands=['bot'])
def command_message(message):
    prompt = message.text
    response = generate_response(prompt)
    bot.reply_to(message, text=response)


# Обработчик остальных сообщений
@bot.message_handler(func=lambda _: True)
def handle_message(message):
    prompt = message.text
    response = generate_response(prompt)
    bot.send_message(chat_id=message.from_user.id, text=response)


# Запуск бота
print('Тур - Bot is working')

while True:
    try:
        bot.polling()
    except (telebot.apihelper.ApiException, ConnectionError) as e:
        logging.error(str(e))
        time.sleep(5)
        continue
