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
from requests_html import HTMLSession
import psycopg2, psycopg2.extras

#from pygooglenews import GoogleNews
session = HTMLSession()

auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

connection = psycopg2.connect(port = st.secrets["DB_PORT"],host=st.secrets["DB_HOST"], database=st.secrets["DB_NAME"], user=st.secrets["DB_USER"], password=st.secrets["DB_PASS"])
cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

option = st.sidebar.selectbox("Which Dashboard?", ('wallstreetbets','candle pattern', 'News','twitter', 'stocktwits','company info'),0)

st.header(option)

if option == 'candle pattern':
    pattern = st.sidebar.selectbox(
        "Which Pattern?",
        ("bearish engulfing", "bullish engulfing", "bearish threeline strike", "bullishh threeline strike", "doji", "3 White Soldiers")
    )
    st.sidebar("if there no stocks fit match the query for then none will appear")

    if pattern == 'bearish engulfing':
        cursor.execute("""
            select symbol, name, engulfing, close, dt
            from stock join stock_price on stock_price.stock_id = stock.id
            where dt = (select max(dt) from stock_price) AND engulfing = '-100'
        """)
    if pattern == 'bullish engulfing':
        cursor.execute("""
            select symbol, name, engulfing, close, dt
            from stock join stock_price on stock_price.stock_id = stock.id
            where dt = (select max(dt) from stock_price) AND engulfing = '100'
        """)

    if pattern == 'bearish threeline strike':
        cursor.execute("""
            select symbol, name, three_line, close, dt
            from stock join stock_price on stock_price.stock_id = stock.id
            where dt = (select max(dt) from stock_price) AND three_line = '-100'
        """)
    if pattern == 'bullishh threeline strike':
        cursor.execute("""
            select symbol, name, three_line, close, dt
            from stock join stock_price on stock_price.stock_id = stock.id
            where dt = (select max(dt) from stock_price) AND three_line = '100'
        """)
   
    if pattern == 'doji':
        cursor.execute("""
            select symbol, name, doji, close, dt
            from stock join stock_price on stock_price.stock_id = stock.id
            where dt = (select max(dt) from stock_price) AND doji = '100'
        """)
    if pattern == '3 White Soldiers':
        cursor.execute("""
            select symbol, name, wh_soldier, close, dt
            from stock join stock_price on stock_price.stock_id = stock.id
            where dt = (select max(dt) from stock_price) AND wh_soldier = '100'
        """)

    rows = cursor.fetchall()

    for row in rows:
        st.image(f"https://finviz.com/chart.ashx?t={row['symbol']}")
#https://finviz.com/chart.ashx?t={row['symbol']}
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
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
                #st.markdown(link,unsafe_allow_html=True)
            except:
                pass

    
if option == 'wallstreetbets':
    num_days = st.sidebar.slider('Number of days', 1, 30, 30)
    st.subheader("This pages shows you how many times each of the listed stocks is mentioned in r/wallstreetbets")
    
    cursor.execute("""
        SELECT COUNT(*) AS num_mentions, symbol
        FROM mention JOIN stock ON stock.id = mention.stock_id
        WHERE date(dt) > current_date - interval '%s day'
        GROUP BY stock_id, symbol   
        HAVING COUNT(symbol) > 3
        ORDER BY num_mentions DESC
    """, (num_days,))

    counts = cursor.fetchall()
    for count in counts:
        st.write(count)
    
    cursor.execute("""
        SELECT symbol, message, url, dt
        FROM mention JOIN stock ON stock.id = mention.stock_id
        ORDER BY dt DESC
        LIMIT 100
    """)

    mentions = cursor.fetchall()
    for mention in mentions:
        st.text(mention['dt'])
        st.text(mention['symbol'])
        st.text(mention['message'])
        st.text(mention['url'])
        #st.text(mention['username'])

    rows = cursor.fetchall()

    st.write(rows)
