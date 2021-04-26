import requests
from bs4 import BeautifulSoup
from data import db_session
from data.items import Item


def parse():
    db_session.global_init("db/database.db")
    URL = 'https://www.e-katalog.ru/list/157/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.438'
    }
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.findAll('table', class_='model-short-block')
    images = soup.findAll('div', class_='list-img h')
    comps = []
    for i in range(24):
        item = items[i]
        about = item.find('div', class_='m-s-f2 no-mobile')
       # config = item.findAll('tr', class_='conf-tr')
        prev = []
        #for el in config:
        #    confs = el.findAll('td')
        #    ab = []
        #    for c in confs:
        #        text = c.get_text()
        #        ab.append(text)
        #    prev.append(ab)
        #string = ''
        #for el in prev:
        #    string += ', '.join(el) + '/'
        mas = []
        lies = about.findAll('div')
        for div in lies:
            text = div.get_text()
            mas.append(text)
        res = ', '.join(mas)
        #res += '|' + string
        comps.append({
            'title': item.find('span', class_='u').get_text(strip=True),
            'price': item.find('div', class_='model-price-range').get_text(),
            'about': res
        })
    for i in range(24):
        comp = comps[i]
        img = images[i]
        item = Item()
        item.title = comp["title"]
        item.category = 'k13'
        price = comp["price"].split('.')
        item.price = price[0][5:14]
        #about = comp['about'].split('|,')
        item.about = comp['about']
        #about = about[1].split('/,')
        #item.about_on_page = '\n'.join(about)
        item.image = 'images' + img.find('img')['src']
        db_sess = db_session.create_session()
        db_sess.add(item)
        db_sess.commit()


def get_image():
    db_session.global_init("db/database.db")
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.category == "k13").all()
    for item in items:
        img_a = item.image
        URL = 'https://www.e-katalog.ru/jpg_zoom1{}'.format(img_a[10:])
        img = requests.get(URL)
        print(item.image)
        img_file = open('static/images/jpg{}'.format(img_a[10:]), 'wb')
        img_file.write(img.content)
        img_file.close()


parse()
get_image()
