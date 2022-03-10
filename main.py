"""Чат-бот в Telegram. Для запуска нужно открыть специально созданный чат @ege_easy_lite_beta_bot
    или создать свой. Тогда не забудь-те поменять TOKEN на свой"""


import random
import sqlite3
from telegram.ext import Updater, Filters, MessageHandler, CallbackQueryHandler
from telegram.ext import CommandHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


TOKEN = '1855585764:AAGehI9Dd0rx90vXnR5E9W9nF9q2DG3o4NM'
USER_BASE = {}
ANSWER = ''
N_EXAMPLE = ''
# Этапы/состояния разговора
FIRST, SECOND, THIRD, FOURTH = range(4)
# Данные обратного вызова
ONE, TWO, THREE, END = range(4)


def start(update, context):
    # Стартовый диалог. Автоматически запоминает пользователя и добавляет его в словарь.
    USER_BASE[update.message.from_user.name] = [str(update.message.date)]
    keyboard = [
        [
            InlineKeyboardButton("🎞 Видео", callback_data=str(ONE)),
            InlineKeyboardButton("🏋️Задание‍", callback_data=str(TWO))

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"Приветствую, {update.message.from_user.first_name}! "
        f"Я бот-помощник для подготовки к ЕГЭ по информатике! 🦾 \n"
        f"Я могу посоветовать видео-разбор одной из задач или дать "
        f"упражнение на тренировку.\n"
        f"Выберите на клавиатуре, что вы сейчас хотите 👇", reply_markup=reply_markup)

    return FIRST


def stop(update, context):
    # Принудительный выход из диалога по команде /stop.
    # После выполнения сохраняет в базу данных информацию о сессии пользователя
    update.message.reply_text(f'🖖 Всего доброго, {update.message.from_user.first_name}! \n'
                              f'Если снова захочешь поговорить нажми или напиши /start')

    connections = sqlite3.connect('ege_easy_test.db')
    cur = connections.cursor()
    name = str(update.message.from_user.name)
    date = USER_BASE[update.message.from_user.name][0]
    other = '; '.join(USER_BASE[update.message.from_user.name][1:])
    new_que = f"""INSERT INTO user_base(user_name, date_time, other)
              VALUES(?, ?, ?) """
    cur.execute(new_que, (name, date, other,))
    connections.commit()
    connections.close()

    return ConversationHandler.END


def end(update, context):
    # Плановый выход из диалога по кнопке "Хватит".
    # После выполнения сохраняет в базу данных информацию о сессии пользователя
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'🖖 Всего доброго, {query.from_user.first_name}! \n'
                                 f'Если снова захочешь поговорить нажми или напиши /start')

    connections = sqlite3.connect('ege_easy_test.db')
    cur = connections.cursor()
    name = str(query.from_user.name)
    date = USER_BASE[query.from_user.name][0]
    other = '; '.join(USER_BASE[query.from_user.name][1:])
    new_que = f"""INSERT INTO user_base(user_name, date_time, other)
                  VALUES(?, ?, ?) """
    cur.execute(new_que, (name, date, other,))
    connections.commit()
    connections.close()

    return ConversationHandler.END


def run_video(update, context):
    # Кнопка "видео"
    query = update.callback_query
    query.answer()
    query.edit_message_text('Напишите числом номер задания, '
                            'видео которого вы хотите посмотреть')
    return FOURTH


