import mysql.connector

class DatabaseManager:
    """
    Handles database operations for storing portfolio information.

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

    def insert_portfolio(self, optimization_method):
        """
        Inserts portfolio information into the database.

        Args:
            optimization_method (str): Optimization method used.

        Returns:
            int: The ID of the newly inserted portfolio.
        """
        try:
            db_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = db_connection.cursor()
            sql = "INSERT INTO Portfolios (OptimizationMethod) VALUES (%s)"
            print(f"Executing SQL: {sql} with value {optimization_method}")  # Debug print
            cursor.execute(sql, (optimization_method,))
            portfolio_id = cursor.lastrowid  # Get the ID of the newly inserted portfolio
            db_connection.commit()
            cursor.close()
            db_connection.close()
            print(f"Inserted portfolio with ID {portfolio_id} and method {optimization_method}")  # Debug print
            return portfolio_id
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Debug print
            return None

    def insert_portfolio_stock(self, portfolio_id, stock_ticker, stock_weight):
        """
        Inserts a stock into a portfolio with its weight.

        Args:
            portfolio_id (int): ID of the portfolio.
            stock_ticker (str): Stock ticker symbol.
            stock_weight (float): Weight of the stock in the portfolio.
        """
        try:
            db_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = db_connection.cursor()
            sql = "INSERT INTO PortfolioStocks (PortfolioID, StockTicker, StockWeight) VALUES (%s, %s, %s)"
            print(f"Executing SQL: {sql} with values {portfolio_id}, {stock_ticker}, {stock_weight}")  # Debug print
            cursor.execute(sql, (portfolio_id, stock_ticker, stock_weight))
            db_connection.commit()
            cursor.close()
            db_connection.close()
            print(f"Inserted stock {stock_ticker} into portfolio {portfolio_id} with weight {stock_weight}")  # Debug print
        except mysql.connector.Error as err:
            print(f"Error: {err}")  # Debug print

    def close(self):
        """
        Closes the database connection.
        """
        pass  # Connection is closed in each method after committing changes