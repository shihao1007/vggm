# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 19:28:33 2019

This script sets up tweepy and hears tweeter streams

@author: Shihao Ran
         STIM Laboratory
"""

from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream
from slistener import SListener

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
keywords_to_hear = ['#LeagueOfLegends',
                    '#Fortnite',
                    '#ApexLegends',
                    '#Hearthstone']

# instantiate the SListener object
listen = SListener(api)

# instantiate the stream object
stream = Stream(auth, listen)

#%%

# begin collecting data
stream.filter(track=keywords_to_hear)