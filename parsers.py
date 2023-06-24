from typing import Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BaseParser():
    def __init__(self):
        options = Options()
        # options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=options)

    def parse(self, url):
        pass


class OzonParser(BaseParser):
    def parse(self, url: str) -> Tuple[str, int]:
        self.driver.get(url)

        price = self._parse_price(self.driver.find_element(By.CLASS_NAME, 'k1y').text)
        name = self.driver.find_element(By.CLASS_NAME, 'lm').text

        return name, price

    def _parse_price(self, price: str) -> int:
        price = price.rsplit(u'\u2009', 1)[0].replace(u'\u2009', '')

        return int(price)


class WildberriesParser(BaseParser):
    def parse(self, url: str) -> Tuple[str, int]:
        self.driver.get(url)
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, 'price-block__final-price')))

        price = self._parse_price(self.driver.find_element(By.CLASS_NAME, 'price-block__final-price').text)
        name = self.driver.find_element(By.CLASS_NAME, 'product-page__header').text

        return name, price

    def _parse_price(self, price: str) -> int:
        price_parts = price.rsplit(' ', 1)[0]
        merged_price = price_parts.replace(' ', '')

        return int(merged_price)


if __name__ == '__main__':
    ozon_parser = OzonParser()
    name, price = ozon_parser.parse(
        'https://www.ozon.ru/product/proteinovye-batonchiki-bez-sahara-assorti-15-sht-193057362')

    print(name, price)

    wb_parser = WildberriesParser()
    name, price = wb_parser.parse('https://www.wildberries.ru/catalog/118210975/detail.aspx')

    print(name, price)