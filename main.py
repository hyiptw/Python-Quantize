# # Auto Trader

import os
import time
import ccxt
import config
import LineBot
import asyncio
from pprint import pprint


# # Parameter
delay = 2
trade_coin = ['BTC', 'ETH', 'LTC', 'NEO'] # Multiple
quote_coin = 'USDT'
good_exchange = ['binance', 'okex', 'bitfinex' , 'huobipro', 'hitbtc']

# # Create exchanges list
def get_list(good_exchange):
    exchange_list = []
    for name in good_exchange:
        exchange = getattr(ccxt,name)()
        if exchange :
            exchange_list.append(exchange)
    return exchange_list

# # Proxy set
def set_proxy():
    os.environ.setdefault('http_proxy', 'http://127.0.0.1:1080')
    os.environ.setdefault('https_proxy', 'http://127.0.0.1:1080')

# # Strategy 
async def find_trade_object(symbol,exlist,base):
    pass
    max_bid1 = 0        # Initial max
    min_ask1 = 100000   # Initial min
    bid_exchange = None
    ask_exchange = None
    bid_time = None
    ask_time = None
    bid_amount = None
    ask_amount = None
    for exchange in exlist:
        #獲取市場交易對數據
        try:
            orderbook = exchange.fetch_order_book(symbol)
        except Exception as e:
            #Debug用
            print('Error! fetch_order_book exception is {},exchange is {},symbol is {}'.format(e.args[0], exchange.name, symbol))
            continue
        date_time = exchange.last_response_headers['Date']
        bid1 = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        bid1_amount = orderbook['bids'][0][1] if len(orderbook['bids']) > 0 else None
        ask1 = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        ask1_amount = orderbook['asks'][0][1] if len(orderbook['asks']) > 0 else None
        print('exchange {} bid1 ask1 is \n-> {}|{}   {}|{}\ndate_time is {}'.format(exchange.name, bid1, bid1_amount,
                                                                                      ask1, ask1_amount, date_time))
        #找到最貴的買一，進行賣操作
        if bid1 and (bid1 > max_bid1):
            max_bid1 = bid1
            bid_exchange = exchange
            bid_time = date_time
            bid_amount = bid1_amount
            print('get new max_bid1 is {}|exchange is {}\ndate_time is {}'.format(max_bid1, exchange.name, date_time))
        #找到最便宜的買一，進行買操作
        if ask1 and (ask1 < min_ask1):
            min_ask1 = ask1
            ask_exchange = exchange
            ask_time = date_time
            ask_amount = ask1_amount
            print('get new min_ask1 is {}|exchange is {}\ndate_time is {}'.format(min_ask1, exchange.name, date_time))
        time.sleep(delay)
 
    # 獲利計算
    if bid_exchange and ask_exchange:
        price_diff = max_bid1 - min_ask1
        percent = price_diff / min_ask1 * 100
        trade_volume = min(ask_amount,bid_amount)
        profits = min_ask1 * trade_volume * percent/100
        print('\n\n-------symbol {} find good exchange\npercent {}% |price_diff {} |trade_volume {} |profits {}'
              '\nbuy  at {}\t|{}\t|{}\t|{}\nsell at {}\t|{}\t|{}\t|{}'.
              format(symbol,percent,price_diff,trade_volume,profits, min_ask1,ask_amount,min_ask1*ask_amount,ask_exchange.name,
                     max_bid1,bid_amount,max_bid1*bid_amount,bid_exchange.name))
        if price_diff > 0:
            v1 = '當前交易對: ' + str(symbol) + '<br><br>在 ' + ask_exchange.name + ' 買入價格' + str(min_ask1) + ' 的' + str(base) + ' ' + str(trade_volume) + '顆<br>' + '<br>在 ' + bid_exchange.name + ' 賣出價格' + str(max_bid1) + ' 的' + str(base) + ' ' + str(trade_volume) + '顆' + '<br><br>價差:<br>' + str(price_diff) + '<br>利潤率(%):<br>' + str(percent) + '<br>利潤:<br>' + str(profits)
            LineBot.send_ifttt(v1)
        
        if price_diff < 0:
            print('oooooooo unlucky symbol {},no pair to make money'.format(symbol))
            v1 = '當前交易對: ' + str(symbol) + '<br><br>並不存在可套利機會'
            LineBot.send_ifttt(v1)
        return percent,price_diff,trade_volume,profits, min_ask1,ask_amount,min_ask1*ask_amount, ask_exchange.name,ask_time,\
               max_bid1,bid_amount,max_bid1*bid_amount,bid_exchange.name,bid_time
    else :
        print('\n\n******------ symbol {} not find good exchange'.format(symbol))
        return min_ask1,None,max_bid1,None
    
# # Main 
if __name__ == '__main__':

    # UI 
    print('-----------Parameters---------------\n')
    print('exchange list is {}\ntrade coin is {}\nquote coin is {}'.format(good_exchange,trade_coin,quote_coin))
    print('\n-----------Parameters---------------')

    #set_proxy() # Set up proxy first
    exlist = get_list(good_exchange) # get list
    
    for base in trade_coin:
        symbol = base + '/' + quote_coin # BTC/USDT 
        print('\n-------start async version | trade coin is {} | symbol is {}\n'.format(base,symbol))
        #while True:
        asyncio.get_event_loop().run_until_complete(find_trade_object(symbol,exlist,base))
    print('\n-----------all over---------------')
