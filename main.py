import bs4
import logging
import collections
import csv
import sys
import time
import random
import re
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

sys.setrecursionlimit(10**6)

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
        'article',
        'price',
        'popularity',
        'rating',
    ),
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
    'Артикул',
    'Цена',
    'Популярность',
    'Оценка',
)

class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result = []
        self.number_of_products = 0

    def load_global_section(self, text: str):
        url = text
        res = self.session.get(url=url)
        res.raise_for_status()
        res = res.text
        soup = bs4.BeautifulSoup(res, 'lxml')
        container = soup.select_one('ul.maincatalog-list-2')
        container = container.select('li')

        for block in container:
            block = block.select_one('a')
            url = block.get('href')
            url_addition = 'https://www.sima-land.ru'
            url = url_addition + url
            logger.debug(url)
            self.load_section(url)


    def load_section(self, text: str):
        #time.sleep(random.randrange(0, 200, 1)/100)
        url = text
        res = self.session.get(url=url)
        res.raise_for_status()
        res = res.text
        soup = bs4.BeautifulSoup(res, 'lxml')
        container = soup.select_one('div.base-pagination-wrapper')
        container = container.select('a._3zocR.OqJuN')
        container = container[len(container)-1]
        self.save_result()
        self.result = []
        while container:
            letter = 0
            n = 0
            url = container.get('href')
            url_addition = 'https://www.sima-land.ru'
            url = url_addition + url
            url = url + '&c_id=22887&is_catalog=1&='
            logger.info(url)
            text = self.load_page(url)
            self.pars_page(text=text)
            return self.load_section(text=url)
        return

    def load_page(self, text: str):
        url = text
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def pars_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div._1H5dr.catalog__item')
        logger.debug(container)
        for block in container:
            self.pars_block(block=block)

    def pars_block(self, block):
        url_block = block.select_one('a._3zocR.OqJuN')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no url')
            return

        logger.debug('%s', url)


        brand_name = block.select('span._8fqc0._1bjFn._3CTRl')[1]
        if not brand_name:
            logger.error(f'no brand_name on {url}')
            return

        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        logger.debug('%s', brand_name)

        goods_name = block.select_one('span._33EfK')
        if not brand_name:
            logger.error(f'no goods_name on {url}')
            return

        goods_name = goods_name.text.strip()

        logger.debug('%s', goods_name)

        container = block.select('span._8fqc0._1bjFn._3CTRl')[0]
        if container:
            articul = container.text
            articul = re.sub("[^0-9]", "", articul)
        else:
            articul = 'Артикула нет'

        logger.debug(articul)

        if container:
            container = block.select_one('span._11vAm')
            price = container.text.strip()
            price = re.sub("[^0-9]", "", price)
            price = int(price)
        else:
            price = 'Цены нет'

        logger.debug(price)

        container = block.select_one('span._12UT7._9agj-._3CTRl')
        if container:
            popularity = container.text.strip()
            popularity = re.sub("[^0-9]", "", popularity)
            popularity = int(popularity)
        else:
            popularity = 'Отзывов нет'

        logger.debug(popularity)

        rating = None

        if popularity == 0:
            rating = 'Нет отзывов.'

        logger.debug(rating)

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
            article=articul,
            price=price,
            popularity=popularity,
            rating=rating,
        ))
        logger.debug(self.result)
        logger.debug('-' * 100)

    def save_result(self):
        path = 'C:/Users/DanKos/PycharmProjects/pythonProject12/sima-land.csv'
        with open(path, 'a') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            for item in self.result:
                writer.writerow(item)
                self.number_of_products += 1
            logger.info(f'Товаров сохранено {self.number_of_products}')

    def run(self, text: str):
        self.load_global_section(text=text)


if __name__ == '__main__':
    parser = Client()
    parser.load_section('https://www.sima-land.ru/muzhskaya-odezhda/?per-page=20&sort=price&viewtype=list&c_id=22887&is_catalog=1&=')