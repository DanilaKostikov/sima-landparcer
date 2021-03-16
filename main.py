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


    def load_section(self, text: str, text2: str):
        #time.sleep(random.randrange(0, 200, 1)/100)
        url_n = text
        res = self.session.get(url=url_n)
        res.raise_for_status()
        res = res.text
        soup = bs4.BeautifulSoup(res, 'lxml')
        container = soup.select_one('div.base-pagination-wrapper')
        container = container.select('a._3zocR.OqJuN')
        container_save = container
        container = container[len(container) - 1]
        for_page = container_save[len(container_save) - 2]
        n = 1
        url_for_page = for_page.get('href')
        url_for_page = url_for_page[n:]
        url_for_page = re.findall(r"\/(.*?)\/", url_for_page)
        url_for_page = url_for_page[0]
        url_for_page = url_for_page[1:]
        try:
            url_for_page = int(url_for_page)
            logger.info(url_for_page)
            url_for_page_2 = container.get('href')
            url_for_page_2 = url_for_page_2[n:]
            url_for_page_2 = re.findall(r"\/(.*?)\/", url_for_page_2)
            url_for_page_2 = url_for_page_2[0]
            url_for_page_2 = url_for_page_2[1:]
            url_for_page_2 = int(url_for_page_2)
            logging.info(url_for_page_2)
            url_for_page_2 = int(url_for_page_2)
            url = container.get('href')
            text = self.load_page(url_n)
            url_addition = 'https://www.sima-land.ru'
            url = url_addition + url
            url = re.split(r'/', url)
            url = url[0] + '//' + url[2] + '/' + url[3] + '/' + url[4] + text2
        except Exception:
            n += 29
            url_for_page = for_page.get('href')
            url_for_page = url_for_page[n:]
            url_for_page = re.findall(r"\/(.*?)\/", url_for_page)
            url_for_page = url_for_page[0]
            url_for_page = url_for_page[1:]
            url_for_page = int(url_for_page)
            logger.info(url_for_page)
            url_for_page_2 = container.get('href')
            url_for_page_2 = url_for_page_2[n:]
            url_for_page_2 = re.findall(r"\/(.*?)\/", url_for_page_2)
            url_for_page_2 = url_for_page_2[0]
            url_for_page_2 = url_for_page_2[1:]
            url_for_page_2 = int(url_for_page_2)
            logging.info(url_for_page_2)
            url_for_page_2 = int(url_for_page_2)
            url = container.get('href')
            text = self.load_page(url_n)
            url_addition = 'https://www.sima-land.ru'
            url = url_addition + url
            url = re.split(r'/', url)
            url = url[0] + '//' + url[2] + '/' + url[3] + '/' + url[4] + '/' + url[5] + text2
        logger.info(url)
        self.pars_page(text=text)
        self.save_result()
        self.result = []
        if url_for_page_2 <= url_for_page:
            return self.load_section(text=url, text2=text2)
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
        if block.select_one('span._303yR._31Oay') != None:
            return

        n = 0

        if block.select('span._8fqc0._1bjFn._3CTRl')[0].text == 'Без скидок':
            n += 1

        url_block = block.select_one('a._3zocR.OqJuN')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no url')
            return

        logger.debug('%s', url)


        brand_name = block.select('span._8fqc0._1bjFn._3CTRl')[n+1]
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

        container = block.select('span._8fqc0._1bjFn._3CTRl')[n]
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
        with open(path, 'a', encoding='utf8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            for item in self.result:
                writer.writerow(item)
                self.number_of_products += 1
            logger.info(f'Товаров сохранено {self.number_of_products}')

    def run(self, text: str):
        self.load_global_section(text=text)


if __name__ == '__main__':
    parser = Client()
    parser.load_section(
        'https://www.sima-land.ru/muzhskaya-odezhda/?per-page=20&sort=price&viewtype=list&c_id=22887&is_catalog=1&=', '/?per-page=20&sort=price&viewtype=list&c_id=22887&is_catalog=1&=')
    parser.load_section(
        'https://www.sima-land.ru/zhenskaya-odezhda/?c_id=22967&c_id=22967&is_catalog=1&per-page=20&sort=price&viewtype=list','/?c_id=22967&c_id=22967&is_catalog=1&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/odezhda-i-obuv/detskaya-odezhda/?is_catalog=1&c_id=4804&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=4804&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/igrushki/?is_catalog=1&c_id=687&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=687&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/posuda/?is_catalog=1&c_id=12&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=12&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tvorchestvo/?is_catalog=1&c_id=690&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=690&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/stroitelstvo-i-remont/?is_catalog=1&c_id=8787&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=8787&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/sad-i-ogorod/?is_catalog=1&c_id=4030&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=4030&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tekhnika-dlya-kuhni/?c_id=9027&c_id=9027&is_catalog=1&per-page=20&sort=price&viewtype=list','/?c_id=9027&c_id=9027&is_catalog=1&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/smartfony-gadzhety-i-planshety/?c_id=37234&per-page=20&sort=price&viewtype=list','/?c_id=37234&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tekhnika-dlya-doma/?c_id=18951&per-page=20&sort=price&viewtype=list','/?c_id=18951&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/bytovaya-tekhnika-i-elektronika-dlya-krasoty-i-zdorovya/?c_id=9840&per-page=20&sort=price&viewtype=list','/?c_id=9840&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/televizory-audio-i-video-tekhnika/?c_id=20446&per-page=20&sort=price&viewtype=list','/?c_id=20446&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/kompyutery-i-noutbuki/?c_id=37232&per-page=20&sort=price&viewtype=list','/?c_id=37232&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/oborudovanie-dlya-umnogo-doma/?c_id=33070&per-page=20&sort=price&viewtype=list','/?c_id=33070&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/elektronika-dlya-hobbi-i-uvlecheniya/?c_id=59692&per-page=20&sort=price&viewtype=list','/?c_id=59692&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tovary-s-lyubimymi-geroyami/?is_catalog=1&c_id=50406&per-page=20&sort=price&viewtype=list','/?is_catalog=1&c_id=50406&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/detskie-tovary-dlya-puteshestviy/?c_id=4571&c_id=4571&per-page=20&sort=price&viewtype=list','/?c_id=4571&c_id=4571&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tovary-dlya-detskogo-otdyha-na-otkrytom-vozduhe/?c_id=41531&c_id=41531&per-page=20&sort=price&viewtype=list','/?c_id=41531&c_id=41531&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/detskaya-bizhuteriya-i-galantereya/?c_id=735&c_id=735&per-page=20&sort=price&viewtype=list','/?c_id=735&c_id=735&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tovary-dlya-detskogo-kormleniya/?c_id=5117&c_id=5117&per-page=20&sort=price&viewtype=list','/?c_id=5117&c_id=5117&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/detskie-tovary-dlya-uhoda-i-gigieny/?c_id=4047&c_id=4047&per-page=20&sort=price&viewtype=list','/?c_id=4047&c_id=4047&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/detskie-tovary-dlya-prazdnika/?c_id=706&c_id=706&per-page=20&sort=price&viewtype=list','/?c_id=706&c_id=706&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/detskie-suveniry/?c_id=689&c_id=689&per-page=20&sort=price&viewtype=list','/?c_id=689&c_id=689&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tovary-dlya-detskoy-komnaty/?c_id=28367&c_id=28367&per-page=20&sort=price&viewtype=list','/?c_id=28367&c_id=28367&per-page=20&sort=price&viewtype=list')
    parser.load_section(
        'https://www.sima-land.ru/tovary-dlya-mam/?c_id=4046&c_id=4046&per-page=20&sort=price&viewtype=list','/?c_id=4046&c_id=4046&per-page=20&sort=price&viewtype=list')