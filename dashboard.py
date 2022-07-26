import streamlit as st
import pandas as pd
import numpy as np
import requests
import tweepy
import config 
import psycopg2, psycopg2.extras
import plotly.graph_objects as go
import datetime
import yfinance as yf
import cufflinks as cf
import webbrowser
from requests_html import HTMLSession
import json
#from pygooglenews import GoogleNews
session = HTMLSession()

auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

option = st.sidebar.selectbox("Which Dashboard?", ('News','twitter', 'stocktwits', 'pattern','company info'), 0)

st.header(option)

if option == 'twitter':
    for username in config.TWITTER_USERNAMES:
        user = api.get_user(username)
        tweets = api.user_timeline(username)

        st.subheader(username)
        st.image(user.profile_image_url)
        
        for tweet in tweets:
            if '$' in tweet.text:
                words = tweet.text.split(' ')
                for word in words:
                    if word.startswith('$') and word[1:].isalpha():
                        symbol = word[1:]
                        st.write(symbol)
                        st.write(tweet.text)
                        st.image(f"https://finviz.com/chart.ashx?t={symbol}")

if option == 'company info':
    
# Sidebar
    st.sidebar.subheader('company info')
    start_date = st.sidebar.date_input("Start date", datetime.date(2022, 1, 1))
    end_date = st.sidebar.date_input("End date", datetime.date(2022, 8, 8))

# Retrieving tickers data
    ticker_list = pd.read_csv('https://raw.githubusercontent.com/shilewenuw/get_all_tickers/master/get_all_tickers/tickers.csv')
    tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol
    tickerData = yf.Ticker(tickerSymbol) # Get ticker data
    tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker

# Ticker information
    string_logo = '<img src=%s>' % tickerData.info['logo_url']
    st.markdown(string_logo, unsafe_allow_html=True)

    string_name = tickerData.info['longName']
    st.header('**%s**' % string_name)

    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)

# Ticker data
    st.header('**Ticker data**')
    st.write(tickerDf)

# Stock Chart
    st.header('**Stock Chart**')
    qf=cf.QuantFig(tickerDf,title='First Quant Figure',legend='top',name='GS')
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)


if option == 'stocktwits':
    symbol = st.sidebar.text_input("Symbol", value='AAPL', max_chars=5)

    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")

    data = r.json()

    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])

        
url = 'https://candle-pattern-app.herokuapp.com/'
if option == 'pattern':
    st.write("check out this [link](https://candle-pattern-app.herokuapp.com/)")
                        

if option == 'News':
    news_option = st.sidebar.selectbox("What Type of News?", ('Business', 'Technology', 'Covid','Russo-Ukrainian War','Sports', 'Health','World News','US News', 'Entertainment'), 0)

    if news_option == 'Business':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?gl=US&hl=en-US&ceid=US:en'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'Technology':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'Covid':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNREZqY0hsNUVnSmxiaWdBUAE?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass
        
    if news_option == 'Russo-Ukrainian War':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqJAgKIh5DQkFTRUFvS0wyMHZNRjk0Tm1RMWVCSUNaVzRvQUFQAQ?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'Sports':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'Health':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'World News':
        st.title(news_option)
        url = 'https://news.google.com/topstories?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'US News':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    if news_option == 'Entertainment':
        st.title(news_option)
        url = 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen'
        r = session.get(url)
        articles = r.html.find('article')
        for item in articles:
            try:
                newsitem = item.find('h3', first = True)
                title = newsitem.text
                link = newsitem.absolute_links
                st.write(title)
                text='check out this [link]({link})'.format(link=link)
                st.markdown(link,unsafe_allow_html=True)
            except:
                pass
