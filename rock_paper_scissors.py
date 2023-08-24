import random
import telebot
import config

bot = telebot.TeleBot(config.bot)

def result(human, computer):
    if human == computer:
        return "Ничья"
    if human == "Камень":
        return "Вы проиграли" if computer == "Бумага" else "Вы победили"
    if human == "Ножницы":
        return "Вы проиграли" if computer == "Камень" else "Вы победили"
    # human == Бумага
    return "Вы проиграли" if computer == "Ножницы" else "Вы победили"

@bot.message_handler(commands=["start", "help"])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes = telebot.types.KeyboardButton("Да")
    no = telebot.types.KeyboardButton("Нет")
    markup.add(yes)
    markup.add(no)
    bot.send_message(m.chat.id, 'Привет! Давай сыграем в "камень-ножницы-бумага"', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def answer(m):
    if m.text.lower() == "да":
        markup2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        scissors = telebot.types.KeyboardButton("Ножницы")
        rock = telebot.types.KeyboardButton("Камень")
        paper = telebot.types.KeyboardButton("Бумага")
        markup2.add(scissors)
        markup2.add(rock)
        markup2.add(paper)
        bot.send_message(m.chat.id, "Нажми на кнопку со своим вариантом", reply_markup=markup2)

    elif m.text.lower() == "нет":
        bot.send_message(m.text.id, "Жаль, приходи если захочешь поиграть")

    choice_list = ['Ножницы', 'Камень', 'Бумага']
    comp = random.choice(choice_list)
    if m.text.capitalize() in choice_list:
        bot.send_message(m.chat.id, f'Я выбрал "{comp.lower()}"')
        bot.send_message(m.chat.id, result(m.text.capitalize(), comp))


bot.polling(non_stop=True, interval=0)
