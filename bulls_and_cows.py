import telebot
from telebot import types
import config
import random
import sqlite3

bot = telebot.TeleBot(config.bot)

start_game = telebot.types.KeyboardButton("Поехали")
new_game = telebot.types.KeyboardButton("Новая игра")
stop_game = telebot.types.KeyboardButton("Стоп")


def check_number(n):
    '''
    Проверка числа на различные цифры
    :param n: число
    :return: различные цифры в числе или нет
    '''
    num_lst = [int(i) for i in str(n)]
    if len(num_lst) == len(set(num_lst)):
        return True
    return False


def generate_number():
    '''
    Генерация числа
    :return: число с различными цифрами
    '''
    num = random.randint(1023, 9876)
    if check_number(num):
        return num
    return generate_number()


def rightEnd(n, whois):
    '''
    Правильное окончание слова
    :param n: количество
    :param whois: bull or cow or move
    :return: Слово с верным окончание или False
    '''
    dec = n // 10
    one = n % 10

    if one == 1 and dec != 1:  # 1, 21, 31... 91
        if whois == "bull":
            return "бык"
        if whois == "cow":
            return "корова"
        if whois == "move":
            return "ход"

    elif 2 <= one <= 4 and dec != 1:  # [2;4], 2[2;4]... 9[2;4]
        if whois == "bull":
            return "быка"
        if whois == "cow":
            return "коровы"
        if whois == "move":
            return "хода"

    elif (5 <= one <= 9 or one == 0) or dec == 1 or (one == 0 and dec == 0):  # 0, [5;9], 1[0;9], 20, 30... 90
        if whois == "bull":
            return "быков"
        if whois == "cow":
            return "коров"
        if whois == "move":
            return "ходов"

    return False


@bot.message_handler(commands=["start"])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(start_game)
    bot.send_message(m.chat.id,
                     f'''Приветствую, {m.chat.first_name}! Это игра "Быки и коровы", если хочешь прочитать правила напиши /rules.\nЧтобы начать напиши: Поехали\nЕсли захочешь закончить игру напиши: Стоп''',
                     reply_markup=markup)


@bot.message_handler(commands=["rules"])
def rules(m):
    rules = '''Компьютер задумывает четыре различные цифры из 0,1,2,...9. Игрок делает ходы, чтобы узнать эти цифры и их порядок.
Каждый ход состоит из четырёх цифр, 0 НЕ может стоять на первом месте.
В ответ компьютер показывает число отгаданных цифр, стоящих на своих местах (число быков) и число отгаданных цифр, стоящих не на своих местах (число коров).'''
    bot.send_message(m.chat.id, rules, reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["help"])
def help(m):
    bot.send_message(m.chat.id,
                     '''Правила - /rules
Закончить текущую игру - Стоп
Начать или продолжить игру - Поехали''', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=["text"])
def main(m):
    global start_game, stop_game, new_game
    id = m.chat.id
    text = m.text.lower().strip()
    con = sqlite3.connect("bulls_and_cows.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM user WHERE id=?", (id,))
    if res.fetchone() is None:
        cur.execute("INSERT INTO user VALUES(?, ?, ?, ?)", (id, 0, 0, 0))
    res = cur.execute("SELECT number, action, counter FROM user WHERE id=?", (id,)).fetchone()
    num, action, counter = res[0], res[1], res[2]

    if text == "нет, спасибо" and not action:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(start_game)
        bot.send_message(id, "Хорошо, было приятно с тобой играть)", reply_markup=markup)

    elif text == "продолжить старую":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(new_game)
        markup.add(stop_game)
        bot.send_message(id, "Хорошо, напиши свою предположение", reply_markup=markup)

    elif text == "стоп" and action:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(start_game)
        cur.execute("UPDATE user SET number=0, action=0, counter=0 WHERE id=?", (id,))
        bot.send_message(id, "Хорошо, когда захочешь приходи", reply_markup=markup)

    # Если ранее уже была игра
    elif (text == "поехали" or text == "да, давай") and action:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        old_game = telebot.types.KeyboardButton("Продолжить старую")
        markup.add(new_game)
        markup.add(old_game)
        bot.send_message(id, "Ты хочешь создать новую игру или продолжить старую?", reply_markup=markup)

    # Создание новой игры
    elif (text == "поехали" or text == "да, давай") and not action or text == "новая игра":
        num = generate_number()
        cur.execute("UPDATE user SET number=?, action=1, counter=0 WHERE id=?", (num, id))
        # cur.execute("SELECT number FROM user WHERE id=?", (id,))
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(stop_game)
        markup.add(new_game)
        bot.send_message(id, "Я загадал число, напиши мне свое предположение", reply_markup=markup)

    # Проверка входных данных
    elif action and text.isdigit() and len(text) != 4:
        bot.send_message(id, f"Нужно 4 цифры, а у тебя {len(text)}")
    elif action and text.isdigit() and not check_number(text):
        bot.send_message(id, "Цифры не должны повторяться")

    # Пользователь угадал
    elif text == str(num) and action:
        counter = cur.execute("SELECT counter FROM user WHERE id=?", (id,)).fetchone()
        cur.execute("UPDATE user SET number=0, action=0, counter=0 WHERE id=?", (id,))
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes_game = telebot.types.KeyboardButton("Да, давай")
        no_game = telebot.types.KeyboardButton("Нет, спасибо")
        markup.add(yes_game)
        markup.add(no_game)
        bot.send_message(id, f"Вы совершенно правы, вы справились за {counter[0]+1} {rightEnd(counter[0]+1, 'move')}!)\nХотите сыграть ещё раз?", reply_markup=markup)

    # Пользователь угадывает
    elif action and text.isdigit() and len(text) == 4:
        counter = cur.execute("SELECT counter FROM user WHERE id=?", (id,)).fetchone()[0]
        cur.execute("UPDATE user SET counter=? WHERE id=?", (counter+1, id))
        string_number = str(num)
        bulls, cows = 0, 0
        for i in range(4):
            if text[i] == string_number[i]:
                bulls += 1
            elif text[i] in string_number:
                cows += 1
        bot.send_message(id, f"{bulls} {rightEnd(bulls, 'bull')}, {cows} {rightEnd(cows, 'cow')}")

    # Если введены цифры, но нет начатой игры
    elif (not action and text.isdigit()) or (text == "стоп" and not action):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(new_game)
        bot.send_message(id, "У тебя нет начатых игр", reply_markup=markup)

    else:
        bot.send_message(id, "Я тебя не понимаю, сформулируй свой запрос иначе. Если тебе нужна помощь в использовании бота, то напиши /help")
    con.commit()


bot.polling(non_stop=True, interval=0)
