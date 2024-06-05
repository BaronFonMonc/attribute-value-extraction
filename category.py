from flask import jsonify
from flask import abort

def category_logic(js, conn):
    new_atrs = dict()

    print(js['data'])
    for i in range(0,len(js['data']),2):
        print(js['data'][i], i)
        if js['data'][i]['Category'] == 'Category name in table':
            continue
        engName = js['data'][i]['Category'].strip()
        ruName = js['data'][i+1]['Category'].strip()
        id = js['data'][i]['Id']
        engAtrs = js['data'][i]['Attributes'].split(',')
        ruAtrs = js['data'][i+1]['Attributes'].split(',')
        idAtrs = js['data'][i]['AtrId'].split(',')
        print(engName, ruName, id, engAtrs, ruAtrs, idAtrs)
        if len(engAtrs) != len(ruAtrs):

            return abort(400, 'Different amount of eng and ru attributes for category: ' + engName + "(" + ruName + ")")
        if id == '':  ## New category
            newCatId = req(conn, "insert into d_category(categoryname, engCategoryName) values ('"+ruName+"','"+engName+"') RETURNING id")
            new_atrs[engName] = []
            print('New id', newCatId)
            for j in range(len(engAtrs)):
                engAtr = engAtrs[j].strip()
                ruAtr = ruAtrs[j].strip()
                new_atrs[engName].append((ruAtr, engAtr))
                a_id = req(conn, "insert into d_attribute(attributeName, engattributeName) values ('" + ruAtr + "','" + engAtr + "') RETURNING id")
                #print(newCatId, a_id)
                req(conn,
                    "insert into category_attribute(categoryId, attributeId) values ('" + str(newCatId[0][0]) + "','" + str(a_id[0][0]) + "') RETURNING categoryId")
        else:         ## Update category
            cats = req(conn, '''
                select dc.id, da.id, dc.categoryname, dc.engcategoryname, dc.isactive as dc_isactive, 
            	   da.attributename, da.engattributename, da.isactive as da_isactive from d_category dc
                left join category_attribute ca on dc.id = ca.categoryid 
                left join d_attribute da on ca.attributeid = da.id
                where dc.id = \'''' + id + "';")
            print('Cats for id:', id, cats)
            if len(cats)>0 and (cats[0][2] != ruName or cats[0][3] != engName):
                req(conn, "Update d_category set isactive = True, categoryname = '" + ruName
                    + "', engcategoryname = '" + engName + "' where id = " + str(id), ret=False)
            for j in range(len(idAtrs)):
                new_atrs[engName] = []
                idAtr = idAtrs[j].strip()
                engAtr = engAtrs[j].strip()
                ruAtr = ruAtrs[j].strip()
                same = False
                for c in cats:
                    if str(c[1]) == str(idAtr):
                        if c[5] == ruAtr and c[6] == engAtr:
                            same = True
                            break
                        req(conn, "Update d_attribute set isactive = True, attributename = '" + ruAtr
                            + "', engattributename = '" + engAtr + "' where id = '" + str(idAtr) + "'", ret=False)
                if not same:
                    new_atrs[engName].append((ruAtr, engAtr))
                    a_id = req(conn,
                               "insert into d_attribute(attributeName, engattributeName) values ('" + ruAtr + "','" + engAtr + "') RETURNING id")
                    #print(id, a_id)
                    req(conn,
                        "insert into category_attribute(categoryId, attributeId) values ('" + str(
                            id) + "','" + str(a_id[0][0]) + "') RETURNING categoryId")
    conn.commit()
    conn.close()

    ## TODO: Вызвать индексацию по new_atrs.

    return jsonify("Saved successfully")

def req(conn, sql, ret=True):
    cur = conn.cursor()
    cur.execute(sql)
    if ret:
        ans = cur.fetchall()
    cur.close()
    #conn.close()
    if ret:
        return ans

def category_get(conn):
    cats = req(conn, '''
                    select dc.id, da.id, dc.categoryname, dc.engcategoryname, dc.isactive as dc_isactive, 
                	   da.attributename, da.engattributename, da.isactive as da_isactive from d_category dc
                    left join category_attribute ca on dc.id = ca.categoryid 
                    left join d_attribute da on ca.attributeid = da.id;
                    ''')

    _cat = dict()
    for i in cats:
        #print(i)
        #print(_cat)
        if i[4] and i[7]:
            if i[0] not in _cat:
                _cat[i[0]] = (i[2], i[3], [i[5]], [i[6]], [i[1]])
            else:
                _cat[i[0]][2].append(i[5])
                _cat[i[0]][3].append(i[6])
                _cat[i[0]][4].append(i[1])

    #rus_cat = dict()
    #en_cat = dict()
    #for i in cats:
    #    print(i)
    #    print(rus_cat, en_cat)
    #    if i[4] and i[7]:
    #        if i[2] not in rus_cat:
    #            rus_cat[i[2]] = (i[0], [i[5]], [i[1]])
    #            en_cat[i[3]] = (i[0], [i[6]], [i[1]])
    #        else:
    #            rus_cat[i[2]][1].append(i[5])
    #            rus_cat[i[2]][2].append(i[1])
    #            en_cat[i[3]][1].append(i[6])
    #            en_cat[i[3]][2].append(i[1])
    conn.close()
    print(_cat)
    return _cat