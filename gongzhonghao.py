#! /usr/bin/env python3
from selenium import webdriver
from datetime import datetime
import bs4, requests
import os, time, sys, re
import itchat

# 获取公众号链接
def getAccountURL(searchURL):
    res = requests.get(searchURL)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "lxml")
    # 选择第一个链接
    account = soup.select('a[uigs="account_name_0"]')
    return account[0]['href']

#获取发表时间
def find_publishTime(input_res):
    #res = requests.get(articleURL)
    ruler=re.compile(r'var publish_time = "(\d+.\d+.\d+)')
    published_t=ruler.findall(input_res.text)[0]
    return published_t



# 获取首篇文章的链接，如果有验证码返回None
def getArticleURL(accountURL):
    browser = webdriver.PhantomJS(r"E:\Program_Files_x86\phantomjs-2.1.1-windows\bin\phantomjs")
    # 进入公众号
    browser.get(accountURL)
    # 获取网页信息
    html = browser.page_source
    accountSoup = bs4.BeautifulSoup(html, "lxml")
    time.sleep(2)
    contents = accountSoup.find_all(hrefs=True)
    #print(contents[:10])
    link_lst=[]
    try:
        for ix in range(1,10):
            partitialLink = contents[ix]['hrefs']
            #firstLink = base + partitialLink
            link_lst.append(base + partitialLink)
    except IndexError:
        #firstLink = None 
        link_lst =None
        print('CAPTCHA!')
    #return firstLink
    return link_lst

# 创建文件夹存储html网页，以时间命名
def folderCreation():
    path = os.path.join(os.getcwd(), datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        print("folder not exist!")
    return path

# 将html页面写入本地
def writeToFile(path, account, title):
    title = title[2:-1]
    print(title)
    pathToWrite = os.path.join(path, '{}_{}.html'.format(account, title))
    myfile = open(pathToWrite, 'wb')
    myfile.write(res.content)
    myfile.close()


def writeToFile2(path, account, w_content):
    meta_file_nm = datetime.now().strftime('%Y-%m-%d')
    meta_file2Write = os.path.join(path, '{}.txt'.format(meta_file_nm))
    with open(meta_file2Write, 'a+') as f:
          f.write(w_content)


if __name__ == "__main__":
    #accountList = sys.argv[1].split(',')#央视新闻,南方周末,浪潮工作室
    pre_accountList = input("输入要爬取的公众号（英文逗号分隔）：\n")
    accountList=pre_accountList.split(',');print(accountList)
    send2who = input("输入接受消息的个人(备注名)：\n")#.decode("utf-8")
    print("输入个人是:{}".format(send2who))
    pre_send2room = input("输入接受消息的群组(备注名)：\n")#.decode("utf-8")
    print('输入群组是:{}'.format(pre_send2room))

    #微信登录
    itchat.login()

    cnt=0
    if pre_send2room != "":
        while True:
            RoomList = itchat.search_chatrooms(name=pre_send2room)
            if RoomList == []:
                print("{} group is not found!".format(pre_send2room))
                cnt +=1
            else:
                send2room = RoomList[0]['UserName']
                break
            if cnt > 10:
                mpsList=itchat.get_chatrooms(update=True)
                for k in mpsList:print(k['NickName'], k['UserName'])
            time.sleep(10)



    print('enter spider..................')
    base ='https://mp.weixin.qq.com'
    query = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
    path = folderCreation()

    for index, account in enumerate(accountList):
        searchURL = query + account
        accountURL = getAccountURL(searchURL)
        time.sleep(10)
        #articleURL = getArticleURL(accountURL)
        articleURList = getArticleURL(accountURL)
        count_day=0
        if articleURList != None:
            # print("#{}({}/{}): {}".format(account, index+1, len(accountList), accountURL))
            for articleURL in articleURList:
                time.sleep(10)
                res = requests.get(articleURL)
                if count_day ==0:
                    #latest_date = datetime.now().strftime('%Y-%m-%d')
                    latest_date = find_publishTime(input_res=res)
                if find_publishTime(input_res=res) != latest_date:
                    break
                res.raise_for_status()
                detailPage = bs4.BeautifulSoup(res.text, "lxml")
                title = detailPage.title.text
                print("标题: {}\n链接: {}\n".format(title, articleURL))
                content2wrt = "公众号: {}\n标题: {}\n链接: {}\n\n".format(account, title[1:-1], articleURL)
                if pre_send2room != "": itchat.send(content2wrt, toUserName=send2room)
                if send2who != "": itchat.send(content2wrt, itchat.search_friends(name=send2who)[0]["UserName"])
                try:
                    writeToFile(path, account, title)
                    writeToFile2(path, account, w_content=content2wrt)
                except OSError:
                    print("write failed")
                count_day +=1
        else:
            print('{} files successfully written to {}'.format(index, path))
            sys.exit()

    print('{} files successfully written to {}'.format(len(accountList), path))
    itchat.logout()
 