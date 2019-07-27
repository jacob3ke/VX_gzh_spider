#! /usr/bin/env python3
from selenium import webdriver
from datetime import datetime
import bs4, requests
import os, time, sys
 
# 获取公众号链接
def getAccountURL(searchURL):
 res = requests.get(searchURL)
 res.raise_for_status()
 soup = bs4.BeautifulSoup(res.text, "lxml")
 # 选择第一个链接
 account = soup.select('a[uigs="account_name_0"]')
 return account[0]['href']
 
# 获取首篇文章的链接，如果有验证码返回None
def getArticleURL(accountURL):
 browser = webdriver.PhantomJS(r"E:\Program_Files_x86\phantomjs-2.1.1-windows\bin\phantomjs")
 # 进入公众号
 browser.get(accountURL)
 # 获取网页信息
 html = browser.page_source
 accountSoup = bs4.BeautifulSoup(html, "lxml")
 time.sleep(1)
 contents = accountSoup.find_all(hrefs=True)
 print(contents[:10])
 try:
  partitialLink = contents[0]['hrefs']
  firstLink = base + partitialLink
 except IndexError:
  firstLink = None 
  print('CAPTCHA!')
 return firstLink
 
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
 myfile = open("{}/{}_{}.html".format(path, account, title), 'wb')
 myfile.write(res.content)
 myfile.close()
 
base ='https://mp.weixin.qq.com'
accountList = ['央视新闻', '新浪新闻','凤凰新闻','羊城晚报']
query = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
 
path = folderCreation()
 
for index, account in enumerate(accountList):
 searchURL = query + account
 accountURL = getAccountURL(searchURL)
 time.sleep(10)
 articleURL = getArticleURL(accountURL)
 if articleURL != None:
  print("#{}({}/{}): {}".format(account, index+1, len(accountList), accountURL))
  # 读取第一篇文章内容
  res = requests.get(articleURL)
  res.raise_for_status()
  detailPage = bs4.BeautifulSoup(res.text, "lxml")
  title = detailPage.title.text
  print("标题: {}\n链接: {}\n".format(title, articleURL))
  writeToFile(path, account, title)
 else:
  print('{} files successfully written to {}'.format(index, path))
  sys.exit()
 
print('{} files successfully written to {}'.format(len(accountList), path))
