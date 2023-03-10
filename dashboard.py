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
from sklearn import linear_model
import glob, os
import csv, zipfile
import base64

#from pygooglenews import GoogleNews
session = HTMLSession()

auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#connection = psycopg2.connect(port = st.secrets["DB_PORT"],host=st.secrets["DB_HOST"], database=st.secrets["DB_NAME"], user=st.secrets["DB_USER"], password=st.secrets["DB_PASS"])
#cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

option = st.sidebar.selectbox("Which Dashboard?", ('Home','AI Price Predictor','Insider Stock Tracker', 'News','twitter', 'stocktwits','company info','Inside Trade Golbin'),0)
if option == 'Insider Stock Tracker':
    st.sidebar.title('Insider Stock Tracker')
    #create a sidebar where you can select the house of representatives member you want to track
    st.sidebar.subheader('Select a House of representatives member')
    congressperson = st.sidebar.selectbox('House members', ['Pelosi', 'Mast', 'Crenshaw', 'Rouzer', 'McKinley', 'Welch', 'Dingell'])

    st.title('Inside Trade Golbin Tracker')
    zip_file_url = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2023FD.ZIP'

    r = requests.get(zip_file_url)
    zipfile_name = '2022.ZIP'
    with open(zipfile_name, 'wb') as f:
        f.write(r.content)

    with zipfile.ZipFile(zipfile_name, 'r') as z:
        z.extractall('results')\

    with open('results/2023FD.txt') as f:
        for line in csv.reader(f, delimiter='\t'):
            if line[1] == congressperson:
                date = line[7]
                doc_id = line[8]
                doc_url = f'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2023/{doc_id}.pdf'
                print(doc_url)
                r = requests.get(doc_url)

                with open(f'results/{doc_id}.pdf', 'wb') as pdf_file:
                    pdf_file.write(r.content)

                with open(f'results/{doc_id}.pdf',"rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'

                    st.markdown(pdf_display, unsafe_allow_html=True)


    for file in glob.glob('results/*.pdf'):
        os.remove(file)

if option == 'Home':
    st.header('Home Page')
    st.write('Welcome to you new dashboard for investing in stocks. This has everything you need from stock prices, to new, to machine learning models to tell what the stock price is going to be.')
if option == 'AI Price Predictor':
    st.header('Stock Price Predictor Using Machine Learing  and Linear Regression')
    st.image('download.png', caption='based on this heat map it my understanding that the high and low have the closest correlation on price.')
    ticker = st.text_input('Stock Ticker')
    period = st.text_input('Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max')
    interval = st.text_input('Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo')
    if interval:
        
        bars = yf.download(tickers = ticker,period=period, interval = interval, rounding = True )
        df = pd.DataFrame(bars)

        st.write(df[['Close', 'Low', 'High']].tail())
        
        X = df[['Low', 'High']]
        y = df['Close']

        regr = linear_model.LinearRegression()
        regr.fit(X,y)

        print(regr.coef_)

        #print(regr.copy_X)
        st.header('Input Values to Make Predictions')
        low_price = st.number_input('Stock Low Price')
        high_price = st.number_input('Stock High Price')
        if low_price and high_price:
            price_prediction = regr.predict([[low_price, high_price]])
            st.write(f'The anticipated price of the stock given the inputs is {price_prediction}')

    
# if option == 'candle pattern':
#     pattern = st.sidebar.selectbox(
#         "Which Pattern?",
#         ("bearish engulfing", "bullish engulfing", "bearish threeline strike", "bullishh threeline strike", "doji", "3 White Soldiers")
#     )
    

#     if pattern == 'bearish engulfing':
#         cursor.execute("""
#             select symbol, name, engulfing, close, dt
#             from stock join stock_price on stock_price.stock_id = stock.id
#             where dt = (select max(dt) from stock_price) AND engulfing = '-100'
#         """)
#     if pattern == 'bullish engulfing':
#         cursor.execute("""
#             select symbol, name, engulfing, close, dt
#             from stock join stock_price on stock_price.stock_id = stock.id
#             where dt = (select max(dt) from stock_price) AND engulfing = '100'
#         """)

#     if pattern == 'bearish threeline strike':
#         cursor.execute("""
#             select symbol, name, three_line, close, dt
#             from stock join stock_price on stock_price.stock_id = stock.id
#             where dt = (select max(dt) from stock_price) AND three_line = '-100'
#         """)
#     if pattern == 'bullishh threeline strike':
#         cursor.execute("""
#             select symbol, name, three_line, close, dt
#             from stock join stock_price on stock_price.stock_id = stock.id
#             where dt = (select max(dt) from stock_price) AND three_line = '100'
#         """)
   
#     if pattern == 'doji':
#         cursor.execute("""
#             select symbol, name, doji, close, dt
#             from stock join stock_price on stock_price.stock_id = stock.id
#             where dt = (select max(dt) from stock_price) AND doji = '100'
#         """)
#     if pattern == '3 White Soldiers':
#         cursor.execute("""
#             select symbol, name, wh_soldier, close, dt
#             from stock join stock_price on stock_price.stock_id = stock.id
#             where dt = (select max(dt) from stock_price) AND wh_soldier = '100'
#         """)

#     rows = cursor.fetchall()

#     for row in rows:
#         st.image(f"https://finviz.com/chart.ashx?t={row['symbol']}")
# #https://finviz.com/chart.ashx?t={row['symbol']}
# if option == 'twitter':
#     for username in config.TWITTER_USERNAMES:
#         user = api.get_user(username)
#         tweets = api.user_timeline(username)

#         st.subheader(username)
#         st.image(user.profile_image_url)
        
#         for tweet in tweets:
#             if '$' in tweet.text:
#                 words = tweet.text.split(' ')
#                 for word in words:
#                     if word.startswith('$') and word[1:].isalpha():
#                         symbol = word[1:]
#                         st.write(symbol)
#                         st.write(tweet.text)
#                         st.image(f"https://finviz.com/chart.ashx?t={symbol}")

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

    
# if option == 'wallstreetbets':
#     num_days = st.sidebar.slider('Number of days', 1, 30, 3)
#     st.subheader("This pages shows you how many times each of the listed stocks is mentioned in r/wallstreetbets")
    
#     cursor.execute("""
#         SELECT COUNT(*) AS num_mentions, symbol
#         FROM mention JOIN stock ON stock.id = mention.stock_id
#         WHERE date(dt) > current_date - interval '%s day'
#         GROUP BY stock_id, symbol   
#         HAVING COUNT(symbol) > 3
#         ORDER BY num_mentions DESC
#     """, (num_days,))

#     counts = cursor.fetchall()
#     for count in counts:
#         st.write(count)
    
#     cursor.execute("""
#         SELECT symbol, message, url, dt
#         FROM mention JOIN stock ON stock.id = mention.stock_id
#         ORDER BY dt DESC
#         LIMIT 100
#     """)

#     mentions = cursor.fetchall()
#     for mention in mentions:
#         st.text(mention['dt'])
#         st.text(mention['symbol'])
#         st.text(mention['message'])
#         st.text(mention['url'])
#         #st.text(mention['username'])

#     rows = cursor.fetchall()

#     st.write(rows)
