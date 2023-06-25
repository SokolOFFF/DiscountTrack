from bs4 import BeautifulSoup

import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def sbermegamarket_parser(url: str) -> float:
    browser = webdriver.Chrome()
    try:
        browser.get(url=url)
        price = browser.find_element(By.CLASS_NAME, "pdp-sales-block__price-final")
        a = price.text
        x = ''
        for i in a:
            if i == '.' or i == ',' or i.isdigit():
                x += i
        x = x.replace(',', '.')
        x = float(x)
        return x

    except Exception as ex:
        return -1

    finally:
        browser.close()
        browser.quit()
