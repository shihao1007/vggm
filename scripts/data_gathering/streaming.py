# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 19:28:33 2019

This script sets up tweepy and hears twitter streams

@author: Shihao Ran
         STIM Laboratory
"""

from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream
from slistener import SListener
from urllib3.exceptions import ProtocolError

#%%
# consumer key authentication
consumer_key = 'vSRCw398hv3Wf03rYEXCNrepJ'
consumer_secret = 'zBbbzg4UnuFbWlNOvh2LBTbvFpkWQauaOELNyYcXim6wSyghop'

auth = OAuthHandler(consumer_key, consumer_secret)
#%%
# access key authentication
access_token = '4790635572-B9cSQdBJr8GofKHubTpU7oe0yBBcEwvTrJ5gUro'
access_token_secret = 'ktaaQc9fX5rZ4oF15NQZeeQ18sr3mL4rcIXBXoRir6uLs'

auth.set_access_token(access_token, access_token_secret)
#%%
# set up the API with the authentication handler
api = API(auth)

#%%
# set up words to hear
keywords_to_hear = ['#GrandTheftAutoV',
                    '#LeagueOfLegends',
                    '#Fortnite',
                    '#dota2',
                    '#CSGO',
                    '#ApexLegends',
                    '#Hearthstone',
                    '#overwatch']

# instantiate the SListener object
listen = SListener(api)

# instantiate the stream object
stream = Stream(auth, listen)

#%%

# begin collecting data
while True:
    # maintian connection unless interrupted
    try:
        stream.filter(track=keywords_to_hear)
    # reconnect automantically if error arise
    # due to unstable network connection
    except (ProtocolError, AttributeError):
        continue