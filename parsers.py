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


class kazanexpress_parser(base_parser):
    def parse(self, url: str) -> Tuple[str, float]:
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
            print(ex, "aboba")
            return "-1", -1

        finally:
            self.driver.close()
            self.driver.quit()


class yandex_market_parser(base_parser):
    def parse(self, url: str) -> Tuple[str, float]:
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

    kz_url = 'https://kazanexpress.ru/product/chekhol-dlya-iphone-834902'
    kz_parser = kazanexpress_parser()
    name, price = kz_parser.parse(kz_url)
    print(name)
    print(price)
    ya_url = 'https://market.yandex.ru/product--zefir-assorti-frantsuzskii-desert-kf-kronshtadtskaia-500g/953680543?cpc=3t1aG6RGaUY2vK7_yceTtqUpp0yqAT_hWyTLT-6IYmV190r3Ak3h4XHd5LG0BmWCtKyg7jDa-lN_QaO-ZcO4M8JEKXBIJzIYaUPwB_4XFFMAYz-bmZRkK6uTfPrcRgd72g6Ru4SZ1LrqQKmiRMNN08Om8bBSWCN2z4ufX5bWABPepNYbb1_dVKXw_gmzDEMfDQGLOigr7SLD1GxUZsQZsD4mq1BoGhxeAl9f1-FLWJ8K-DLfcAtekjFcwOE1uGa1zhKXjI3e1gOKrcJ2gLRC6Q%2C%2C&from-show-uid=16885772993429145794700001&sku=101313811940&do-waremd5=akLI3xgCmvKb26Q-Y5QY0Q&sponsored=1&cpa=1'
    ya_parser = yandex_market_parser()
    name, price = ya_parser.parse(ya_url)
    print(name)
    print(price)
