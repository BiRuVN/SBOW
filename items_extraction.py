# -*- coding: utf-8 -*-
import pandas as pd
import re
from underthesea import sent_tokenize, word_tokenize
from fuzzywuzzy import fuzz
import time
import sys

#data_path = sys.argv[1]

def read_txt(f_path):
    f = open(f_path, encoding="utf8")
    if f.mode == 'r':
        content = f.read()
    return content.split('\n')

stopwords = read_txt('stopwords.txt')

# Remove stopwords
def remove_stopword(text):
    tokens = word_tokenize(text)
    return ' '.join(word for word in tokens if word not in stopwords)

df = pd.read_csv('chotot.csv')
df = df.drop(['price', 'acreage', 'bathroom', 'bedroom', 'address', 'time'], axis=1)
arr_description = []
set_abbreviate = { 'phòng ngủ': ['pn', 'phn'],
            'phòng khách': ['pk', 'phk'],
            'phòng vệ sinh': ['wc', 'tolet', 'toilet'],
            'hợp đồng': ['hđ', 'hd'],
            'đầy đủ': ['full'],
            'nhỏ': ['mini'],
            'tầm nhìn': ['view'],
            'địa chỉ': ['đc', 'đ/c'],
            'miễn phí': ['free'],
            'vân vân' : ['vv'],
            'liên hệ' : ['lh'],
            'trung tâm thành phố': ['tttp'],
            'yêu cầu': ['order'],
            'công viên': ['cv', 'cvien'],
            'triệu /' : ['tr/', ' tr /', 'tr '],
            'phường' : [' p ', ' ph '],
            'quận' : [' q ', ' qu '],
            ' một ' : [' 1 '],
            ' hai ' : [' 2 '],
            ' ba ' : [' 3 '],
            ' bốn ' : [' 4 '],
            ' năm ' : [' 5 ']
            }

def replace_abbreviate(s):
    for key in set_abbreviate:
        s = re.sub('|'.join(set_abbreviate[key]),' {} '.format(key), s)
    return s

for index in range(len(df.index)):
    arr = [re.sub('[+|()]', ' ', line.lower()) for line in df.iloc[index]["description"].split('\n')]
    arr = [re.sub('[.]', '', line) for line in arr if line != '']
    arr = [replace_abbreviate(line) for line in arr]
    arr = [re.sub('[^0-9A-Za-z ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ/%,]', ' ', line) for line in arr]
    arr = [re.sub('m2', ' m2', line) for line in arr]
    arr = [" ".join(line.split()) for line in arr]
    arr_description.append(remove_stopword(". ".join(arr)))

df = df.assign(description_2 = arr_description)

items = read_txt('items.txt')
places = read_txt('places.txt')

def check(sent):
    words = word_tokenize(sent)
    t = ''
    code = ''
    while len(words) > 0:
        t = " ".join(words)
        if any(fuzz.UQRatio(t, item) > 80 for item in items):
            code = 'item'
            break
        elif any(fuzz.UQRatio(t, place) > 80 for place in places):
            code = 'place'
            break
        else:
            words.pop(len(words)-1)
        t = ''
    return t, code

def extract_info(text):
    places_temp = []
    items_temp = []
    
    sents = sent_tokenize(text)
    for sent in sents:
        sent = sent.replace('.', '')
        sent = sent.replace(',', '')
        sent = sent.replace(':', '')
        sent = " ".join(sent.split())
        words = word_tokenize(sent)  
        while (len(words) > 0):
            t = ''
            for w in words:
                t = t + ' ' + w
            t = t.lstrip()
            s, code = check(t)
            if s != '':
                print('------------>' + s)
                if code == 'item':
                    items_temp.append(s)
                elif code == 'place':
                    places_temp.append(s)
                else:
                    continue
                t = t.replace(s, '', 1)
                words = word_tokenize(t)
            else:
                t = t.replace(words[0], '', 1)
                words = word_tokenize(t)
    
    return places_temp, items_temp

places_list = []
items_list = []

for i in range (len(df)):
    text = df['description_2'][i]
    places_result, items_result = extract_info(text)
    items_list.append(items_result)
    places_list.append(places_result)



