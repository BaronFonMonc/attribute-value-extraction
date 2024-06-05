import datetime
import requests
from flask import jsonify
import psycopg2
from elasticsearch import Elasticsearch
import api_logic
import json

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',
                            password='1')
    return conn

def get_product():
    pass

def index_product(js, es):
    conn = get_db_connection()
    id = js['id']
    ans = req(conn, "select * from d_product where id = '" + str(id) + "';")
    print(ans)
    title = ans[0][1]
    description = ans[0][2]
    txt = 'Оглавление: ' + ans[0][1] + "\nОписание: " + ans[0][2]

    ans = req(conn, "select c.attributename from d_product a left join category_attribute b on a.categoryid = b.categoryid  left join d_attribute c on b.attributeid = c.id where a.id='"+str(id)+"'")
    print(ans, ans[0])
    ans = api_logic.send_yandex_sync([i[0] for i in ans], txt)
    print(ans, ans.json())
    print(ans.json()['result']['alternatives'][0]['message']['text'])
    res = json.loads(ans.json()['result']['alternatives'][0]['message']['text'])

    body = {'title': title, 'description': description}
    for i in res:
        try:
            ans = req(conn, "select engattributename from d_attribute where attributename = '"+ i +"';")[0][0]
            body[ans] = res[i]
        except:
            print("Упал")

    cat = req(conn, "select b.engcategoryname from d_product a left join d_category b on a.categoryid = b.id where a.id = '" + str(id) + "';")[0][0]

    conn.commit()
    conn.close()

    es.index(index=cat, id=id, body=body)
    return res

def save_product(js):
    conn = get_db_connection()
    id = js['id']
    if id == "":
        id = req(conn, 'insert into d_product(title, description, imageurl, producturl, categoryid) \n' +
            "values ('" + js['name'] + "','" + js['description'] + "','"  + js['url_image'] + "','"  + get_url(int(js['url'])) + "',(select id from d_category where categoryname = '" + js['category'] + "')) \n" +
            "RETURNING id;"
        )
        print(id[0][0])
        for i in js['real_data']:
            print(i)
            req(conn, 'insert into d_old_attributes(value, attributename, productid)\n' +
                      "values ('"+i['Value']+"','"+i['Attribute']+"','"+str(id[0][0])+"') RETURNING id;")
    else:
        req(conn, '')
    conn.commit()
    conn.close()
    return id

def req(conn, sql, ret=True):
    cur = conn.cursor()
    cur.execute(sql)
    if ret:
        ans = cur.fetchall()
    cur.close()
    #conn.close()
    if ret:
        return ans

def get_url(id):
    return "https://www.wildberries.ru/catalog/" + str(id) + "/detail.aspx"

def get_info(id):
    HEADERS_FOR_DESCRIPTION = {
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.wildberries.ru",
        "Referer": "https://www.wildberries.ru/catalog/" + str(id) + "/detail.aspx",
        "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    url = wb_img_url(id)
    response = requests.get(url, headers=HEADERS_FOR_DESCRIPTION)
    data = response.json()
    return get_parsed(data)


def formate_options(data_options):
    formated_options = dict()
    for i in data_options:
        formated_options[i['name']] = str(i['value'])
    return formated_options



def get_parsed(data):
    ids, formated_options, options, grouped_options, names, descriptions, categories, root_categories = '','','','','','','',''
    ids = data['nm_id']
    if 'options' in data:
        formated_options = formate_options(data['options'])
        options = data['options']
    if 'grouped_options' in data:
        grouped_options = data['grouped_options']
    if 'imt_name' in data:
        names = data['imt_name']
    if 'description' in data:
        descriptions = data['description']
    categories = data['subj_name']
    root_categories = data['subj_root_name']
    return (ids, formated_options, names, descriptions, categories, root_categories)
    #return (ids, formated_options, options, grouped_options, names, descriptions, categories, root_categories)


# Get url by articulate
def wb_img_url(nm):
    vol = int(nm // 1e5)
    part = int(nm // 1e3)
    if (vol >= 0 and vol <= 143):
        host = "//basket-01.wb.ru"
    elif (vol >= 144 and vol <= 287):
        host = "//basket-02.wb.ru"
    elif (vol >= 288 and vol <= 431):
        host = "//basket-03.wb.ru"
    elif (vol >= 432 and vol <= 719):
        host = "//basket-04.wb.ru"
    elif (vol >= 720 and vol <= 1007):
        host = "//basket-05.wb.ru"
    elif (vol >= 1008 and vol <= 1061):
        host = "//basket-06.wb.ru"
    elif (vol >= 1062 and vol <= 1115):
        host = "//basket-07.wb.ru"
    elif (vol >= 1116 and vol <= 1169):
        host = "//basket-08.wb.ru"
    elif (vol >= 1170 and vol <= 1313):
        host = "//basket-09.wb.ru"
    elif (vol >= 1314 and vol <= 1601):
        host = "//basket-10.wb.ru"
    elif (vol >= 1602 and vol <= 1655):
        host = "//basket-11.wb.ru"
    elif (vol >= 1656 and vol <= 1919):
        host = "//basket-12.wb.ru"
    elif (vol >= 1920 and vol <= 2045):
        host = "//basket-13.wb.ru"
    elif (vol >= 2046 and vol <= 2189):
        host = "//basket-14.wb.ru"
    else:
        host = "//basket-15.wbbasket.ru"

    return "https:" + str(host) + "/vol" + str(vol) + "/part" + str(part) + "/" + str(nm) + "/info/ru/card.json"