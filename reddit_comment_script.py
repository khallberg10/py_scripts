# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
from pushshift_py import PushshiftAPI
import datetime as dt
import re
import nltk
from textblob import TextBlob

def main():
    
    '''get user input'''
    print('subreddit: ')
    subreddit = input()
    print('search term: ')
    q = input()
    try:
        limit= int(input('Number of comments (leave blank for all): '))
    except ValueError:
        limit = None


    '''get reddit comments from pushshift.io'''
    df = get_comments(subreddit, q , limit)
    
    '''commplete sentiment analysis'''
    _sentiment = df['body'].apply(get_sentiment)
    df = df.assign(sentiment = _sentiment)
   
    '''convert unix time to datetime'''
    _timestamp = df['created'].apply(get_date)
    df=df.assign(timestamp = _timestamp)
    
    print('save csv to filepath: ')
    filepath = str(input())
    
    df.to_csv(filepath)
    
def get_comments(subreddit, q, limit):
    
    api = PushshiftAPI()
    
    results = api.search_comments(subreddit=subreddit, q=q, limit=limit)

    comment_dict = {'body':[],'created':[],'comment_id':[],'submission_id':[],\
                'parent_id':[],'score':[]}
    
    for sub in results:
        comment_dict['body'].append(sub.body)
        comment_dict['created'].append(sub.created_utc)
        comment_dict['comment_id'].append(sub.id)
        comment_dict['submission_id'].append(sub.link_id)
        comment_dict['parent_id'].append(sub.parent_id)
        comment_dict['score'].append(sub.score)
    
    data = pd.DataFrame(comment_dict)
    
    _clean_body = data['body'].apply(clean_text)
    data_clean = data.assign(body=_clean_body)
    
    return data_clean

def clean_text(text):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)",\
                           " ", text).split()) 

def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def get_date(created):
    return dt.datetime.fromtimestamp(created)

main()