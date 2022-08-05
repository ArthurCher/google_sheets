from django.shortcuts import render
import psycopg2


def index(request):
    # Подключаемся к БД postgress
    while True:
        try:
            conn = psycopg2.connect(dbname='trans', user='postgres',
                                    password='45rtFGvb', host='localhost')
            cursor = conn.cursor()
            break

        except:
            raise

    # Получаем данные из нужной таблицы
    records = []
    try:
        cursor.execute('SELECT * FROM orders')
        records = cursor.fetchall()

    except:
        raise


    # Передаем данные в шаблон
    return render(request, 'main/index.html', {'data': records})
