from flask import Flask, render_template, request, flash, url_for, redirect
from dotenv import load_dotenv
import datetime
import psycopg2
import os
import validators
import requests

# connect to Postgres DB
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True


# flask init
app = Flask(__name__)
SECRET_KEY = os.getenv('SECRET_KEY')
app.secret_key = SECRET_KEY


@app.get('/')
def index():
    return render_template(
        'index.html',
        title='Анализатор страниц'
    )


@app.post('/urls')
def urls_add():
    creation_time = datetime.datetime.now()
    incoming_form = request.form.to_dict()
    incoming_url = incoming_form['url']

    url_is_valid = validators.url(incoming_url)
    if url_is_valid and len(incoming_url) <= 255:
        cur = conn.cursor()
        cur.execute(
            'SELECT id FROM urls WHERE name=(%s);',
            (incoming_url, )
        )
        id_in_database = cur.fetchone()
        cur.close()

        if id_in_database:
            flash('Страница уже существует', 'success')
            return redirect(url_for('show_url', id=id_in_database[0]))

        cur = conn.cursor()
        cur.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s);',
            (incoming_url, creation_time)
        )
        cur.execute(
            'SELECT id FROM urls WHERE name=(%s);',
            (incoming_url, )
        )
        id_in_database = cur.fetchone()
        cur.close()
        flash('Страница добавлена', 'success')
        return redirect(url_for('show_url', id=id_in_database[0]))
    else:
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            title='Анализатор страниц'
        ), 422


@app.get('/urls')
def get_urls():
    cur = conn.cursor()
    cur.execute('SELECT urls.id, urls.name,'
                'MAX(url_checks.created_at), '
                'MAX(url_checks.status_code) '
                'FROM urls '
                'LEFT JOIN url_checks '
                'ON urls.id = url_checks.url_id '
                'GROUP BY urls.id '
                'ORDER BY urls.id ASC')
    site = cur.fetchall()
    cur.close()
    return render_template('urls.html',
                           site=site
                           )


@app.get('/urls/<int:id>')
def show_url(id):
    cur = conn.cursor()
    cur.execute('SELECT * FROM urls WHERE id=(%s);',
                (id,))
    site = cur.fetchone()
    cur.execute('SELECT * FROM url_checks WHERE url_id = (%s)'
                'ORDER BY created_at DESC;',
                (id,))
    site2 = cur.fetchall()
    cur.close()
    return render_template('show_url.html',
                           site=site,
                           site2=site2,
                           )


@app.post('/urls/<int:id>/checks')
def urls_id_checks_post(id):
    try:
        check_time = datetime.datetime.now()
        
        cur = conn.cursor()
        cur.execute('SELECT name FROM urls WHERE id=(%s);', (id,))
        # sitename = cur.fetchone()
        # print(sitename)
        # тут будет реквест
        # req = requests.get(sitename[0])

        # пишем в базу
        cur = conn.cursor()
        cur.execute('INSERT INTO url_checks (url_id, created_at) VALUES ((%s), (%s));',
                    (id, check_time))
        cur.close()

        flash('Проверка прошла успешно', 'success')
    except requests.exceptions.HTTPError:
        flash('Что-то пошло не так, попробуйте ещё раз', 'danger')
    
    return redirect(url_for('show_url', id=id))