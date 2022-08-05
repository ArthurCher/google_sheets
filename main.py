# Подключаем библиотеки

import gspread # библиотека для работы с google sheets
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd  # pandas датафрейм будет легче записать/перезаписать в БД
from sqlalchemy import create_engine # для работы с postgres из-под pandas
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Создаем класс Sheets - объект этого класса может читать google sheets, и писать содержимое в БД
class Sheets:
    def __init__(self, credentials, sheet_name):
        self.credentials = credentials  # файл для подключения к Google API
        self.sheet_name = sheet_name  # название google sheets откуда берем данные

    def get_sheets(self, name):  # метод для получения данных из google sheets и создания из него pandas датафрейма
        gc = gspread.service_account(filename=self.credentials)
        sh = gc.open(name)
        data = sh.sheet1.get()

        data_json = {'number': [], 'order_id': [], 'cost': [], 'delivery_date': [], 'cost_ruble': []}

        for item in data[1:]:
            data_json['number'].append(int(item[0]))
            data_json['order_id'].append(int(item[1]))
            data_json['cost'].append(float(item[2]))
            data_json['delivery_date'].append(item[3])
            data_json['cost_ruble'].append(self.get_exchange_rate(float(item[2])))

        df = pd.DataFrame(data_json)

        return df

    def get_exchange_rate(self, cost):  # Метод для конвертации валюты
        today = datetime.today()
        date = today.strftime('%d/%m/%Y')
        url = 'http://www.cbr.ru/scripts/XML_daily.asp'
        date_req = date
        VAL_NM_RQ = 'R01235'

        while True:
            try:
                response = requests.get(url, params={'date_req': date_req, 'VAL_NM_RQ': VAL_NM_RQ})
                break

            except:
                raise

        soup = BeautifulSoup(response.text, 'html.parser')

        exchange_rate = float(soup.find(id=VAL_NM_RQ).find('value').text.replace(',', '.'))

        return cost*exchange_rate

    def update_db(self):  # Метод записи в БД данных из google sheets
        df = self.get_sheets(self.sheet_name)

        with open('connect.json') as f:
            connect_data = json.load(f)

        while True:
            try:
                connect_address = connect_data['user']+':'+connect_data['password']+'@'+connect_data['host']+':'+connect_data['port']
                engine = create_engine('postgresql://' + connect_address + '/trans')
                df.to_sql('orders', engine, if_exists='replace', index=False)

                print('Данные обновлены')
                break

            except:
                print('База данных отсутствует')
                connection = psycopg2.connect(user=connect_data['user'],
                                              password=connect_data['password'],
                                              host=connect_data['host'],
                                              port=connect_data['port'])
                connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = connection.cursor()
                sql_create_database = 'create database trans'
                cursor.execute(sql_create_database)
                cursor.close()
                connection.close()
                print('База данных создана')
                raise


# Создаем объект класса Sheets
sheets = Sheets(credentials='cred.json', sheet_name='Копия test')

# Запускаем бесконечный цикл для обновления данных в БД
while True:
    sheets.update_db()
