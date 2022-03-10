"""Простенькая страница для анализа сессий пользователей чат-бота
    Если все запущено и работает, при обновлении страницы информация о пользователе добавляется.
    Программу каждый раз запускать не нужно. Ссылка на страницу открывается в консоли"""


import sqlite3
from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    connections = sqlite3.connect('ege_easy_test.db')
    cur = connections.cursor()
    que = f'SELECT * FROM user_base'
    result = (cur.execute(que).fetchall())
    data = [' ||| '.join([str(line[0])] + list(line[1:])) for line in result]
    return render_template('index.html', items=data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)


