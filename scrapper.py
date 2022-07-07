import logging
import sqlite3
import urllib.request
from urllib.parse import quote

from bs4 import BeautifulSoup


def db_action(action, data=None):
    try:
        conn = sqlite3.connect('cities.db')
        cur = conn.cursor()
    except Exception as error:
        logging.error(f'Ошибка при обращении к БД: {error}')
    if action == 'read':
        sql = 'SELECT name, link, population FROM cities'
        if data is not None:
            sql += ' WHERE name LIKE "%' + str(data).lower() + '%"'
        cur.execute(sql)
        return cur.fetchall()
    elif action == 'insert':
        cur.execute("DELETE FROM cities")
        conn.commit()
        cur.executemany("INSERT INTO cities VALUES(?, ?, ?, ?);", data)
        conn.commit()
        return 1
    elif action == 'create':
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS cities(
                        cityid INT PRIMARY KEY,
                        name TEXT,
                        link TEXT,
                        population INT);
                    """)
        return 1


def get_data():
    SITE = 'https://ru.wikipedia.org'
    url = (SITE + '/wiki/' +
           quote('Городские_населённые_пункты_Московской_области'))
    try:
        response = urllib.request.urlopen(url)
        page = response.read().decode('utf-8')
    except Exception as error:
        logging.error(f'Ошибка при запросе к Вики: {error}')
    soup = BeautifulSoup(page, 'lxml')
    table1 = soup.find('tbody')
    cities = []
    q = 0
    for row in table1.find_all('tr'):
        tds = row.find_all('td')
        if len(tds) == 8:
            name_href, _, _, people = tds[1:5]
            link = SITE + name_href.find('a').get('href')
            name = str(name_href.find('a').text).lower()
            people = people.get('data-sort-value')
            record = (q, name, link, people)
            cities.append(record)
            q += 1

    try:
        db_action('insert', data=cities)
    except Exception as error:
        logging.error(f'Ошибка при заполнении таблицы: {error}')
    return cities


if __name__ == '__main__':
    get_data()
