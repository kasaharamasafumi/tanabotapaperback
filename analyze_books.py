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
import json
from watson_developer_cloud import PersonalityInsightsV3
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from collections import OrderedDict
import pprint
import itertools
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
from ibm_watson import PersonalityInsightsV3

import random

# APIキーの設置
CONSUMER_KEY = 'UVZ8k8rfFjKMFVs9opIx3k230'
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
    count = 200  # 一度のアクセスで何件取ってくるか
    aTimeLine = t.statuses.user_timeline(screen_name=screen_name, count=count, max_id=max_id)
    for tweet in aTimeLine:
        userTweets.append(tweet['text'])


def get_userstweets(screen_name):
    number_of_tweets = 0
    count = 200  # 一度のアクセスで何件取ってくるか
    aTimeLine = t.statuses.user_timeline(screen_name=screen_name, count=count)
    for tweet in aTimeLine:
        number_of_tweets += 1
        userTweets.append(tweet['text'])
        if number_of_tweets >= 200:
            max_id = tweet["id"]
            print(max_id)
            get_userstweets_again(screen_name, max_id)
    return userTweets


def get_shaped_tweets(tweets_list):
    shaped_tweets = []
    rm_replie = re.compile(r'@([A-Za-z0-9_]+)')
    rm_url = re.compile(r'https?://t.co/([A-Za-z0-9_]+)')
    rm_hashtag = re.compile(r'#(\w+)')
    for tweet in tweets_list:
        shape = rm_replie.sub('', tweet)
        shape = rm_url.sub('', shape)
        shape = rm_hashtag.sub('', shape)
        shape = shape.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('\n', ' ')
        shaped_tweets.append(shape)
    return shaped_tweets






def get_personality(text):

    authenticator = IAMAuthenticator('tt0Ul73SdE0aOXsfeeAV55XHrBASyZs1ukRIZD3WWdYn')  # APIkeyを入力

    service = PersonalityInsightsV3(
        version='2018-10-30',
        authenticator=authenticator)
    service.set_service_url(
        'https://api.jp-tok.personality-insights.watson.cloud.ibm.com/instances/591407d0-781f-49cf-a85e-2315151d4f61')  # URLを入力

    profile = service.profile(
        content=text,
        content_type="text/plain",
        accept="application/json",
        content_language="ja",
        accept_language="en",
        raw_scores=True,
    ).get_result()

    return profile


def convert_dict_to_json(orig_dict, indent=4):
    return json.dumps(orig_dict)


def load_json_as_dict(json_name):
    with open("./" + json_name, "r") as json_file:
        return json.load(json_file, object_pairs_hook=OrderedDict)


def sort_personality(tweet_result):
    return sorted(tweet_result.items(), key=lambda x: x[1], reverse=True)


def main(my_user_name):
    tweets = get_userstweets(my_user_name)
    tweets = get_shaped_tweets(tweets)

    ## ユーザのツイートを性格APIで分析する

    tweets_joined = " ".join(tweets)  # 集めた複数のツイートを結合
    user_personality_dict = OrderedDict()

    tweet_personality_dict = get_personality(tweets_joined)  # ツイートを結合したデータをAPIに入力


    # ツイートから分析した性格の名前
    personality_name = [big5["name"] for big5 in tweet_personality_dict["personality"]]
    # 性格の値。小数点第2位で四捨五入した後、decimal.Decimalからfloatに変換している。
    # 参考サイト(四捨五入)：https://note.nkmk.me/python-round-dec\imal-quantize/
    personality_percentile = [float(Decimal(str(big5["percentile"])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) \
                              for big5 in tweet_personality_dict["personality"]]

    # ユーザのツイートの分析結果
    all_tweets_big5 = OrderedDict(zip(personality_name, personality_percentile))

    # { my_user_id: { personality_name1: percentile1, personality2: percentile2, ... } }
    user_personality_dict[my_user_name] = all_tweets_big5
    # print("finished analyzing all({}) tweets.".format(len(tweets)))

    # Agreeableness: 協調性, Conscientiousness: 真面目さ, Emotional range: 精神的安定性, Extraversion: 外向性, Openness: 開放性
    # 参考サイト：https://note.nkmk.me/python-math-factorial-permutations-combinations/
    big5_list = ["Agreeableness", "Conscientiousness", "Emotional range", "Extraversion", "Openness"]

    # big5から2つの性格を選ぶ組み合わせを列挙する
    category_patterns = [set(pat) for pat in itertools.combinations(big5_list, 2)]

    # ユーザのツイートのカテゴリ分けを記録する辞書
    user_tweet_category_table = OrderedDict()

    # ユーザのツイートの分析結果を、値の大きい順にソートする
    sorted_result = sort_personality(user_personality_dict[my_user_name])

    # big5のうち大きい順から2番目までの値の性格名のみを取得し、その本のカテゴリとする(例：{Openness, Extraversion})
    # この時、複数の性格の順番を考慮させないために、setで用意する
    # 2つを組み合わせているため、1つだけの場合よりも幅広くカテゴリ分けできそう
    tweet_category = {big5_elm[0] for big5_elm in sorted_result[0:2]}
    user_tweet_category_table[my_user_name] = tweet_category

    user_personality = user_tweet_category_table[my_user_name]

    suggest_book = ""
    img_path = "./static/images/nothing.jpg"  # templates/index.htmlを基準にしたパス
    if user_personality == {'Openness', 'Extraversion'}:
        candidates = ['chumonno_oi_ryoriten', 'hashire_merosu']
        suggest_book = random.choice(candidates)
        img_path = "./static/images/" + suggest_book + ".jpg"
    elif user_personality == {'Openness', 'Emotional range'}:
        suggest_book = 'bocchan'
        img_path = "./static/images/" + suggest_book + ".jpg"
    elif user_personality == {'Openness', 'Agreeableness'}:
        candidates = ['kaijin_nijumenso', 'ningen_shikkaku']
        suggest_book = random.choice(candidates)
        img_path = "./static/images/" + suggest_book + ".jpg"
    else:
        suggest_book = "not found a suggested book..."

    return suggest_book, img_path
