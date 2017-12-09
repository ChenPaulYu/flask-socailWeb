# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:06:35 2017

@author: cure8
"""

import os
import shutil
import datetime
import requests
import pandas as pd 
from dateutil.parser import parse
import sys
import time
from selenium import webdriver

#'fanpage_name'請輸入欲爬取的粉專名稱，資料型態需使用字串
#'url'請輸入欲爬取的粉專首頁網址，資料型態需使用字串
#"daylen"請輸入欲爬取近"幾"天的文章，輸入數字即可，唯資料型態也需使用字串

def hasSelector(selector):
    try:
        driver.find_element_by_css_selector(selector)
        return True
    except:
        return False

def crawlfb(fanpage_name, url, daylen):

    #以下token為永遠權限不會到期
    #儲存路徑是設定在我自己電腦的你們可以改!
    #path = 'C:\\Users\\cure8\\Desktop\\實習資訊\\DIGI+Talent\\Team project_Code\\' + fanpage_name

    token = 'EAACRsaKtrOABANosgm3IbdMT9seNS2NtxZAuqxouZCp8oBKFW1PPD1R6qgf5wLoSvDzgrOMh2IVDV6pGopOqmy8jp4LZCre1lRIZCLU339xTV3QUW8D5cfzKke8q9oy3LaBAhjfVMuIuUDGImtz4ZCGUsyadsKlrpvP6f2VLFtgZDZD'
    global path1
    #path1 = 'C:\\Users\\cure8\\Desktop\\實習資訊\\DIGI+Talent\\Team project_Code'
    path = path1 + '\\' + fanpage_name
    
    #新增資料夾以供excel儲存
    
    if os.path.exists(path):
        shutil.rmtree(path)
        
    os.mkdir(path)

    #抓取粉專按讚人數、頭貼、封面照片

    res = requests.get('https://graph.facebook.com/v2.10/%s/posts?limit=100&access_token=%s' %(url, token))
    res = requests.get('https://graph.facebook.com/v2.10/%s/posts?limit=100&access_token=%s' %(res.json()['id'], token))

    fanpage = []
    res1 = requests.get('https://graph.facebook.com/v2.10/%s?fields=fan_count, picture, cover&access_token=%s' %(url, token))
    fanpage.append([res1.json()['fan_count'],
                    res1.json()['picture']['data']['url'],
                    res1.json()['cover']['source']
                    ])
     
    #建立空的list
    #以下為主要抓文章的code
    #開始比較輸入的時間範圍與發文日期，決定是否抓取文章
    posts = []
    comments_list = []
    page = 1
    index = 1

    today = datetime.date.today()
    print()
    print ("今天日期 => %s" %str(today))
    print()

    while 'paging' in res.json():
    
        for post in res.json()['data']:

            res2 = requests.get('https://graph.facebook.com/v2.10/%s?fields=likes.limit(0).summary(True), shares, comments.limit(100)&access_token=%s' %(post['id'], token))
        
            year = int(post['created_time'][0:4])
            month = int(post['created_time'][5:7])
            day = int(post['created_time'][8:10])
        
            other_day = datetime.date(year, month, day)
            result = today - other_day
        
            if result.days > int(daylen):
                break
            else:        
                if 'likes' in res2.json():
                    likes = res2.json()['likes']['summary'].get('total_count')
                else:
                    likes = 0
            
                if 'shares' in res2.json():
                    shares = res2.json()['shares'].get('count')
                else:
                    shares = 0
        
                posts.append([fanpage_name,
                              parse(post['created_time']), 
                              post['id'], 
                              post.get('message'), 
                              post.get('story'), 
                              likes, 
                              shares
                              ])
    
                locals()['comments_list_%s' %(index)] = []
        
                if 'comments' in res2.json():          
                    for ele in res2.json()['comments']['data']:
                        locals()['comments_list_%s' %(index)].append([ele['created_time'], ele['from']['id'], ele['from']['name'], ele['message']])
                else:
                    locals()['comments_list_%s' %(index)].append(['NO', 'NO', 'NO', 'NO'])
                    
                print('目前已抓取了第%d頁第%d篇文章，日期是：%s，距離現在%d天' % (page, index, post['created_time'], result.days))
        
            index = index + 1    

        if 'next' in res.json()['paging']:
            res = requests.get(res.json()['paging']['next'])
            page += 1
        else:
            break
    
    print()    
    print('抓取結束!')

    #檔案輸出

    df = pd.DataFrame(fanpage, columns = ['粉專按讚人數', '粉絲專頁大頭貼', '粉絲專頁封面照片'])
    df.to_csv(os.path.join(path, '粉專按讚人數與頭貼與封面.csv'), index=False, encoding='UTF-8')

    df = pd.DataFrame(posts, columns = ['粉絲專頁名稱', '貼文時間', '貼文ID', '貼文內容', '分享內容', '讚數', '分享數'])
    df.to_csv(os.path.join(path, '粉專各文章之基本數值統計.csv'), index=False, encoding='UTF-8')

    for i in range(index-1):
        i = i+1
        df = pd.DataFrame(locals()['comments_list_%s' %(i)], columns = ['時間', 'ID', '名字', '留言內容'])
        name = '第'+str(i)+'篇文章留言.csv'
        df.to_csv(os.path.join(path, name), index=False, encoding='UTF-8')


#"account"請輸入你的facebook帳號
#"code"請輸入你的facebook密碼
#"want"請輸入想搜尋的關鍵字，型態為字串
#"daylen"請輸入想搜尋的天數(距離現在幾天)，型態同為字串

def search(account ,code ,want ,order , daylength):
    
    global driver

    if sys.platform == 'linux':
        driver = webdriver.Chrome(os.path.relpath('./linux/chromedriver'))
    elif sys.platform == 'win32':
        driver = webdriver.Chrome(os.path.relpath('./windows/chromedriver.exe'))
    elif sys.platform == 'darwin':
        driver = webdriver.Chrome(os.path.relpath('./mac/chromedriver'))

    if account == '':
        account = 'ericsyu0801@gmail.com'
        code = 'bloggerscout'
    
    if order == '':
        order = '3'
        
    if daylength == '':
        daylength = '3'
        
    order = int(order)
    daylength = int(daylength)
        
    url = 'https://www.facebook.com/'

    driver.get(url)

    time.sleep(2)

    user = driver.find_element_by_css_selector('#email')
    user.send_keys(account)
    password = driver.find_element_by_css_selector('#pass')
    password.send_keys(code)

    login = driver.find_element_by_css_selector('#loginbutton')
    login.click()
    
    time.sleep(12)
    
    if hasSelector('body > div._n8._3qx.uiLayer._3qw > div._3ixn'):
        space = driver.find_element_by_css_selector('body > div._n8._3qx.uiLayer._3qw > div._3ixn')
        space.click()

    if hasSelector('body > div._10.uiLayer._4-hy._3qw > div._59s7 > div > div > div > div > div._5a8u._5lnf.uiOverlayFooter > div > div > div._ohf.rfloat > div > a.layerCancel._4jy0._4jy3._517h._51sy._42ft'):
        cancel = driver.find_element_by_css_selector('body > div._10.uiLayer._4-hy._3qw > div._59s7 > div > div > div > div > div._5a8u._5lnf.uiOverlayFooter > div > div > div._ohf.rfloat > div > a.layerCancel._4jy0._4jy3._517h._51sy._42ft')
        cancel.click()

    keyword = driver.find_element_by_class_name('_1frb')
    keyword.send_keys(want)

    search = driver.find_element_by_class_name('_585_')
    search.click()

    time.sleep(4)

    page = driver.find_element_by_link_text('粉絲專頁')
    page.click()

    time.sleep(10)

    results = driver.find_elements_by_class_name('_32mo')

    global searresults
    searresults = []

    for result in results:
        searresult = []
        searresult.append(result.text)
        #temp = result.find_element_by_xpath('..')
        temp = result.get_attribute('href')
        temp = temp.strip('?ref=br_rs')
        searresult.append(temp)
        searresults.append(searresult)
        
    print()    
    print('粉絲專頁搜尋結果如下：')
    print()

    for i in searresults:
        print(i)
        
    for i in searresults:
        token = 'EAACRsaKtrOABANosgm3IbdMT9seNS2NtxZAuqxouZCp8oBKFW1PPD1R6qgf5wLoSvDzgrOMh2IVDV6pGopOqmy8jp4LZCre1lRIZCLU339xTV3QUW8D5cfzKke8q9oy3LaBAhjfVMuIuUDGImtz4ZCGUsyadsKlrpvP6f2VLFtgZDZD'
        res = requests.get('https://graph.facebook.com/v2.10/%s?fields=fan_count, location&access_token=%s' %(i[1], token))
        i.append(res.json()['fan_count'])
        if 'location' in res.json():
            i.append(res.json()['location'])
        else:
            i.append('N/A')
    
    i = len(searresults)-1
    
    while i > 0:
        for j in range(0, i):
            if searresults[j][2] < searresults[j+1][2]:
                searresults[j], searresults[j+1] = searresults[j+1], searresults[j]
        i = i-1   

    for i in searresults:
        i.insert(3, searresults.index(i)+1)

    print()    
    print('粉絲人數前%d名結果如下：' %(order))
    print()

    for i in range(0, order):
        # print(searresults[i])
        return searresult;
        
    # for i in range(0, order):
    #     print()
    #     print('現在開始抓取 --> %s 粉專' %(searresults[i][0]))
    #     crawlfb(searresults[i][0], searresults[i][1], daylength)


x
