#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
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
    query = "select id_avito from testdb.APPARTEMENTS"
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    allrows = cursor.fetchall()
    cursor_for_ins_flat = cnx.cursor()
    cursor_for_ins_price = cnx.cursor()

    while  i < k:
        url = 'https://www.avito.ru/kolomna/kvartiry/prodam?p=' + str(pagecount)
        pagecount = pagecount + 1
        browser.get(url)

        if i == 0:
            k = int(browser.find_element_by_xpath('//span[@class="breadcrumbs-link-count js-breadcrumbs-link-count"]').text.replace(" ",""))
        flats = browser.find_elements_by_xpath('//div[contains(@class,"item item_table clearfix js-catalog-item-enum")]')
        insert_flat = "insert into testdb.APPARTEMENTS (id_avito,address,description,link,agency,date_created) values (%s, %s, %s, %s, %s, %s);"
        insert_price = "insert into testdb.prices (id_avito,price_RUB,price_RUB_meter,price_USD,price_EUR,position,views) values (%s, %s, %s, %s, %s, %s, %s);"
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
                time.sleep(3)
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
                if unicode(row[0]) == unicode(id):
                    upd_check = True
                    break
            if not upd_check:
                cursor_for_ins_flat.execute(insert_flat,(id,address,description,link,vendor,date_created))

            cursor_for_ins_price.execute(insert_price,(id,priceRUB,priceMRUB,priceUSD,priceEUR,i,views))
            cnx.commit()
            i=i+1

    cursor_for_ins_flat.close()
    cursor_for_ins_price.close()
    cursor.close()
    cnx.close()
    browser.quit()

def rus_date_to_eng(s):
    mapping = [ (u'декабря', u'December'), (u'января', u'January'), (u'февраля', u'February'), (u'марта', u'March'), (u'апреля', u'April'),
                (u'мая', u'May'), (u'июня', u'June'), (u'июля', u'July'), (u'августа', u'August'), (u'сентября', u'September'),
                (u'октября', u'October'), (u'ноября', u'November') ]
    for r,e in mapping:
        s = s.replace(r,e)
    return s
main()
