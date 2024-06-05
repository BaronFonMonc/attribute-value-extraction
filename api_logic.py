# -*- coding: utf-8 -*-
import requests


id_cat = 'b1gdfvvdf7m12f6bij3p'
id_model = 'bt16ivhgc3fojljfrbst'
iam_token = 't1.9euelZqKx8qUjJyUzYqMk82Xk5Cdz-3rnpWanYuTiYyNxonKz56UkZnGj5nl8_cden5M-e8ceRZg_d3z910ofEz57xx5FmD9zef1656VmozGzpeeyc_IjcmLm5SSkIqO7_zF656VmozGzpeeyc_IjcmLm5SSkIqO.3chjILvipZGkGzi5trf6v4Mzp6J6nsxa7DU0GgTWfnFAfpZYF568OfvdW_1MHLCf3zhmpiSKWhbYZ5cUEgXXDw'

full_pmt = 'Извлеки атрибуты товара в формате json из описания и оглавления продукта на маркетплейсе. В ответ выведи атрибуты товара и их значения.'
part_pmt_1 = 'Извлеки атрибуты товара в формате json из описания и оглавления продукта на маркетплейсе. В ответ выведи атрибуты товара и их значения. Выдели только следующие атрибуты: '
part_pmt_2 = 'Если данный атрибут не представлен в тексте, напиши вместо его значения "n/a".'

def get_yandex_response(pmt, txt):
    req = {
        "modelUri": "ds://" + id_model,
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": "500"
        },
        "messages": [
            {
            "role": "system",
            "text": pmt
            },
            {
            "text": txt,
            "role": "user"
            }
        ]
    }
    headers = {"Authorization" : "Bearer " + iam_token,
                       "x-folder-id": id_cat, }
    res = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers, json=req)
    return res

import requests
id_cat = 'b1gdfvvdf7m12f6bij3p'
id_model = 'bt16ivhgc3fojljfrbst'

def get_yandex_response_async(pmt, txt):
    req = {
        "modelUri": "ds://" + id_model,
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": "500"
        },
        "messages": [
            {
            "role": "system",
            "text": pmt
            },
            {
            "text": txt,
            "role": "user"
            }
        ]
    }
    headers = {"Authorization" : "Bearer " + iam_token,
                       "x-folder-id": id_cat}
    res = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
        headers=headers, json=req)
    return res

def get_yandex_response_desync(id):
    headers = {"Authorization" : "Bearer " + iam_token}
    res = requests.get("https://llm.api.cloud.yandex.net/operations/" + id,
        headers=headers)
    return res

def generate_pmt(atrs):
    if len(atrs) == 0:
        return full_pmt
    s = ", ".join(atrs)[:-2] + ".\n"
    pmt = part_pmt_1 + s + part_pmt_2
    return pmt

def send_yandex_sync(atrs, txt):
    pmt = generate_pmt(atrs)
    return get_yandex_response(pmt, txt)

def send_yandex_async(atrs, txt):
    pmt = generate_pmt(atrs)
    return get_yandex_response_async(pmt, txt)

def get_yandex_async():
    pass

def confirm_id():
    pass

if __name__ == '__main__':
    print('Starting server...')
    res = get_yandex_response("Извлеки атрибуты товара в формате json из описания и оглавления продукта на маркетплейсе. В ответ выведи атрибуты товара и их значения.",
                              "Оглавление: Ноутбук Gaming TUF F15 FX506HE-HN411 i7/RTX3050/16GB/1TB/DOS\nОписание: Игровой ноутбук ASUS TUF Gaming F15 FX506HE-HN411 обеспечивает впечатляющую производительность для игр и других задач. " +
                              "Ноутбук игровой оснащён высокопроизводительным процессором Intel Core i7-11800H, обеспечивающим высокую скорость работы и позволяющим параллельно выполнять несколько задач без задержек. " +
                              "Большого объема оперативной памяти 16 ГБ достаточно для комфортной работы ресурсоемких приложений и игр. " +
                              "Видеокарта GeForce RTX 3050 с 4 Гб видеопамяти обеспечивает широкие возможности для работы с трехмерной графикой. Для быстрой загрузки приложений, хранения важных документов и медиафайлов служит накопитель объемом 1 ТБ. " +
                              "Портативный компьютер оснащен 15.6-дюймовым антибликовым экраном. Частота обновления экрана составляет 144 Гц, что дает большое преимущество игроку в динамичных сценах. Разрешение FHD (1920x1080) гарантирует четкость каждой детали. " +
                              "Встроенная технология Adaptive-Sync предназначена для быстрой смены кадров в динамичных игровых сессиях. " +
                              "Ноутбук игровой ASUS TUF оснащен всеми необходимыми интерфейсами для эффективной работы в любых сценариях: три порта USB 3.2 Gen 1 Type-A, RJ45, порт Thunderbolt 4, HDMI-выход обеспечит подключение проектора или дополнительного монитора. " +
                              "Срок службы - двадцать четыре месяца. Операционная система не установлена, что предоставляет вам свободу выбора ОС. " +
                              "Аккумулятор емкостью 48 Вт·ч обеспечивает длительное время автономной. ASUS TUF Gaming F15 – ноутбук для работы и учебы, сочетающий в себе надежность, производительность и мобильность, благодаря чему позволяет полноценно насладиться играми и творчеством в любой точке мира. Гарантия 12 месяцев.")
    print(res, res.text, res.json(), sep='\n')