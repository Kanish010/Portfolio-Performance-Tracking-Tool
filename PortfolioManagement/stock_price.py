import yfinance as yf

def get_current_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        current_price = stock.history(period="1d")['Close'].iloc[0]
        return current_price
    except Exception as e:
        print(f"Error retrieving stock price for {symbol}: {e}")
        return None