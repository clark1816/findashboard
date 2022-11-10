import yfinance as yf
import pandas as pd
from sklearn import linear_model
import streamlit as st

st.header('Stock Price Predictor Using Machine Learing  and Linear Regression')
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

    # print(price_prediction)
    print('code completed')