#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
from datetime import datetime
import requests
import time
import json
import mysql.connector
import time
from mysql.connector import errorcode
from selenium import webdriver

def main():
    gryaz()

def gryaz():
    cnx = mysql.connector.connect(user='ohmygolly',password='Suiginto77',host='mriadb.cwdov9h6pdvb.us-east-2.rds.amazonaws.com',port=3306,charset='utf8')
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    # log = codecs.open('ads.csv', 'w', 'utf-16')
    # insrt = codecs.open('insrt.sql', 'w', 'utf-16')
    i = 0
    k =1480
    pagecount = 1
    query = "select id,id_avito,address,description,price_rub,price_rub_meter,price_usd,price_eur,link,upload_date,agency,current_position,prev_position from testdb.APPARTEMENTS"
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    allrows = cursor.fetchall()
    cursor_for_upd = cnx.cursor()
    cursor_for_ins = cnx.cursor()
    while  i < k:
        # page = requests.get('https://www.avito.ru/kolomna/kvartiry/prodam?p='+str(pagecount),headers = headers,verify=False,timeout = 2)
        url = 'https://www.avito.ru/kolomna/kvartiry/prodam?p='+str(pagecount)
        pagecount = pagecount + 1
        browser = webdriver.PhantomJS()
        browser.get(url)
        tree = html.fromstring(browser.page_source)
        browser.quit()
        # tree = html.fromstring(page.content)

        if i == 0:
            k = int(tree.xpath('//span[@class="breadcrumbs-link-count js-breadcrumbs-link-count"]/text()')[0].replace(" ",""))
        flats = tree.xpath('//div[contains(@class,"item item_table clearfix js-catalog-item-enum")]')
        print len(flats),pagecount
        update_row = "update testdb.APPARTEMENTS set price_RUB = %s,price_RUB_meter = %s,price_USD = %s,price_EUR = %s, current_position = %s, prev_position = %s, date_created = %s, views = %s where id_avito = %s;"
        insert_row = "insert into testdb.APPARTEMENTS (id_avito,address,price_RUB,price_RUB_meter,price_USD,price_EUR,description,link,agency,current_position,date_created,views) values (%s, %s, %s, %s, %s, %s, %s ,%s ,%s, %s,%s, %s);"
        for r in flats:
            price1 = r.xpath('.//div[contains(@class,"popup-prices")]')[0].get('data-prices')
            price2 = json.loads(price1)
            priceRUB = price2[0]['currencies']['RUB']
            priceMRUB = price2[1]['currencies']['RUB']
            priceUSD = price2[0]['currencies']['USD']
            priceEUR = price2[0]['currencies']['EUR']
            id =  str(r.get('id')).strip()
            address = r.xpath('.//p[@class="address"]/text()')[0].strip()
            description = r.xpath('.//a[@class="item-description-title-link"]/text()')[0].strip()
            try:
                vendor = r.xpath('.//a[@target="_blank"]/text()')[0].strip()
            except Exception:
                vendor = r.xpath('.//div[@class="data"]/text()')[0].strip()
            link = 'https://www.avito.ru' + r.xpath('.//a[@class="item-description-title-link"]')[0].get('href')

            views = 0
            date_created = ''

            try:
                page_stat = requests.get('https://www.avito.ru/items/stat/%s'%id[1:],headers = headers,verify=False)
                tree_stat = html.fromstring(page_stat.content)
                date_str = tree_stat.xpath('//div[@class="item-stats__date"]/strong/text()')
                v = tree_stat.xpath('//div[@class="item-stats-legend"]/strong/text()')
                views = v[0].replace(' ','')
                date_string = rus_date_to_eng(date_str[0].encode('latin1').decode('utf-8'))
                date_created = datetime.strptime(date_string,'%d %B %Y')
            except Exception as e:
                print e, "exception in date"

            # log.write("\'%s\'\t%s\t%s\t%s\t%s\t\'%s\'\t\'%s\'\t\'https://www.avito.ru%s\'\t\'%s\'\t%s\n"%(id,priceRUB,priceMRUB,priceUSD,priceEUR,address,description,link,vendor,i))

            # rows_for_update = [row for row in cursor if row[1] == id]
            # rows_for_insert = [row for row in cursor if row not in rows_for_update]
            upd_check = False
            counter = 0
            prev_pos = 0
            for row in allrows:
                if unicode(row[1]) == unicode(id):
                    upd_check = True
                    prev_pos = row[11]
            if upd_check:
                cursor_for_upd.execute(update_row,(priceRUB,priceMRUB,priceUSD,priceEUR,i,prev_pos,date_created,views,id))
            else:
                cursor_for_ins.execute(insert_row,(id,address,priceRUB,priceMRUB,priceUSD,priceEUR,description,link,vendor,i,date_created,views))
            # insrt.write("insert into testdb.APPARTEMENTS (id_avito,address,price_RUB,price_RUB_meter,price_USD,price_EUR,description,link,agency) values (\'%s\', \'%s\', %s, %s, %s, %s,\'%s\',\'https://www.avito.ru%s\',\'%s\',%s);\n"%(id,address,priceRUB,priceMRUB,priceUSD,priceEUR,description,link,vendor,i))
            i=i+1
    cnx.commit()
    cursor_for_upd.close()
    cursor_for_ins.close()
    cursor.close()
    cnx.close()
    insrt.close()
    log.close()

def rus_date_to_eng(s):
    mapping = [ (u'декабря', u'December'), (u'января', u'January'), (u'февраля', u'February'), (u'марта', u'March'), (u'апреля', u'April'),
                (u'мая', u'May'), (u'июня', u'June'), (u'июля', u'July'), (u'августа', u'August'), (u'сентября', u'September'),
                (u'октября', u'October'), (u'ноября', u'November') ]
    for r,e in mapping:
        s = s.replace(r,e)
    return s
main()
