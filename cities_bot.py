import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from scrapper import db_action, get_data

load_dotenv()
secret_token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='main.log')


def cities(update, context):
    chat = update.effective_chat
    user_says = " ".join(context.args)
    # update.message.reply_text(user_says)
    if user_says:
        cities = db_action('read', user_says)
    else:
        cities = db_action('read')
    message = ''
    num_cities = len(cities)
    if num_cities == 0:
        message = 'Информация не найдена'
    elif num_cities == 1:
        message = (str(cities[0][0]).title() + ' (Численность ' +
                   str(cities[0][2]) + ' чел.)\n' +
                   cities[0][1])
    else:
        for i in range(num_cities):
            message += str(i+1) + '. ' + str(cities[i][0]).title() + '\n'
    context.bot.send_message(chat.id, message)


def help_me(update, context):
    chat = update.effective_chat
    texts = ['Вот несколько примеров запросов, которые я могу обработать',
             'Набери "/cities" и получишь список всех городов',
             'Набери "/cities горск" и получишь список всех городов, в которых встречается "горск"',
             'Набери "/cities Балашиха" и получишь информацию об этом городе',
             'Чтобы обновить информацию с Википедии, набери "/refresh"']
    for i in range(len(texts)):
        context.bot.send_message(chat.id, texts[i])


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/cities', '/help'],
                                  ['/start', '/refresh']],
                                 resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=(f'Привет, {name}. Ну что, поработаем? Какой город ищешь? \n' +
              'Посмотреть варианты команд можно, набрав "/help"'),
        reply_markup=button
    )


def refresh(update, context):
    chat = update.effective_chat
    cities = get_data()
    texts = ['Обновили информацию с сайта ВИКИ',
             f'Нашли инфу о {len(cities)} городах']
    for i in range(len(texts)):
        context.bot.send_message(chat.id, texts[i])


def main():
    if not(os.path.exists('cities.db')):
        try:
            db_action('create')
        except Exception as error:
            logging.error(f'Ошибка при создании БД: {error}')

    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('cities', cities))
    updater.dispatcher.add_handler(CommandHandler('refresh', refresh))
    updater.dispatcher.add_handler(CommandHandler('help', help_me))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
