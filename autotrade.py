import time
import pyupbit
import datetime
import telepot

access = "your-access"
secret = "your-secret"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

#원화로 거래 되는 ticker 가져오기
tickers = pyupbit.get_tickers("KRW")
tickers.sort()


# 텔레그램으로 메세지 보내기
token="1269160830:AAFshIib8P2nICaScQwru0r8Pn1LCVGmtCs"
mc = "497235997"
bot = telepot.Bot(token)



# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)


        if start_time < now < end_time - datetime.timedelta(seconds=10):
            for ticker in tickers :
                target_price = get_target_price(ticker, 0.5)
                ma15 = get_ma15(ticker)
                current_price = get_current_price(ticker)

                if target_price < current_price and ma15 < current_price:
                    unit = upbit.get_amount('ALL')+ upbit.get_balance()
                    unit1 = unit // 500000 * 10000
                    krw = get_balance("KRW")

                    if krw > unit1 and upbit.get_balance(ticker) is None:
                        upbit.buy_market_order(ticker, unit1)
                        bot.sendMessage(mc, "%s를 매수합니다. " % ticker[4:])

                time.sleep(0.1)
        else:
            for ticker in tickers:
                if upbit.get_balance(ticker) is not None:
                    upbit.sell_market_order(ticker, upbit.get_balance(ticker))
                    bot.sendMessage(mc, "%s를 매도합니다. " % ticker[4:])
                time.sleep(0.1)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)