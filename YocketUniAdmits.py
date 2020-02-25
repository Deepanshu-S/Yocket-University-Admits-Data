#!/usr/bin/env python
# coding: utf-8


import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
import re


#####   Enter your details here         ######

base = "https://yocket.in"      
url = 'https://yocket.in/applications-admits-rejects/195-university-of-texas-dallas/2' ##your university program url
pages = 88                                                                  #number of total pages you want to scan (pagination at bottom)
user = ''           ##your credentials
passw = ''

#driver init
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(7)

#login
driver.get('https://yocket.in/account/login')
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[2]/form/div[2]/input').send_keys(user)
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[2]/form/div[3]/button').click()
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[2]/form/div[2]/div[2]/input').send_keys(passw)
driver.find_element_by_xpath('//*[@id="overlay"]/div/div[1]/div/div[2]/form/div[3]/button').click()
driver.get(url)


#cancel popup if it appears
try:
    driver.find_element_by_class_name('subscribers-no-button').click()
except:
    pass

##########Scan all pages

df = pd.DataFrame(columns= ['Name','Term', 'Year', 'GRE' ,'Q','V', 'TOEFL', 'GPA', 'EXP','Going', 'LINK'])

for i in range(1,pages+1):
    driver.get(url+'?page='+str(i))    
    content = driver.page_source
    soup = BeautifulSoup(content)
        
    univ = soup.findAll('input', id='users-view-search-universities')[0]
    univ = BeautifulSoup(str(univ))
    univ = univ.input['value']

    for a in soup.findAll('div', class_="panel-body"):
        #print(a)
        name = a.h4.a.text                                       #name
        term  = a.small.text[-10:-6]                             #term of the year
        term= 'Spring' if term=='ring' else 'Fall' if term=='all' else term
        year  = a.small.text[-5:]                                #Year of joining
        link = a.a.get('href')                                   # profile links
        link = base + link 
        gre = a.findAll('div', class_="col-xs-6")[0].text[4:]    # GRE links
        t =a.findAll('div', class_="col-xs-6")[1].text[7:]       # TOEFL links
        gpa = a.findAll('div', class_="col-xs-6")[2].text[11:]   # GPA links
        exp = a.findAll('div', class_="col-xs-6")[3].text[9:]    # EXP links
        df = df.append({'Name' : name ,'Term': term, 'Year': year, 'GRE' : gre, 'TOEFL' : t, 'GPA' : gpa, 'EXP' : exp, 'LINK' : link}, ignore_index = True) 

df_orig = df.copy()   #for safe keeping####################
df['GRE'] = df['GRE'].str.extract('(\d+)').astype(float)
df['TOEFL'] = df['TOEFL'].str.extract('(\d+)').astype(float)

#Percentage conversion to GPA for simplification
df['GPA'] = df['GPA'].str.extract(r'(\d+.\d+)').astype(float)
df['GPAEq'] = np.where(df['GPA'].astype(float) > 10,  df['GPA'] / 10, df['GPA']) 

df.to_csv('Report.csv', index=False, encoding='utf-8')



##Run this part to get GRE score split and final university decided upon of each user ####
    
##Yocket will block you temporarily through a captcha after 200 continous requests, 
    
for i in df.index:      # or range(0,200):
    link = df["LINK"][i]
    print(i, link)
    
    driver.get(link)
    content = driver.page_source
    soup = BeautifulSoup(content)
    
    a =soup.findAll('div', class_="col-sm-4 col-xs-4")
    try:
        quant = a[0].h4.span.text[8:11]
    except:
        quant = 0
    try:
        verbal = a[0].h4.span.text[20:]
    except:
        verbal=0
        
    uni = 'Undecided' 
    status=''
    for s in soup.findAll('i', class_='fa-plane'):
        uni = s.parent.parent.parent.parent.td.h4.a.text
        sub = s.parent.parent.parent.parent.td.h4.a.small.text
        uni = uni[1:uni.find(sub)-1]
        
    if(uni==univ):
        status ="Yes"
    elif(uni=='Undecided'):
        status = uni
    else:
        status = "No"
        
    df['Q'][i]= quant
    df['V'][i]= verbal
    df['Going'][i]= status
    

df.to_csv ('dataframe.csv', index = False, header=True) 
