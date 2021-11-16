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


auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

option = st.sidebar.selectbox("Which Dashboard?", ('twitter', 'stocktwits', 'pattern','company info','wallstreetbets','s&p500stocks'), 4)

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

if option == 'wallstreetbets':
    st.subheader('trending stocks in r/wallstreetbets over the past 4 days.')
    st.write('GGPI Most Mentions')
    st.subheader('trending stocks in r/wallstreetbets over the past 14 days.')
    st.write('1. TSLA')
    st.write('2. GME')
    st.write('3. SNDL')
    st.write('4. WISH')
    st.write('5. LCID')

if option == 's&p500stocks':
    st.subheader('Stocks in the S&P 500 that are breaking out:')
    st.write('AEE is breaking out')
    st.subheader('Stocks in the S&P 500 that are consolidating:')
    st.write('ARE is consolidating')
    st.write('MMM is consolidating')

if option == 'company info':
    
# Sidebar
    st.sidebar.subheader('company info')
# url = 'http://127.0.0.1:5000/'
# if st.sidebar.button('Candle Stick Screener'):
    #webbrowser.open_new_tab(url)
    start_date = st.sidebar.date_input("Start date", datetime.date(2021, 10, 15))
    end_date = st.sidebar.date_input("End date", datetime.date(2021, 11, 15))

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
