import random

import telebot
import json
import sqlite3

CONFIG = json.load(open("config.json", 'r'))
SHOPS = ['ozon', 'sbermarket', "yandexmarket", "wildberries"]
bot = telebot.TeleBot(CONFIG['BOT_TOKEN'])


def generate_password():
    symbols = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x',
               'c', 'v', 'b', 'n', 'm', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '?', '*', '$']
    generated = [random.choice(symbols) for i in range(23)]
    password = ""
    for symbol in generated:
        password = password + symbol
    return password


def get_password(id):
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    cur.execute(f"""SELECT password FROM users WHERE id = ?""", (id,))
    ret = cur.fetchall()
    con.close()
    return ret[0][0]


def user_exists(id):
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    cur.execute(f"""SELECT id FROM users WHERE id = ?""", (id,))
    ret = cur.fetchall()
    if len(ret) == 0:
        con.close()
        return False
    else:
        con.close()
        return True


def add_new_user(id, password):
    if not user_exists(id):
        con = sqlite3.connect(CONFIG['DB_NAME'])
        cur = con.cursor()
        data = (id, password)
        cur.execute(f"""INSERT INTO users VALUES (?, ?)""", data)
        con.commit()
        con.close()


@bot.message_handler(content_types=['text'], commands=['start', 'help'])
def handle_start_help(message):
    if message.text == "/start":
        bot.send_message(message.chat.id,
                         text="hi, {0.first_name}!\ni'm <b>{1.first_name}</b>\ni hope i can help you somehow. ❤️".format(
                             message.from_user, bot.get_me()), parse_mode='HTML')
        password = generate_password()
        if not user_exists(message.chat.id):
            bot.send_message(message.chat.id,
                             text=f"remember: use your telegram id and auto-generated password to login "
                                  f"to our site:\nid: <b><i>{message.chat.id}</i></b> password: <b><i>{password}</i></b>",
                             parse_mode='HTML')
        else:
            bot.send_message(message.chat.id,
                             text=f"remember: use your telegram id and auto-generated password to login "
                                  f"to our site:\nid: <b><i>{message.chat.id}</i></b> password: <b><i>{get_password(message.chat.id)}</i></b>",
                             parse_mode='HTML')
        add_new_user(message.chat.id, password)
    if message.text == "/help":
        bot.send_message(message.chat.id,
                         text="i can help you to track discounts and low prices of product you send me! type '/commands' to see all commands or use "
                              "telegram interface to get it!\n\n")


# TODO: rewrite commands list
@bot.message_handler(content_types=['text'], commands=['commands'])
def handle_commands(message):
    commands = ['🥺 /help', '🔧 /login', '👤 /show_users', '💳 /id', '🖼 /add_photo', '🪩 /get_random_photo',
                '📂 /manage_themes', '🎮 /game', '⛅ /weather', '🗓 /schedule', '🗺 /manage_locations',
                '🏖 /favourite_locations']
    text = 'here are all commands: \n'
    for command in commands:
        text = text + f'{command}\n'
    bot.send_message(message.chat.id, text=text)


@bot.message_handler(content_types=['text'], commands=['add_new_product'])
def handle_add_new_product(message):
    bot.send_message(message.chat.id,
                     text='okay! send me links for this product and name of product in the following '
                          'format:\n\n*product name*\n*shop name* *link to product*\n*shop name* *link to '
                          'product*\netc...')
    shops = ""
    for i in range(0, len(SHOPS) - 1):
        shops = shops + SHOPS[i] + ", "
    shops += SHOPS[-1]
    msg = bot.send_message(message.chat.id, text=f'use these names of shops in your message: {shops}')
    bot.register_next_step_handler(msg, receive_product_links)


def get_last_id():
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT id FROM product ORDER BY id DESC LIMIT 1""")
    last_id = r.fetchone()
    con.commit()
    con.close()
    if last_id is not None:
        return last_id[0]
    else:
        return 0


# TODO: implement
def check_link(link):
    return True


def parse_links(text, tg_id):
    try:
        text = text.replace('\n', ' ')
        product_name = text.split(' ')[0]
        links = text.split(' ')[1:]
        for i in range(0, len(links), 2):
            if links[i] not in SHOPS:
                return False
            if not check_link(links[i + 1]):
                return False

        for i in range(0, len(links), 2):
            con = sqlite3.connect(CONFIG['DB_NAME'])
            cur = con.cursor()
            data = (links[i + 1], links[i], product_name)
            cur.execute(f"""INSERT INTO product VALUES ({get_last_id() + 1}, {tg_id}, ?, ?, ?)""", data)
            con.commit()
            con.close()
        return True

    except Exception as e:
        print('error while parsing', e)
        return False


def receive_product_links(message):
    if message.text == '/exit':
        bot.send_message(message.chat.id, text='okay, got you!')
        return

    if parse_links(message.text, message.chat.id):
        bot.send_message(message.chat.id, text='okay, i added this!')
    else:
        msg = bot.send_message(message.chat.id,
                               text='sorry, got some problems. please, check your input or type /exit to reset adding')
        bot.register_next_step_handler(msg, receive_product_links)


bot.polling(none_stop=True)
