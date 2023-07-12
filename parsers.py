import time
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class base_parser:
    """Parent class for parsers of all marketplaces"""
    def __init__(self):
        """Default constructor which created a web driver for selenium parser"""
        options = Options()
        self.driver = webdriver.Chrome(options=options)

    def parse(self, url):
        """Function parses a site via provided url. Should be reimplemented in each dependent class"""
        pass


class ozon_parser(base_parser):
    """Ozon market parser. Extends from base parser class"""
    def parse(self, url: str) -> Tuple[str, int]:
        """
        Reimplementation of parse function for ozon market. Parses price and name of product using provided url.
        :param url: url for the product
        :return: tuple (name, price)
        """
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
        """
        Parses price from sting to integer.
        :param price: price in string format.
        :return: price in integer format.
        """
        price = price.rsplit(u'\u2009', 1)[0].replace(u'\u2009', '')

        return int(price)


class wildberries_parser(base_parser):
    """Wildberries market parser. Extends from base parser class"""
    def parse(self, url: str) -> Tuple[str, int]:
        """
        Reimplementation of parse function for wildberries market. Parses price and name of product using provided url.
        :param url: url for the product
        :return: tuple (name, price)
        """
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
        """
        Parses price from sting to integer.
        :param price: price in string format.
        :return: price in integer format.
        """
        price_parts = price.rsplit(' ', 1)[0]
        merged_price = price_parts.replace(' ', '')

        return int(merged_price)


class sbermegamarket_parser(base_parser):
    """Sbermegamarket parser. Extends from base parser class"""
    def parse(self, url: str) -> Tuple[str, int]:
        """
        Reimplementation of parse function for sbermegamarket. Parses price and name of product using provided url.
        :param url: url for the product
        :return: tuple (name, price)
        """
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


class kazanexpress_parser(base_parser):
    """KazanExpress parser. Extends from base parser class"""
    def parse(self, url: str) -> Tuple[str, float]:
        """
        Reimplementation of parse function for kazanexpress market. Parses price and name of product using provided url.
        :param url: url for the product
        :return: tuple (name, price)
        """
        try:
            self.driver.get(url=url)
            time.sleep(5)
            prod_name = self.driver.find_element(By.XPATH, '//*[@id="product-info"]/div[1]/h1').text
            price_div = self.driver.find_element(By.XPATH, '//*[@id="product-info"]/div[2]/div[4]/div[2]/div[1]/span')
            price_div_text = price_div.text
            item_price = ''
            for i in price_div_text:
                if i == '.' or i == ',' or i.isdigit():
                    item_price += i
            item_price = item_price.replace(',', '.')
            item_price = float(item_price)
            return prod_name, item_price

        except Exception as ex:
            return "-1", -1

        finally:
            self.driver.close()
            self.driver.quit()


class yandex_market_parser(base_parser):
    """Yandex market parser. Extends from base parser class"""
    def parse(self, url: str) -> Tuple[str, float]:
        """
        Reimplementation of parse function for yandex market. Parses price and name of product using provided url.
        :param url: url for the product
        :return: tuple (name, price)
        """
        try:
            self.driver.get(url)
            time.sleep(15)
            xpath_for_name_list = ['/html/body/div[2]/div[2]/main/div[4]/div/div/div[2]/div/div/div[1]/div[1]/h1',
                                   '/html/body/div[2]/div[2]/main/div[3]/div/div/div[2]/div/div/div[1]/div[1]/h1',
                                   '/html/body/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div[1]/h1']
            prod_name = ''
            for i in range(len(xpath_for_name_list)):
                xpath = xpath_for_name_list[i]
                flag = 0   
                try:
                    prod_name = self.driver.find_element(By.XPATH, xpath).text
                except Exception as ex:
                    flag = 1
                if not flag:
                    break

            try:
                price_div = self.driver.find_element(By.XPATH, '//*[@id="cardAddButton"]/div[1]/div/div/div[1]/div/div[4]/div[1]/div/div[1]/div/h3/span[2]')
            except Exception as ex:
                price_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div[3]/div/div[3]/div[1]/div[1]/div/div/div[3]/div[2]/div/div/div[1]/span/span[1]')
            price_div_text = price_div.text
            item_price = ''
            for i in price_div_text:
                if i == '.' or i == ',' or i.isdigit():
                    item_price += i
            item_price = item_price.replace(',', '.')
            item_price = float(item_price)
            return prod_name, item_price

        except Exception as ex:
            return "-1", -1

        finally:
            self.driver.close()
            self.driver.quit()
