#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
from datetime import datetime
import requests
import time
import json
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main():
    start = time.time()
    try:
        gryaz()
    finally:
        print time.time()-start
def gryaz():

    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--window-size=1200,1100')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument("user-data-dir=selenium")
    browser = webdriver.Chrome(chrome_options=options,executable_path='/usr/bin/chromedriver')
    # browser_stat = webdriver.Chrome(chrome_options=options,executable_path='/usr/bin/chromedriver')
    cnx = mysql.connector.connect(user='pasha',password='Suiginto66',host='51.38.179.34',port=3306,charset='utf8')

    i = 0
    k =10

    pagecount = 1
    query = "select id,id_avito,address,description,price_rub,price_rub_meter,price_usd,price_eur,link,upload_date,agency,current_position,prev_position from testdb.APPARTEMENTS"
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    allrows = cursor.fetchall()
    cursor_for_upd = cnx.cursor()
    cursor_for_ins = cnx.cursor()

    while  i < k:
        url = 'https://www.avito.ru/kolomna/kvartiry/prodam?p=' + str(pagecount)
        pagecount = pagecount + 1
        browser.get(url)

        if i == 0:
            k = int(browser.find_element_by_xpath('//span[@class="breadcrumbs-link-count js-breadcrumbs-link-count"]').text.replace(" ",""))
        flats = browser.find_elements_by_xpath('//div[contains(@class,"item item_table clearfix js-catalog-item-enum")]')
        update_row = "update testdb.APPARTEMENTS set price_RUB = %s,price_RUB_meter = %s,price_USD = %s,price_EUR = %s, current_position = %s, prev_position = %s, date_created = %s, views = %s where id_avito = %s;"
        insert_row = "insert into testdb.APPARTEMENTS (id_avito,address,price_RUB,price_RUB_meter,price_USD,price_EUR,description,link,agency,current_position,date_created,views) values (%s, %s, %s, %s, %s, %s, %s ,%s ,%s, %s,%s, %s);"
        prices = [x.get_attribute('data-prices') for x in browser.find_elements_by_xpath('.//div[contains(@class,"popup-prices")]')]
        addresses = [x.text.strip() for x in browser.find_elements_by_xpath('.//p[@class="address"]')]
        descriptions = [x.text.strip() for x in browser.find_elements_by_xpath('.//a[@class="item-description-title-link"]')]
        # vendor1 = [x.text.strip() for x in browser.find_elements_by_xpath('.//a[@target="_blank"]')]
        vendor2 = [x.text.strip() for x in browser.find_elements_by_xpath('.//div[@class="data"]')]
        links = [x.get_attribute('href') for x in browser.find_elements_by_xpath('.//a[@class="item-description-title-link"]')]
        ids = [x.get_attribute('id').strip() for x in flats]
        for r in range(len(flats)):
            price1 = prices[r]
            price2 = json.loads(price1)
            priceRUB = price2[0]['currencies']['RUB']
            priceMRUB = price2[1]['currencies']['RUB']
            priceUSD = price2[0]['currencies']['USD']
            priceEUR = price2[0]['currencies']['EUR']
            id =  ids[r]
            address = addresses[r]
            description = descriptions[r]
            vendor = vendor2[r]
            link = 'https://www.avito.ru' + links[r]

            views = 0
            date_created = ''

            try:
                browser.get('https://www.avito.ru/items/stat/%s'%id[1:])
                driver.implicitly_wait(3)
                date_str = browser.find_element_by_xpath('//div[@class="item-stats__date"]/strong').text
                views = browser.find_element_by_xpath('//div[@class="item-stats-legend"]/strong').text.replace(' ','')
                # date_string = rus_date_to_eng(date_str.encode('latin1').decode('utf-8'))
                date_string = rus_date_to_eng(date_str)
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
            cnx.commit()
            i=i+1

    cursor_for_upd.close()
    cursor_for_ins.close()
    cursor.close()
    cnx.close()
    log.close()
    browser_stat.quit()
    browser.quit()

def rus_date_to_eng(s):
    mapping = [ (u'декабря', u'December'), (u'января', u'January'), (u'февраля', u'February'), (u'марта', u'March'), (u'апреля', u'April'),
                (u'мая', u'May'), (u'июня', u'June'), (u'июля', u'July'), (u'августа', u'August'), (u'сентября', u'September'),
                (u'октября', u'October'), (u'ноября', u'November') ]
    for r,e in mapping:
        s = s.replace(r,e)
    return s
main()
