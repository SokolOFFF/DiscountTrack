import random
import telebot
import json
from parsers import wildberries_parser, sbermegamarket_parser, ozon_parser
from database_functions import add_new_product, add_new_user, user_exists, get_password

CONFIG = json.load(open("config.json", 'r'))
SHOPS = ['ozon', 'sbermarket', "wildberries"]
bot = telebot.TeleBot(CONFIG['BOT_TOKEN'])


def generate_password():
    symbols = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x',
               'c', 'v', 'b', 'n', 'm', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '?', '*', '$']
    generated = [random.choice(symbols) for i in range(23)]
    password = ""
    for symbol in generated:
        password = password + symbol
    return password


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


def check_link(shop, link):
    parser = ''
    if shop == 'sbermarket':
        parser = sbermegamarket_parser()
    if shop == 'ozon':
        parser = ozon_parser()
    if shop == 'wildberries':
        parser = wildberries_parser()

    _, price = parser.parse(link)

    if price == -1:
        return False
    return True


def parse_links(text, tg_id):
    try:
        text = text.replace('\n', ' ')
        product_name = text.split(' ')[0]
        links = text.split(' ')[1:]
        if len(links) == 0:
            return False
        for i in range(0, len(links), 2):
            bot.send_message(tg_id, text=f'checking {links[i]} link..')
            if links[i] not in SHOPS:
                bot.send_message(tg_id, text=f'{links[i]} not in shops list! ❌')
                return False

            if not check_link(links[i], links[i + 1]):
                bot.send_message(tg_id,
                                 text=f'{links[i]} link cannot be parsed. double check your input or choose other link! ❌')
                return False
            else:
                bot.send_message(tg_id, text=f'{links[i]} link is ok! ✅')

        for i in range(0, len(links), 2):
            add_new_product(tg_id, links[i], links[i + 1], product_name)

        return True

    except Exception as e:
        print('error while parsing', e)
        return False


def receive_product_links(message):
    if message.text == '/exit':
        bot.send_message(message.chat.id, text='okay, got you!')
        return

    if parse_links(message.text, message.chat.id):
        bot.send_message(message.chat.id, text='okay, i added this! ✅')
    else:
        msg = bot.send_message(message.chat.id,
                               text='sorry, got some problems. please, double check your input or type /exit to reset adding ❌')
        bot.register_next_step_handler(msg, receive_product_links)


def send_alert(tg_id, last_price, new_price, shop, product_name):
    bot.send_message(tg_id, text=f"product <b><i>{product_name}</i></b> price on {shop} changed <i>{last_price}</i> -> <i>{new_price}</i>",
                     parse_mode='HTML')


bot.polling(none_stop=True)
