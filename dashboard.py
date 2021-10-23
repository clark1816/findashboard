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

connection = psycopg2.connect(host = config.DB_HOST, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASS, port = '5432')
cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

option = st.sidebar.selectbox("Which Dashboard?", ('twitter', 'wallstreetbets', 'stocktwits', 'pattern','company info'), 1)

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
# url = 'http://127.0.0.1:5000/'
# if st.sidebar.button('Candle Stick Screener'):
    #webbrowser.open_new_tab(url)
    start_date = st.sidebar.date_input("Start date", datetime.date(2021, 1, 1))
    end_date = st.sidebar.date_input("End date", datetime.date(2021, 10, 19))


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

# Bollinger bands
    st.header('**Bollinger Bands**')
    qf=cf.QuantFig(tickerDf,title='First Quant Figure',legend='top',name='GS')
    qf.add_bollinger_bands()
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

if option == 'wallstreetbets':
    num_days = st.sidebar.slider('Number of days', 1, 30, 3)
    
    st.info('Number of times a ticker has been mentioned in wallstreet bets reddit page.')

    cursor.execute("""
        SELECT COUNT(*) AS num_mentions, symbol
        FROM mention JOIN stock ON stock.id = mention.stock_id
        WHERE date(dt) > current_date - interval '%s day'
        GROUP BY stock_id, symbol   
        HAVING COUNT(symbol) > 10
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

    rows = cursor.fetchall()

    st.write(rows)

# if option == 'pattern':
#     pattern = st.sidebar.selectbox(
#         "Which Pattern?",
#         ("engulfing", "threebar")
#     )

#     if pattern == 'engulfing':
#         cursor.execute("""
#             SELECT * 
#             FROM ( 
#                 SELECT day, open, close, stock_id, symbol, 
#                 LAG(close, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_close, 
#                 LAG(open, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_open 
#                 FROM daily_bars
#                 JOIN stock ON stock.id = daily_bars.stock_id
#             ) a 
#             WHERE previous_close < previous_open AND close > previous_open AND open < previous_close
#             AND day = '2021-10-17'
#         """)

#     if pattern == 'threebar':
#         cursor.execute("""
#             SELECT * 
#             FROM ( 
#                 SELECT day, close, volume, stock_id, symbol, 
#                 LAG(close, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_close, 
#                 LAG(volume, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_volume, 
#                 LAG(close, 2) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_close, 
#                 LAG(volume, 2) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_volume, 
#                 LAG(close, 3) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_previous_close, 
#                 LAG(volume, 3) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_previous_volume 
#             FROM daily_bars 
#             JOIN stock ON stock.id = daily_bars.stock_id) a 
#             WHERE close > previous_previous_previous_close 
#                 AND previous_close < previous_previous_close 
#                 AND previous_close < previous_previous_previous_close 
#                 AND volume > previous_volume 
#                 AND previous_volume < previous_previous_volume 
#                 AND previous_previous_volume < previous_previous_previous_volume 
#                 AND day = '2021-10-17'
#         """)

#     rows = cursor.fetchall()

#     for row in rows:
#         st.image(f"https://finviz.com/chart.ashx?t={row['symbol']}")
url = 'http://127.0.0.1:5000/'
if option == 'pattern':
    st.text('This option is not live it will be live once I get funding I have it set up but I dont have money for the software to make it live.')
    webbrowser.open_new_tab(url)
