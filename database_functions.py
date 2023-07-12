import sqlite3
import json
from recreate_login_config import recreate_login_config
from github_functions import git_push_data

CONFIG = json.load(open("config.json", 'r'))


def get_password(id):
    """
    Function gets password of user by its id.
    :param id: id of the user.
    :return: password
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    cur.execute(f"""SELECT password FROM users WHERE id = ?""", (id,))
    ret = cur.fetchall()
    con.close()
    return ret[0][0]


def user_exists(id):
    """
    Function checks if a user is already in database.
    :param id: id of the user.
    :return: True if the user exists, False otherwise.
    """
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
    """
    Function adds new user into 'users' table.
    :param id: id of the user.
    :param password: password of the user.
    :return:
    """
    if not user_exists(id):
        con = sqlite3.connect(CONFIG['DB_NAME'])
        cur = con.cursor()
        data = (id, password)
        cur.execute(f"""INSERT INTO users VALUES (?, ?)""", data)
        con.commit()
        con.close()
        recreate_login_config()
        git_push_data()


def get_last_id():
    """
    Function gets the last id in 'product' table.
    :return: the biggest id number.
    """
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


def add_new_product(tg_id, shop, link, product_name):
    """
    Function adds new product into 'product' table.
    :param tg_id: telegram id of the user.
    :param shop: shop/market name.
    :param link: link to the product.
    :param product_name: product name provided by user.
    :return:
    """
    id = get_last_id() + 1
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    data = (id, tg_id, link, shop, product_name)
    cur.execute(f"""INSERT INTO product VALUES (?, ?, ?, ?, ?)""", data)
    con.commit()
    con.close()
    git_push_data()


def add_new_price(product_id, date, price):
    """
    Function adds new price of the product into 'price' table.
    :param product_id: id of the product.
    :param date: data of price parsing.
    :param price: latest price of the product.
    :return:
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    data = (product_id, date, price)
    cur.execute(f"""INSERT INTO price VALUES (?, ?, ?)""", data)
    con.commit()
    con.close()
    git_push_data()


def get_products():
    """
    Function gets all products from 'product' table.
    :return: data from 'products' table.
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT * FROM product""")
    data = r.fetchall()
    con.commit()
    con.close()
    if data is not None:
        return data
    else:
        return [()]


def get_last_price(product_id):
    """
    Function gets the last price of the product by its id.
    :param product_id: id of product.
    :return: latest price.
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT price FROM price WHERE product_id = {product_id} ORDER BY date LIMIT 1""")
    data = r.fetchone()
    con.commit()
    con.close()
    if data is not None:
        return data[0]
    else:
        return -1


def get_users():
    """
    Function gets all the users from 'users' table.
    :return: data from 'users' table.
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT * FROM users""")
    data = r.fetchall()
    con.commit()
    con.close()
    if data is not None:
        return data
    else:
        return -1


def get_users_products(user_id):
    """
    Function gets products of user by user's id.
    :param user_id: telegram user id.
    :return: list of products names.
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT product_name FROM product WHERE tg_id = {user_id}""")
    data = r.fetchall()
    ret = []
    for d in data:
        ret.append(d[0])
    con.commit()
    con.close()
    if data is not None:
        return ret
    else:
        return -1


def get_product_ids_and_shops(tg_id, product_name):
    """
    Function gets ids and shops of the product for curtain telegram user.
    :param tg_id: telegram user id.
    :param product_name: name of the product.
    :return: returns ids and shops names for the product.
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT id, shop FROM product WHERE tg_id = {tg_id} AND product_name = '{product_name}'""")
    data = r.fetchall()
    con.commit()
    con.close()
    if data is not None:
        return data
    else:
        return -1


def get_one_product_price_history(product_id):
    """
    Function gets the whole history of the product's prices by product id.
    :param product_id: id of the product.
    :return: history of product prices with dates and prices.
    """
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    r = cur.execute(f"""SELECT date, price FROM price WHERE product_id = {product_id} ORDER BY date""")
    data = r.fetchall()
    con.commit()
    con.close()
    if data is not None:
        return data
    else:
        return -1


def get_price_history(tg_id, product_name):
    """
    Function gets price history of the product by its name.
    :param tg_id: telegram id of the user.
    :param product_name: name of the product.
    :return: dictionary of the price history.
    """
    product_data = get_product_ids_and_shops(tg_id, product_name)
    price_data = {}
    for product in product_data:
        price_data[f'{product[0]}'] = {}
        price_data[f'{product[0]}']['shop'] = product[1]
        price_data[f'{product[0]}']['price_history'] = get_one_product_price_history(product[0])

    return price_data
