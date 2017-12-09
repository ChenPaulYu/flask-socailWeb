# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:06:35 2017

@author: cure8
"""

def crawlfb(fanpage_name, url, daylen):

    import os
    import shutil
    import datetime
    import requests
    import pandas as pd 
    from dateutil.parser import parse

    #以下token為永遠權限不會到期
    #儲存路徑是設定在我自己電腦的你們可以改!

    token = 'EAACRsaKtrOABANosgm3IbdMT9seNS2NtxZAuqxouZCp8oBKFW1PPD1R6qgf5wLoSvDzgrOMh2IVDV6pGopOqmy8jp4LZCre1lRIZCLU339xTV3QUW8D5cfzKke8q9oy3LaBAhjfVMuIuUDGImtz4ZCGUsyadsKlrpvP6f2VLFtgZDZD'
    path = './fanpage/' + fanpage_name
    
    #新增資料夾以供excel儲存
    
    if os.path.exists(path):
        shutil.rmtree(path)
        
    os.mkdir(path)

    #抓取粉專按讚人數、頭貼、封面照片

    res = requests.get('https://graph.facebook.com/v2.10/%s/posts?limit=100&access_token=%s' %(url, token))
    res = requests.get('https://graph.facebook.com/v2.10/%s/posts?limit=100&access_token=%s' % (res.json()['id'], token))


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
