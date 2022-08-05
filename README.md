# Инструкция по запуску:
1. Установить зависимости: pip3 install -r requirements.txt
2. Создать пустую базу данных postgres: 
	* название: transactions
	* user: postgres
	* password: 45rtFGvb
3. Создать файл cred.json с данным авторизации в Google API
4. Поменять данные для подключения к postgres файле connect.json
5. Запустить файл main.py - скрипт чтения google sheets и записи его содержимого в БД. Скрипт запустить в бесконечном цикле для регулярного обновления данных в БД
6. После завершения одного цикла работы скрипта main.py можно запустить django: python3 manage.py runserver - по ссылке http://localhost:8000 откроется страница с данными из google sheets. Опыта работы с React нет, поэтому Front-end обычный html, для обновления данных - нужно обновить страницу.
