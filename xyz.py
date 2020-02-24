from flask import Flask, render_template, request
import re
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from json2html import *     

class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key =  '8copIvV98chMO1XS5tu4rgwym'
        consumer_secret = 'AQHFU1qm9GCW6TRFqJkoSqpLUFJr0RJEOIwEclTIDKmXM0s6ds'
        access_token = '882544249404829696-Q6wS2TqvOeYOB4Ad7OO1J0cRQ7AUsxv'
        access_token_secret = 'IutQHY5m6P2bP0SbauTyOQak7Ys7aeE70GnFFAxJaIW6r'
  
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 
  
    #def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        #return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|((www\.[^\s]+)|(https?://[^\s]+))", " ", tweet).split()) 
        #return ' '.join(re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet, flags=re.MULTILINE).split())  

    

    def preprocess_tweet(self,tweet):
       #Preprocess the text in a single tweet
       #arguments: tweet = a single tweet in form of string 
       #convert the tweet to lower case
       
       tweet = tweet.lower()
       #convert all urls to sting "URL"
       tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
       #convert all @username to "AT_USER"
       tweet = re.sub('@[^\s]+','AT_USER', tweet)
       #correct all multiple white spaces to a single white space
       tweet = re.sub('[\s]+', ' ', tweet)
       #convert "#topic" to just "topic"
       tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
       return tweet


    def get_tweet_sentiment(self, tweet): 
        ''' tweet
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text 
        analysis = TextBlob(self.preprocess_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'
  
    def get_tweets(self, query, count = 10): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = [] 
  
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count) 
  
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 

                ## Processing
  
                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 
  
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
  
            # return parsed tweets 
            return tweets 
  
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e)) 
  
def main(result): 
    v = {}
    pos = []
    neg= []
    neu = []
    # creating object of TwitterClient Class 
    api = TwitterClient() 
    # calling function to get tweets 
    tweets = api.get_tweets(query = result, count = 200) 
  
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    # percentage of positive tweets 
    v["Positive"]=100*len(ptweets)/len(tweets) 
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
    # percentage of negative tweets 
    v["Negative"]=100*len(ntweets)/len(tweets) 
    # percentage of neutral tweets 
    # neutral Tweetes from tweets
    neu_tweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral'] 
     #percentage of neutral
    v['Neutral']=100*len(neu_tweets)/len(tweets)
    #print("Neutral tweets percentage: {} % ".format(100*len(tweets - ntweets - ptweets)/len(tweets))) 
  
    # printing first positive tweets 
   
    for tweet in ptweets[:10]: 
        pos.append(tweet['text']) 
  
    # printing first  negative tweets 
    
    for tweet in ntweets[:10]: 
        neg.append(tweet['text']) 

    for tweet in neu_tweets[:5]: 
        neu.append(tweet['text']) 

    v["N_tweets:"]= neg 
    v["P_tweets:"]= pos
    v["Neu_tweets:"] = neu
    return v
    


app = Flask(__name__)


@app.route('/')
def student():
   return render_template('student1.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   sentiment_val = []
   if request.method == 'POST':
      result = list(request.form.values())[0]
      print('Searched Keyword is :',result)
      v=main(result)
      columnNames = v.keys()
      # colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
      sentiment_val.append(v['Positive'])
      sentiment_val.append(v['Negative'])
      sentiment_val.append(v['Neutral'])
      labels = ['Positive','Negative','Neutral']
      colors = ["#00FF00", "#FF0000","#0000FF"]
   return render_template('table.html', records= v, colnames=columnNames,set = zip(sentiment_val,labels,colors))



'''
@app.route('/table')
def tb():
   return render_template('table.html')

'''

if __name__ == '__main__':
   app.run(debug = True)
