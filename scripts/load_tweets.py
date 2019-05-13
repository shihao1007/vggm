# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 20:21:42 2019

@author: Shihao Ran
         STIM Laboratory
"""

import json
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
import glob

def list_col_to_str_col(df):
    """
    if a column in the dataframe is a list
    convert it into str so it can be stored in the batabase

    Parameters
    ----------
        df: the dataframe to be converted

    Returns
    -------
        None
    """

    for col in df.columns:
        if type(df[col].iloc[0]) is list:
            df[col] = df[col].apply(str)

def expand_dict(df):
    """
    expand a two column dataframe of which the second column
    contains dictionarys

    Parameters
    ----------
        df: 2-column pandas dataframe

    Returns
    -------
        df_with_id: multi-column pandas dataframe
            the number of columns after expantion is equal to the number
            of keys in the dictionary
    """
    ID = df.iloc[:,0]
    series = df.iloc[:,1].tolist()
    df_from_series = pd.DataFrame(series, index=df.index)
    df_with_id = pd.concat([ID, df_from_series], axis=1)

    return df_with_id

def drop_empty_list(df):
    """
    replace the empty lists in a two-column dataframe into np.nan
    so they can be dropped using df.dropna() method

    Parameters
    ----------
        df: two-column pandas dataframe

    Returns
    -------
        df_dropped: with all the empty lists dropped
    """

    replace_nan = lambda x: np.nan if len(x)==0 else x
    col = df.iloc[:,1].copy()
    new_col = col.apply(replace_nan)
    df_replaced = pd.concat([df.iloc[:,0], new_col], axis=1)

    df_dropped = df_replaced.dropna()
    return df_dropped


def merge_dicts(df):
    """
    when the other column of the dataframe contains a list of dictionarys
    with the same key and value pairs
    we merge the list to a single dictionary

    Parameters
    ----------
        df: input dataframe

    Returns
    -------
        df_merged_w_id

    """
    series = df.iloc[:,1].copy().tolist()
    merged_series = []
    for dict_lst in series:
        dict_1 = dict_lst[0]
        total_dict = {key:[] for key in list(dict_1.keys())}
        for dit in dict_lst:
            for key in list(dict_1.keys()):
                total_dict[key].append(dit[key])
        merged_series.append(total_dict)
    df_merged = pd.DataFrame(merged_series, index=df.index)
    df_merged_w_id = pd.concat([df.iloc[:,0], df_merged], axis=1)
    
    return df_merged_w_id

#%%
def json2df(filename):
    """
    load json file into a list of dictionarys
    
    Parameters
    ----------
        filename: string
            the directory of the json file
    
    Returns
    -------
        to_sql: list of pandas dataframes
            each dataframe corresponds to a table in the database
    """
    
    
    """
    First section:
        load the tweets from the json file
        then coarsely split them into base tweets and dict tweets
    """
    
    # convert from JSON to Python object
    
    
    # initialize a list for all the json lines
    tweets = []
    
    # initialize a dictionary for all the dataframes
    to_sql = {}
    
    # load the json file into a list
    with open(filename, 'r') as f:
        for line in f:
            if line != '\n':
                tweet = json.loads(line)
                tweets.append(tweet)
    
    # convert the list of lines into a dataframe
    tweets_df = pd.DataFrame(tweets)
    tweets_df.rename(columns={'id':'tweet_id',
                              'id_str':'tweet_id_str'}, inplace=True)
    
    # specify the columns that have to be stored in dicts
    to_dicts = ['tweet_id',
                'coordinates',
                'entities',
                'extended_entities',
                'extended_tweet',
                'place',
                'quoted_status',
                'quoted_status_permalink',
                'retweeted_status',
                'user']
    
    # specify the columns to drop
    to_drop = [ 'contributors',
                'display_text_range',
                'coordinates',
                'entities',
                'extended_entities',
                'extended_tweet',
                'geo',
                'place',
                'quoted_status',
                'quoted_status_permalink',
                'retweeted_status',
                'user']
    
    
    # divide the raw tweets into normal part (without dicts)
    # and dict part (needs to be saved into multiple tables)
    tweets_dicts = tweets_df[to_dicts]
    tweets_non_dicts = tweets_df.drop(to_drop, axis=1)
    
    # add the base tweets into the dictionary
    to_sql['base_tweets'] = tweets_non_dicts
    
    # seperate the columns in the dicts dataframe into multiple dataframes
    tweets_2dict_lst = []
    for idx in range(1, len(to_dicts)):
        tweets_2dict_lst.append(tweets_dicts[['tweet_id', to_dicts[idx]]].dropna())
    
    """
    Second section:
        for each dataframes in the tweets_2dict_lst
        flatten them into a cleaner format of dataframes
    """
    
    """
    2.1 coordinates
    """
    coor_df = tweets_2dict_lst[0]
    
    coor_df = expand_dict(coor_df)
    
    list_col_to_str_col(coor_df)
    
    to_sql['coordinates'] = coor_df
    
    """
    2.2 entities
    """
    # get the entities first
    entities_df = expand_dict(tweets_2dict_lst[1])
    
    # get hashtags and user_mentions
    hashtags_df = drop_empty_list(entities_df[['tweet_id', 'hashtags']])
    user_mentions_df = drop_empty_list(entities_df[['tweet_id', 'user_mentions']])
    
    # merge them
    hashtags_df = merge_dicts(hashtags_df)
    user_mentions_df = merge_dicts(user_mentions_df)
    
    # convert list object to str
    list_col_to_str_col(hashtags_df)
    list_col_to_str_col(user_mentions_df)
    
    # add into list
    to_sql['hashtags'] = hashtags_df.rename({'text':'hashtag'}, axis=1)
    to_sql['user_mentions'] = user_mentions_df
    
    """
    2.3-2.5 extended tweet, quoted tweet, retweeted
    """
    
    # use the json indexing to get the useful information
    # initialize each dictionary
    extended_tweet = {'tweet_id':[],
                      'full_text':[],
                      'user_mentions':[],
                      'extended_hashtags':[]}
    
    quoted_tweet = {'tweet_id':[],
                    'quoted_id':[],
                    'quoted_text':[],
                    'quoted_hashtags':[]}
    
    quoted_user = {'tweet_id':[],
                   'quoted_user':[]}
    
    retweeted_tweet = {'tweet_id':[],
                       'retweeted_id':[],
                       'retweeted_text':[],
                       'retweeted_hashtags':[]}
    
    retweeted_user = {'tweet_id':[],
                      'retweeted_user':[]}
    
    
    with open(filename, 'r') as file:
        for line in file:
            if line != '\n':
                tweet = json.loads(line)
                
                # get info for extended tweets
                if 'extended_tweet' in tweet.keys():
                    extended_tweet['tweet_id'].append(tweet['id'])
                    extended_tweet['full_text'].append(tweet['extended_tweet']['full_text'])
                    user_mentions = [dit['id'] for dit in tweet['extended_tweet']['entities']['user_mentions']]
                    extended_tweet['user_mentions'].append(user_mentions)
                    extended_hashtags = [dit['text'] for dit in tweet['extended_tweet']['entities']['hashtags']]
                    extended_tweet['extended_hashtags'].append(extended_hashtags)
                    
                # get info for quoted tweets
                if 'quoted_status' in tweet.keys():
                    quoted_tweet['tweet_id'].append(tweet['id'])
                    quoted_tweet['quoted_id'].append(tweet['quoted_status']['id'])
                    quoted_tweet['quoted_text'].append(tweet['quoted_status']['text'])
                    quoted_hashtags = [dit['text'] for dit in tweet['quoted_status']['entities']['hashtags']]
                    quoted_tweet['quoted_hashtags'].append(quoted_hashtags)
                    
                    # get info for quoted users
                    
                    quoted_user['tweet_id'].append(tweet['id'])
                    quoted_user['quoted_user'].append(tweet['quoted_status']['user'])
                    
                # get info for retweeted tweets
                if 'retweeted_status' in tweet.keys():
                    retweeted_tweet['tweet_id'].append(tweet['id'])
                    retweeted_tweet['retweeted_id'].append(tweet['retweeted_status']['id'])
                    retweeted_tweet['retweeted_text'].append(tweet['retweeted_status']['text'])
                    retweeted_hashtags = [dit['text'] for dit in tweet['retweeted_status']['entities']['hashtags']]
                    retweeted_tweet['retweeted_hashtags'].append(retweeted_hashtags)
                    
                    # get info for quoted users
                    
                    retweeted_user['tweet_id'].append(tweet['id'])
                    retweeted_user['retweeted_user'].append(tweet['retweeted_status']['user'])
                    
        extended_tweet_df = pd.DataFrame(extended_tweet)
        quoted_tweet_df = pd.DataFrame(quoted_tweet)
        quoted_user_df = pd.DataFrame(quoted_user)
        retweeted_tweet_df = pd.DataFrame(retweeted_tweet)
        retweeted_user_df = pd.DataFrame(retweeted_user)
        
    # handle the new dataframes
    # expand two user dataframes
    quoted_user_df = expand_dict(quoted_user_df)
    retweeted_user_df = expand_dict(retweeted_user_df)
    
    # convert list to str
    list_col_to_str_col(extended_tweet_df)
    list_col_to_str_col(quoted_tweet_df)
    list_col_to_str_col(retweeted_tweet_df)
    
    # add into list
    to_sql['extended_tweets'] = extended_tweet_df
    to_sql['quoted_tweets'] = quoted_tweet_df
    to_sql['quoted_user'] = quoted_user_df
    to_sql['retweeted_tweet'] = retweeted_tweet_df
    to_sql['retweeted_user'] = retweeted_user_df
    
    """
    2.6 place
    """
    # handle place dataframe
    place_df = tweets_2dict_lst[4]
    # expand it first
    place_df = expand_dict(place_df).drop(['attributes'], axis=1)
    
    # note that bounding box column contains dictionarys
    # make it a new dataframe into two columns
    bounding_box_lst = place_df.loc[:, 'bounding_box'].copy().tolist()
    bounding_box_df = pd.DataFrame(bounding_box_lst,
                                   index=place_df.index)
    bounding_box_df.rename(columns={'coordinates': 'bounding_box_coordinates',
                                    'type': 'bounding_box_type'})
    
    # then merge it back and drop the original one
    place_df = pd.concat([place_df, bounding_box_df], axis=1)
    place_df.drop(['bounding_box'], axis=1, inplace=True)
    
    # convert list to str
    list_col_to_str_col(place_df)
    
    # add to list
    to_sql['place'] = place_df
    
    """
    2.7 user
    """
    # expand it
    user_df = expand_dict(tweets_2dict_lst[8])
    to_keep = ['tweet_id',
               'created_at',
               'description',
               'favourites_count',
               'followers_count',
               'geo_enabled',
               'id',
               'lang',
               'location',
               'url',
               'verified',
               'friends_count']
    
    # add to list
    to_sql['tweet_user'] = user_df[to_keep].copy()
    
    """
    Third section
        parse datetime object
    """
    # for each dataframe in the list
    for df_name, df in to_sql.items():
        if 'created_at' in df.columns:
            df.created_at = pd.to_datetime(df.created_at)
        df.drop_duplicates(inplace=True)
    
    return to_sql
    
#%%
# create a new database
#engine = create_engine('postgresql://postgres:461022@localhost:5432')
#
#con = engine.connect()
#con.execute('commit')
#con.execute('create database tweets_48')
#con.close()

#%%
# to postgresql
#engine = create_engine('postgresql://postgres:461022@localhost:5432/tweets_48')
engine = create_engine('sqlite:///tweets_48.sqlite')
# call the function to load the json into dataframes
file_str = r'E:\self_learning\vggm\raw_tweets\streamer*.json'
file_lst = glob.glob(file_str)

for file_idx, file_name in enumerate(file_lst):
    if file_idx == 0:
        option = 'replace'
    else:
        option = 'append'
    to_sql = json2df(file_name)
    for df_name, df in to_sql.items():
        print(file_idx, df_name)
        df.to_sql(df_name, con=engine, if_exists=option)
