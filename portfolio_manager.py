from collections import Counter
from datetime import datetime

import yfinance as yf

import utils.json_simplifier as json_simp
import yf_extender as yf_ext
from utils import alerts

purchased = {}
sold = {}


def buy_stock(ticker: yf.Ticker, quantity: int):
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    json_simp.read_json()

    if ticker_symbol not in purchased:
        stock_info = yf_ext.get_stock_state(ticker)
        stock_info['Quantity'] = quantity
        purchased[ticker_symbol] = stock_info
        print("Buying", ticker_symbol)
        alerts.sayBeep(1)

    json_simp.updated_purchased()
    json_simp.read_json()


def sell_stock(ticker: yf.Ticker):
    ticker_symbol = yf_ext.get_ticker_symbol(ticker)
    json_simp.read_json()

    if ticker_symbol not in sold:
        stock_info = Counter(yf_ext.get_stock_state(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        stock_info.subtract(purchase_info)
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info

    elif ticker_symbol in purchased:
        stock_info = Counter(yf_ext.get_stock_state(ticker))
        purchase_info = Counter(purchased.pop(ticker_symbol))
        sold_info = Counter(sold.pop(ticker_symbol))
        stock_info.pop('Time')
        purchase_info.pop('Time')
        sold_info.pop('Time')
        stock_info.subtract(purchase_info)

        for i in stock_info and sold_info:
            stock_info[i] = stock_info[i] + sold_info[i]
        stock_info['Time'] = datetime.now().strftime("%H:%M:%S")
        sold[ticker_symbol] = stock_info

    json_simp.updated_purchased()
    json_simp.updated_sold()
    json_simp.read_json()
    print("Selling", ticker_symbol)
    alerts.sayBeep(2)


def get_position_polarity() -> float:
    json_simp.read_json()

    polarity = 0.0
    print("Holding")
    for i in purchased:
        stock_polarity = yf_ext.get_stock_state(yf.Ticker(i))['Close'] - purchased[i]['Close']
        polarity += stock_polarity
        print("{0} {1}".format(i, stock_polarity))
    print("Holding Position polarity {0}".format(polarity))
    print("Sold")
    polarity = 0.0
    for i in sold:
        stock_polarity = sold[i]['Close']
        polarity += stock_polarity
        print("{0} {1}".format(i, stock_polarity))
    print("Sold Position polarity {0}".format(polarity))
    return polarity


def print_adjusted_position_polarity():
    json_simp.read_json()

    polarity = 0.0
    print("Holding")
    for i in purchased:
        stock_polarity = (yf_ext.get_stock_state(yf.Ticker(i))['Close'] - purchased[i]['Close']) * purchased[i]['Quantity']
        polarity += stock_polarity
        print("{0} {1}".format(i, stock_polarity))
    print("Holding Position profits {0}".format(polarity))
    print("Sold")
    polarity = 0.0
    for i in sold:
        stock_polarity = sold[i]['Close'] * abs(sold[i]['Quantity'])
        polarity += stock_polarity
        print("{0} {1}".format(i, stock_polarity))
    print("Sold Position profits {0}".format(polarity))
