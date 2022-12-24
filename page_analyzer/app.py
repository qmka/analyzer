from flask import Flask, render_template, request, flash, url_for, redirect
from dotenv import load_dotenv
from bs4 import BeautifulSoup
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
        site_data = cur.fetchone()
        site_url = site_data[0]

        res = requests.get(site_url)
        res_code = res.status_code
        res.raise_for_status()
        res_html = res.text

        soup = BeautifulSoup(res_html, 'html.parser')

        h1_tag = (soup.find('h1'))
        title_tag = (soup.find('title'))
        meta_tag = (soup.find('meta', attrs={'name': 'description'}))
        msg = 'Отсутствует'
        h1_content = h1_tag.text if h1_tag is not None else msg
        title_content = title_tag.text if title_tag is not None else msg
        meta_content = meta_tag['content'] if meta_tag is not None else msg

        # пишем в базу
        cur = conn.cursor()
        cur.execute('INSERT INTO url_checks (url_id, created_at,'
                    'status_code, h1, title, description) '
                    'VALUES ((%s), (%s), (%s), (%s), (%s), (%s));',
                    (
                        id,
                        check_time,
                        res_code,
                        h1_content,
                        title_content,
                        meta_content
                    ))
        cur.close()

        flash('Проверка прошла успешно', 'success')

    except requests.exceptions.HTTPError:
        flash('Что-то пошло не так, попробуйте ещё раз', 'danger')
    except Exception:
        flash('Что-то пошло не так, попробуйте ещё раз', 'danger')

    return redirect(url_for('show_url', id=id))
