import time
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class base_parser:
    def __init__(self):
        options = Options()
        self.driver = webdriver.Chrome(options=options)

    def parse(self, url):
        pass


class ozon_parser(base_parser):
    def parse(self, url: str) -> Tuple[str, int]:
        try:
            self.driver.get(url)

            price = self._parse_price(self.driver.find_element(By.CLASS_NAME, 'k1y').text)
            name = self.driver.find_element(By.CLASS_NAME, 'lm').text

            return name, price

        except Exception as ex:
            print(ex)
            return "-1", -1

        finally:
            self.driver.close()
            self.driver.quit()

    def _parse_price(self, price: str) -> int:
        price = price.rsplit(u'\u2009', 1)[0].replace(u'\u2009', '')

        return int(price)


class wildberries_parser(base_parser):
    def parse(self, url: str) -> Tuple[str, int]:
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'price-block__final-price')))

            price = self._parse_price(self.driver.find_element(By.CLASS_NAME, 'price-block__final-price').text)
            name = self.driver.find_element(By.CLASS_NAME, 'product-page__header').text

            return name, price

        except Exception as ex:
            print(ex)
            return "-1", -1

        finally:
            self.driver.close()
            self.driver.quit()

    def _parse_price(self, price: str) -> int:
        price_parts = price.rsplit(' ', 1)[0]
        merged_price = price_parts.replace(' ', '')

        return int(merged_price)


class sbermegamarket_parser(base_parser):
    def parse(self, url: str) -> Tuple[str, int]:
        try:
            self.driver.get(url=url)
            time.sleep(3)
            try:
                self.driver.find_element(By.CLASS_NAME, 'header-region-selector-view__footer-ok').click()
            except Exception as ex:
                pass
            price_div = self.driver.find_element(By.CLASS_NAME, "pdp-sales-block__price-final")
            price_div_text = price_div.text
            item_price = ''
            for i in price_div_text:
                if i == '.' or i == ',' or i.isdigit():
                    item_price += i
            item_price = item_price.replace(',', '.')
            item_price = float(item_price)
            return ' ', item_price

        except Exception as ex:
            print(ex)
            return "-1", -1

        finally:
            self.driver.close()
            self.driver.quit()


if __name__ == '__main__':
    ozon_parser_1 = ozon_parser()
    url = ''
    name, price = ozon_parser_1.parse(url)

    print(name, price)

    # wb_parser = wildberries_parser()
    # name, price = wb_parser.parse('https://www.wildberries.ru/catalog/118210975/detail.aspx')
    #
    # print(name, price)

    # sb_parser = sbermegamarket_parser()
    # name, price = sb_parser.parse(
    #     'https://sbermegamarket.ru/catalog/details/voda-mineralnaya-borjomi-gazirovannaya-v-stekle-05-l-100023379416/')
    #
    # print(price)
