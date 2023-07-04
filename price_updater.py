import datetime
from parsers import ozon_parser, wildberries_parser, sbermegamarket_parser
from database_functions import add_new_price, get_products, get_last_price
from time import sleep
from bot_code import send_alert


def main():
    products = get_products()
    for product in products:
        id, tg_id, link, shop, product_name = product[0], product[1], product[2], product[3], product[4]

        parser = ''
        if shop == 'sbermarket':
            parser = sbermegamarket_parser()
        if shop == 'ozon':
            parser = ozon_parser()
        if shop == 'wildberries':
            parser = wildberries_parser()
        last_price = get_last_price(id)
        _, price = parser.parse(link)
        date = datetime.datetime.now().date()
        if price != -1:
            add_new_price(id, date, price)
        if last_price != -1:
            send_alert(tg_id, float(last_price), float(price), shop, product_name)


if __name__ == "__main__":
    while True:
        time = datetime.datetime.now().hour
        if time == 10:
            main()
        sleep(3600)
