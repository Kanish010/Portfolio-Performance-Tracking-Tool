import mysql.connector
import yfinance as yf

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.entered_stocks = []  # Added attribute to hold entered stock symbols

    def historical_stock_data(self, stock):
        """
        Fetches historical stock data using the Yahoo Finance API.

        Args:
            stock (str): The stock symbol.

        Returns:
            pandas.DataFrame: Historical stock data.
        """
        stock = yf.Ticker(stock)
        historical_data = stock.history(period="1d")
        return historical_data
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("Connected to MySQL database successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database.")

    def insert_stock(self, symbol):
        try:
            stock = yf.Ticker(symbol)
            market_price = stock.history(period="1d")["Close"].iloc[-1]
            query = "INSERT INTO Stock (Symbol, MarketPrice) VALUES (%s, %s)"
            values = (symbol, market_price)
            self.cursor.execute(query, values)
            self.connection.commit()
            print("Stock inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error inserting stock: {err}")

    def insert_historical_data(self, stock_id, date, close_price):
        try:
            query = "INSERT INTO HistoricalData (StockID, Date, ClosePrice) VALUES (%s, %s, %s)"
            values = (stock_id, date, close_price)
            self.cursor.execute(query, values)
            self.connection.commit()
            print("Historical data inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error inserting historical data: {err}")

    def insert_stocks_from_gui(self):
        """
        Inserts stocks entered by the user from the GUI.
        """
        for stock_symbol in self.entered_stocks:
            self.insert_stock(stock_symbol.upper())  # Ensure symbols are uppercase

    def set_entered_stocks(self, entered_stocks):
        """
        Sets the list of entered stock symbols.

        Args:
            entered_stocks (list): List of entered stock symbols.
        """
        self.entered_stocks = entered_stocks

# Example usage:
if __name__ == "__main__":
    db_manager = DatabaseManager(
        host="localhost",
        user="root",
        password="password",
        database="Portfolio_Optimization",
    )

    db_manager.connect()
    db_manager.insert_stocks_from_gui()  # Call the method to insert stocks from GUI
    db_manager.disconnect()