def video(update, context):
    # Возвращает видео из базы данных по введенному номеру из ЕГЭ
    connections = sqlite3.connect('ege_easy_test.db')
    cur = connections.cursor()
    number_lesson = update.message.text.strip().replace('№', '')
    USER_BASE[update.message.from_user.name] += [f'Просмотрено видео №{number_lesson}']
    if number_lesson in [str(i) for i in range(1, 28)]:
        que = f'SELECT * FROM lessons where id = {number_lesson}'
        result = random.choice(cur.execute(que).fetchall())
        comment = ['Отличный выбор! 👍', 'Мне тоже нравиться это видео! 😻',
                   'Думаю, вам это пригодиться! ✍', 'Такое не грех и два раза посмотреть 👌',
                   'Рекомендую повторять за видео! ✍✍✍']
        update.message.reply_text(f'*{number_lesson}. {result[1]}*. '
                                  f'\n{random.choice(comment)}',
                                  parse_mode='Markdown')
        update.message.reply_text(result[2])
    else:
        update.message.reply_text('Некорректный номер задания, '
                                  'нужно было ввести число от 1 до 27')
    keyboard = [
        [
            InlineKeyboardButton("🎞 Видео", callback_data=str(ONE)),
            InlineKeyboardButton("🏋️Задание‍", callback_data=str(TWO)),
            InlineKeyboardButton("💔 Хватит", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text="👇 Выбирайте снова 👇", reply_markup=reply_markup
    )
    return FIRST


def run_example(update, context):
    # Кнопка "задание"
    query = update.callback_query
    query.answer()
    query.edit_message_text('Напишите *числом* номер задания',
                            parse_mode='Markdown')
    return SECOND


def example(update, context):
    # Возвращает случайное задание из базы данных по введенному номеру из ЕГЭ
    global ANSWER, N_EXAMPLE
    connections = sqlite3.connect('ege_easy_test.db')
    cur = connections.cursor()
    number_example = update.message.text.strip().replace('№', '')
    if number_example in [str(i) for i in range(1, 28)]:
        N_EXAMPLE = number_example
        que = f'SELECT * FROM examples where id_example = {number_example}'
        result = random.choice(cur.execute(que).fetchall())
        text = result[2].replace('\n\n', '\n')
        update.message.reply_text(f"*Задание № {number_example}*\n {text}",
                                  parse_mode='Markdown')
        if result[3] != 'нет':
            if number_example in ['9', '10', '18', '24', '26', '27']:
                if number_example == '27':
                    update.message.reply_text(f'Ссылка на *файл A*: {result[3].split()[0]}\n'
                                              f'Ссылка на *файл B*: {result[3].split()[1]}',
                                              parse_mode='Markdown')
                else:
                    update.message.reply_text(f'Ссылка на *файл*: {result[3]}',
                                              parse_mode='Markdown')
            else:
                context.bot.send_photo(update.message.chat_id, result[3])
        ANSWER = ' '.join(result[4].split())
        update.message.reply_text(f"✍ Напишите *ответ* на задание. "
                                  f"Если ответов несколько, укажите их через *пробел*",
                                  parse_mode='Markdown')
        return THIRD
    else:
        update.message.reply_text('❌ Некорректный номер задания, '
                                  'нужно было ввести число от 1 до 27')


def answer(update, context):
    # Проверяет ответ на задание
    global ANSWER, N_EXAMPLE
    if update.message.text.strip() == ANSWER:
        update.message.reply_text(f'🧐 Правильно, ответ: {ANSWER}')
        USER_BASE[update.message.from_user.name] += [f'Задача №{N_EXAMPLE} +']
    else:
        update.message.reply_text(f'🚫 Неправильно, ответ: {ANSWER}')
        USER_BASE[update.message.from_user.name] += [f'Задача №{N_EXAMPLE} -']

    keyboard = [
        [
            InlineKeyboardButton("🎞 Видео", callback_data=str(ONE)),
            InlineKeyboardButton("🏋️Задание‍", callback_data=str(TWO)),
            InlineKeyboardButton("💔 Хватит", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text="👇 Выбирайте снова 👇", reply_markup=reply_markup
    )
    return FIRST


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(run_video, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(run_example, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(END) + '$')
            ],
            SECOND: [MessageHandler(Filters.text, example)],
            THIRD: [MessageHandler(Filters.text, answer)],
            FOURTH: [MessageHandler(Filters.text, video)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
