#!/usr/bin/env python                                                                                                                                             
# -*- coding:utf-8 -*-  
import json
from requests_oauthlib import OAuth1Session
from twitter import Twitter, OAuth
from janome.tokenizer import Tokenizer
import collections
import re
from collections import Counter, defaultdict
import sys, json, time, calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta

#APIキーの設置
CONSUMER_KEY =  'UVZ8k8rfFjKMFVs9opIx3k230'
CONSUMER_SECRET = 'jLRKOA4tAQyJ4zJTclQdsElMUmSigywmxP0QjoCvbIdBNb62XC'
ACCESS_TOKEN = '848831384944640000-4ZMFN2QeB0DqPPBySkoaROr1qPp6GUl'
ACCESS_SECRET = 'QgUnk1GmnahidECs671moBFcsXmt19UXAHQviSApXwN4x'

t = Twitter(auth=OAuth(
    ACCESS_TOKEN,
    ACCESS_SECRET,
    CONSUMER_KEY,
    CONSUMER_SECRET
))
    
twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
url = "https://api.twitter.com/1.1/search/tweets.json"
userTweets = []

def get_userstweets_again(screen_name, max_id):
    max_id = max_id
    count = 200 #一度のアクセスで何件取ってくるか
    aTimeLine = t.statuses.user_timeline(screen_name = screen_name, count=count, max_id=max_id)
    for tweet in aTimeLine:
        userTweets.append(tweet['text'])

def get_userstweets(screen_name):
    number_of_tweets = 0
    count = 200 #一度のアクセスで何件取ってくるか
    aTimeLine = t.statuses.user_timeline(screen_name = screen_name, count=count)
    for tweet in aTimeLine:
        number_of_tweets += 1
        userTweets.append(tweet['text'])
        if number_of_tweets >= 200:
            max_id = tweet["id"]
            print("aa")
            print(max_id)
            print("bb")
            get_userstweets_again(screen_name, max_id)

def use_function():
    #検索したい相手を指定 
    print("自分のuser_idを入力してください")
    my_user_id = input('>> ')
    print('----------------------------------------------------')
    
    get_userstweets(my_user_id)
    
    print("ツイートの取得が終了しました")
    print()
    # print(userTweets)
    # print(len(userTweets))
