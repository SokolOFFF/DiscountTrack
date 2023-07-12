import yaml
import json
import sqlite3
import streamlit_authenticator as stauth

CONFIG = json.load(open("config.json", 'r'))


def get_users():
    """
    Function gets all users from 'users' table.
    :return: data from the 'users' table.
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


def recreate_login_config():
    """
    Function recreates 'login_config.yaml' for streamlit site login and authorization.
    :return:
    """
    credentials = {
        'usernames':
            {}
    }

    cookie = {'expiry_days': 30,
              'key': 'some_signature_key',
              'name': 'some_cookie_name'}

    preauthorized = {}

    users = get_users()
    for user in users:
        tg_id = user[0]
        password = user[1]
        credentials['usernames'][f"{tg_id}"] = {}
        credentials['usernames'][f"{tg_id}"]['email'] = f"{tg_id}@gmail.com"
        credentials['usernames'][f"{tg_id}"]['name'] = f"user_{tg_id}"
        hashed_password = stauth.Hasher([password]).generate()
        credentials['usernames'][f"{tg_id}"]['password'] = hashed_password[0]

    config = {"credentials": credentials,
              "cookie": cookie,
              'preauthorized': preauthorized}

    with open('login_config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
