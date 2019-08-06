import requests
import sqlite3
import configparser

from bs4 import BeautifulSoup
from sqlite3 import Error
from twilio.rest import Client


def send_text(id):
    account_sid = config.get("default", "account_sid")
    auth_token = config.get("default", "auth_token")

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to=config.get("default", "to_number"),
        from_=config.get("default", "from_number"),
        body="A new dog! " + id)


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return connection


def create_table():
    sql = """ CREATE TABLE IF NOT EXISTS dogs (
        id TEXT PRIMARY KEY ON CONFLICT IGNORE,
        html TEXT NOT NULL
        );
    """
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def insert_html(html):
    img = div.find('img', alt=True)

    dog_name = img['alt']
    dog_age = div.find('div', {'class': 'field field--sex'}).text.strip()
    dog_breed = div.find('div', {'class': 'field field--breed'}).text.strip()
    dog_location = div.find('div', {
        'class': 'field field--name-field-location field--type-entity-reference field--label-hidden field__item'}).text.strip()
    dog_id = dog_name + " " + dog_age + " " + dog_breed + " " + dog_location

    sql = "INSERT INTO dogs (id,html) VALUES (?, ?)"
    cur = conn.cursor()
    cur.execute(sql, [dog_id, html])
    conn.commit()
    if cur.lastrowid > 0:
        send_text(dog_id)
    return cur.lastrowid


def fetch_website():
    url = "https://www.animalhumanesociety.org/adoption?f%5B0%5D=animal_sex%3AFemale&f%5B1%5D=animal_type%3ADog"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    return soup.findAll("div", {"class": "views-row"})


if __name__ == '__main__':
    # read config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # fetch site and get all divs with doggos
    divs = fetch_website()
    conn = create_connection(config.get("default", "db_location"))
    create_table()
    for div in divs:
        insert_html(str(div))

    conn.close()
