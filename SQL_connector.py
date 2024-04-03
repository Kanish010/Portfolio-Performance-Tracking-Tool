import mysql.connector

class DatabaseManager:
    """
    Handles database operations for storing stock symbols, their historical data, and portfolio information.

    Attributes:
        host (str): Hostname for the MySQL database.
        user (str): Username for accessing the MySQL database.
        password (str): Password for accessing the MySQL database.
        database (str): Name of the MySQL database.
    """
    def __init__(self, host="localhost", user="root", password="password", database="PortfolioOptimization"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def insert_stock_data(self, symbol, market_price):
        """
        Inserts stock symbol and market price into the database.

        Args:
            symbol (str): Stock symbol.
            market_price (float): Market price of the stock.
        """
        db_connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = db_connection.cursor()
        sql = "INSERT INTO Stock (Symbol, MarketPrice) VALUES (%s, %s)"
        cursor.execute(sql, (symbol, market_price))
        db_connection.commit()
        cursor.close()
        db_connection.close()

    def insert_portfolio(self, name):
        """
        Inserts portfolio information into the database.

        Args:
            name (str): Name of the portfolio.
        """
        db_connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        cursor = db_connection.cursor()
        sql = "INSERT INTO Portfolio (Name) VALUES (%s)"
        cursor.execute(sql, (name,))
        db_connection.commit()
        cursor.close()
        db_connection.close()