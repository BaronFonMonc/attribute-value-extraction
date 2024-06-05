from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from elasticsearch import Elasticsearch
from flask import jsonify
import json
import psycopg2

import api_logic, category, product

app = Flask(__name__)
es = Elasticsearch('http://localhost:9200')

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',
                            password='1')
    return conn

def get_desync(js):
    id = js['id'] if 'id' in js else ''
    if id == '':
        return abort(400, 'Blank id for YandexGpt async get request')
    return api_logic.get_yandex_response_desync(id).json()

@app.route("/getAttributes", methods=['POST'])
def get_attributes():
    js = request.get_json()
    title = js['title'] if 'title' in js else ''
    description = js['description'] if 'description' in js else ''
    model_type = js['model_type'] if 'model_type' in js else 'yandex'
    if model_type == 'get_async':
        return get_desync(js)
    txt = ''
    if title == '' and description == '':
        return abort(400, 'At least title or description of a product should be not null')
    if title != '':
        txt += 'Оглавление: ' + title
    if description != '':
        txt += '\nОписание: ' + description
    print(txt)
    if model_type == 'yandex':
        ans = api_logic.send_yandex_sync((), txt)
        print(ans, ans.json())
        return ans.json()
    if model_type == 'async':
        ans = api_logic.send_yandex_async((), txt)
        print(ans, ans.json())
        return ans.json()
    return abort(400, 'Model type \"' + model_type + '\" is not implemented yet')

@app.route("/checkAttributes", methods=['POST'])
def check_attributes():
    js = request.get_json()
    title = js['title'] if 'title' in js else ''
    description = js['description'] if 'description' in js else ''
    attributes = js['attributes'] if 'attributes' in js else ''
    model_type = js['model_type'] if 'model_type' in js else 'yandex'
    if model_type == 'get_desync':
        return get_desync(js)
    if model_type == 'get_async':
        return get_desync(js)
    txt = ''
    if title == '' and description == '':
        return abort(400, 'At least title or description of a product should be not null')
    if title != '':
        txt += 'Оглавление: ' + title
    if description != '':
        txt += '\nОписание: ' + description
    print(txt)
    if model_type == 'yandex':
        ans = api_logic.send_yandex_sync(attributes, txt)
        print(ans, ans.json())
        return ans.json()
    if model_type == 'async':
        ans = api_logic.send_yandex_async(attributes, txt)
        print(ans, ans.json())
        return ans.json()
    return abort(400, 'Model type "' + model_type + '" is not implemented yet')

@app.route(f"/confirm/<id>", methods=['POST'])
def confirm(id):
    # TODO: Confirm to base. Set flag is valid true and to aaaaaaaaaaaah
    pass

####################################################
################# DEMONSTRATION ####################
####################################################

@app.route("/search")
def search_page():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('select categoryname from d_category;')
    cats = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('search.html', cats = cats)

@app.route("/search_query", methods=['POST'])
def search_query():
    js = request.get_json()

    cat = js['cat'] if 'cat' in js else ''
    query = js['query'] if 'query' in js else ''
    model_type = js['model_type'] if 'model_type' in js else 'yandex_all'

    if model_type == 'bert':
        atrs = ['Цвет', 'Модель']
    if model_type == 'yandex_cat':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("select distinct c.attributename from d_category a left join category_attribute b on a.id = b.categoryid left join d_attribute c on b.attributeid = c.id where a.categoryname = '" + cat + "';")
        atrs = cur.fetchall()
        atrs = [i[0] for i in atrs]
        cur.close()
        conn.close()
    if model_type == 'yandex_all':
        atrs = []
    ans = api_logic.send_yandex_sync(atrs, query)
    res = json.loads(ans.json()['result']['alternatives'][0]['message']['text'])

    for i in res:
        print(i, res[i])
        # TODO сохранять в базу нужно атрибуты и поиск.

    return res

@app.route("/search_es", methods=['POST'])
def search_es():
    js = request.get_json()

    cat = js['cat'] if 'cat' in js else ''
    attrib = js['attrib'] if 'attrib' in js else ''

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select engcategoryname from d_category where categoryname = '" + cat + "';")
    encat = cur.fetchall()
    encat = encat[0][0]
    cur.close()
    conn.close()

    body = dict()

    for i in attrib:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("select engattributename from d_attribute where attributename = '"+ i +"';")
        try:
            atrs = cur.fetchall()
            atrs = atrs[0][0]
            body[atrs] = attrib[i]
        except:
            atrs = ''
            print('Пусто')
        cur.close()
        conn.close()

    arr = [0] * len(body)
    for i in range(len(body)):
        arr[i] = dict()
        arr[i]['match'] = dict()
        arr[i]['match'][list(body.keys())[i]] = body[list(body.keys())[i]]

    result = es.search(index=encat, body={'query': {'bool': {'must': arr}}})
    ids = [int(hit['_id']) for hit in result['hits']['hits']]
    print(result)
    print(ids)
    return result


################# END OF SEARCH ####################

@app.route("/category")
def category_page():
    conn = get_db_connection()
    return render_template('admin.html', cats=category.category_get(conn))

@app.route("/category/save", methods=['POST'])
def category_save():
    js = request.get_json()
    conn = get_db_connection()

    return category.category_logic(js, conn)

@app.route("/category/get", methods=['POST'])
def get_category_table():
    #js = request.get_json()
    conn = get_db_connection()

    return jsonify(category.category_get(conn))

################# END OF CATEGORY###################

@app.route("/login")
def login_page():
    return render_template('login.html')

################# END OF LOGIN #####################

@app.route("/product")
def product_page():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('select categoryname from d_category;')
    cats = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('product.html', cats=cats)

# Get from Wildberries
@app.route("/product/get", methods=['POST'])
def get_product_page():
    js = request.get_json()
    data = product.get_info(int(js['id']))
    return jsonify(data)

@app.route("/product/save", methods=['POST'])
def save_product_page():
    js = request.get_json()
    data = product.save_product(js)
    return jsonify(data)

@app.route("/index_product", methods=['POST'])
def index_product():
    js = request.get_json()
    data = product.index_product(js, es)
    return jsonify(data)

# Get from database
@app.route("/product/get_by_id", methods=['POST'])
def get_by_id_product_page():
    js = request.get_json()
    #data = product.get_info(int(js['id']))
    return js

################ END OF PRODUCT ####################

@app.route("/queries")
def queries_page():
    return render_template('queries.html')

################# END OF QUERIES####################

if __name__ == '__main__':
    print('Starting server...')
    #print(product.get_info(212920690))
    #print(es.search(index='my_index', body={'query': {'match': {'text': 'this test'}}}))
    #es.index(index='my_index', id=2, body={'text': 'a second test'})
    #es.index(index='my_index', id=1, body={'text': 'this is a test'})
    app.run(debug=True)

