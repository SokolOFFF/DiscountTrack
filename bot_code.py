import telebot
import json
import sqlite3

CONFIG = json.load(open("config.json", 'r'))
bot = telebot.TeleBot(CONFIG['BOT_TOKEN'])


# TODO: write password generation function
def generate_password():
    return 'aboba'


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


# TODO: refactor bot's messages
@bot.message_handler(content_types=['text'], commands=['start', 'help'])
def handle_start_help(message):
    if message.text == "/start":
        bot.send_message(message.chat.id,
                         text="hi, {0.first_name}!\ni'm <b>{1.first_name}</b>\ni hope i can help you somehow. ❤️".format(
                             message.from_user, bot.get_me()), parse_mode='HTML')
        password = generate_password()
        bot.send_message(message.chat.id, text=f"remember: use your telegram id and auto-generated password to login "
                                               f"to our site:\nid: <b><i>{message.chat.id}</i></b> password: <b><i>{password}</i></b>",
                         parse_mode='HTML')
        add_new_user(message.chat.id, password)
    if message.text == "/help":
        bot.send_message(message.chat.id,
                         text="i can help you with a lot of things! type '/commands' to see all commands or use "
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
def handle_commands(message):
    msg = bot.send_message(message.chat.id,
                           text='okay! send me links for this product and name of product in the following '
                                'format:\n\n*product name*\n*shop name* *link to product*\n*shop name* *link to '
                                'product*\netc...')
    bot.register_next_step_handler(msg, receive_product_links)


# TODO: implement
def parse_links(text):
    pass


def receive_product_links(message):
    if message.text == '/exit':
        bot.send_message(message.chat.id, text='okay, got you!')
        return

    if parse_links(message.text):
        bot.send_message(message.chat.id, text='okay, i added this!')
    else:
        msg = bot.send_message(message.chat.id,
                               text='sorry, got some problems. please, check your input or type /exit to reset adding')
        bot.register_next_step_handler(msg, receive_product_links)


bot.polling(none_stop=True)
