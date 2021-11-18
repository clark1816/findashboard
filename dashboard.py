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
from web3 import Web3
import json

auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

option = st.sidebar.selectbox("Which Dashboard?", ('twitter', 'stocktwits', 'pattern','company info','wallstreetbets','s&p500stocks', 'nftdashboard'), 4)

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
    st.write('No stocks are  breaking out')
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
    
if option == 'nftdashboard':
    st.sidebar.header("Endpoints")
    endpoint_choices = ['Assets', 'Events', 'Rarity']
    endpoint = st.sidebar.selectbox("Choose an Endpoint", endpoint_choices)

    st.title(f"OpenSea API Explorer - {endpoint}")

    def render_asset(asset):
        if asset['name'] is not None:
            st.subheader(asset['name'])
        else:
            st.subheader(f"{asset['collection']['name']} #{asset['token_id']}")

        if asset['description'] is not None:
            st.write(asset['description'])
        else:
            st.write(asset['collection']['description'])

        if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
            st.video(asset['image_url'])
        elif asset['image_url'].endswith('svg'):
            svg = requests.get(asset['image_url']).content.decode()
            st.image(svg)
        elif asset['image_url']:
            st.image(asset['image_url'])


    if endpoint == 'Events':
        collection = st.sidebar.text_input("Collection")
        asset_contract_address = st.sidebar.text_input("Contract Address")
        token_id = st.sidebar.text_input("Token ID")
        event_type = st.sidebar.selectbox("Event Type", ['offer_entered', 'cancelled', 'bid_withdrawn', 'transfer', 'approve'])
        params = {}
        if collection:
            params['collection_slug'] = collection
        if asset_contract_address:
            params['asset_contract_address'] = asset_contract_address
        if token_id:
            params['token_id'] = token_id
        if event_type:
            params['event_type'] = event_type
        
        r = requests.get('https://api.opensea.io/api/v1/events', params=params)

        #events = r.json()
        event_list = []
        for event in events['asset_events']:
            if event_type == 'offer_entered':
                if event['bid_amount']:
                    bid_amount = Web3.fromWei(int(event['bid_amount']), 'ether')
                if event['from_account']['user']:
                    bidder = event['from_account']['user']['username']
                else:
                    bidder = event['from_account']['address']

                event_list.append([event['created_date'], bidder, float(bid_amount), event['asset']['collection']['name'], event['asset']['token_id']])

        df = pd.DataFrame(event_list, columns=['time', 'bidder', 'bid_amount', 'collection', 'token_id'])
        st.write(df)
        
        st.write(events)

    if endpoint == 'Assets':
        st.sidebar.header('Filters')
        owner = st.sidebar.text_input("Owner")
        collection = st.sidebar.text_input("Collection")
        params = {'owner': owner}
        if collection:
            params['collection'] = collection

        r = requests.get('https://api.opensea.io/api/v1/assets', params=params)

        assets = r.json()['assets']
        for asset in assets:                
            render_asset(asset)

        st.subheader("Raw JSON Data")
        st.write(r.json())

    if endpoint == 'Rarity':
        with open('assets.json') as f:
            data = json.loads(f.read())
            asset_rarities = []

            for asset in data['assets']:
                asset_rarity = 1

                for trait in asset['traits']:
                    trait_rarity = trait['trait_count'] / 8888
                    asset_rarity *= trait_rarity

                asset_rarities.append({
                    'token_id': asset['token_id'],
                    'name': f"Wanderers {asset['token_id']}",
                    'description': asset['description'],
                    'rarity': asset_rarity,
                    'traits': asset['traits'],
                    'image_url': asset['image_url'],
                    'collection': asset['collection']
                })

            assets_sorted = sorted(asset_rarities, key=lambda asset: asset['rarity']) 

            for asset in assets_sorted[:20]:
                render_asset(asset)
                st.subheader(f"{len(asset['traits'])} Traits")
                for trait in asset['traits']:
                    st.write(f"{trait['trait_type']} - {trait['value']} - {trait['trait_count']} have this")
