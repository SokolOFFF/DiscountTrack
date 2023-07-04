import sqlite3
import json
from recreate_login_config import recreate_login_config
from github_functions import git_push_data

CONFIG = json.load(open("config.json", 'r'))


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
        recreate_login_config()
        git_push_data()


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


def add_new_product(tg_id, shop, link, product_name):
    id = get_last_id() + 1
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    data = (id, tg_id, link, shop, product_name)
    cur.execute(f"""INSERT INTO product VALUES (?, ?, ?, ?, ?)""", data)
    con.commit()
    con.close()
    git_push_data()


def add_new_price(product_id, date, price):
    con = sqlite3.connect(CONFIG['DB_NAME'])
    cur = con.cursor()
    data = (product_id, date, price)
    cur.execute(f"""INSERT INTO price VALUES (?, ?, ?)""", data)
    con.commit()
    con.close()
    git_push_data()


def get_products():
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
    product_data = get_product_ids_and_shops(tg_id, product_name)
    price_data = {}
    for product in product_data:
        price_data[f'{product[0]}'] = {}
        price_data[f'{product[0]}']['shop'] = product[1]
        price_data[f'{product[0]}']['price_history'] = get_one_product_price_history(product[0])

    return price_data
