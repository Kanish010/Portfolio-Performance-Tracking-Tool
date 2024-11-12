import uuid
from psycopg2 import Error
from database import create_connection, close_connection
from PortfolioManagement.stock_price import get_current_stock_price

def generate_uuid():
    return str(uuid.uuid4())[:6]

def list_user_portfolios(user_id):
    """Fetches and prints all portfolios for a user."""
    connection = create_connection()
    portfolios = []
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "name", "description" FROM "Portfolios" WHERE "user_id" = %s', (user_id,))
            portfolios = cursor.fetchall()
            if portfolios:
                print("\nYour Portfolios:")
                for idx, portfolio in enumerate(portfolios, start=1):
                    print(f"{idx}. Name: {portfolio[0]}, Description: {portfolio[1]}")
            else:
                print("No portfolios found.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)
    return [portfolio[0] for portfolio in portfolios]  # Return a list of portfolio names for further use

def create_portfolio(user_id):
    name = input("Enter portfolio name: ")
    description = input("Enter portfolio description: ")
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        portfolio_id = generate_uuid()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, name))
            if cursor.fetchone():
                print("Portfolio name must be unique within the same user.")
                return
            cursor.execute('INSERT INTO "Portfolios" ("portfolio_id", "user_id", "name", "description") VALUES (%s, %s, %s, %s)',
                           (portfolio_id, user_id, name, description))
            connection.commit()
            print("Portfolio created successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def edit_portfolio(user_id):
    portfolio_names = list_user_portfolios(user_id)
    if not portfolio_names:
        print("You have no portfolios to edit.")
        return
    
    current_name = input("Enter current portfolio name: ")
    if current_name not in portfolio_names:
        print("Invalid portfolio name.")
        return

    new_name = input("Enter new portfolio name (leave blank to keep current): ")
    new_description = input("Enter new description (leave blank to keep current): ")
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, current_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            portfolio_id = portfolio[0]
            if new_name:
                cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, new_name))
                if cursor.fetchone():
                    print("New portfolio name must be unique within the same user.")
                    return
                cursor.execute('UPDATE "Portfolios" SET "name" = %s WHERE "portfolio_id" = %s', (new_name, portfolio_id))
            if new_description:
                cursor.execute('UPDATE "Portfolios" SET "description" = %s WHERE "portfolio_id" = %s', (new_description, portfolio_id))
            connection.commit()
            print("Portfolio updated successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def delete_portfolio(user_id):
    portfolio_names = list_user_portfolios(user_id)
    if not portfolio_names:
        print("You have no portfolios to delete.")
        return
    
    name = input("Enter portfolio name to delete: ")
    if name not in portfolio_names:
        print("Invalid portfolio name.")
        return

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            portfolio_id = portfolio[0]
            cursor.execute('DELETE FROM "Portfolios" WHERE "portfolio_id" = %s', (portfolio_id,))
            connection.commit()
            print("Portfolio deleted successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolio_with_stocks(user_id):
    portfolio_names = list_user_portfolios(user_id)
    if not portfolio_names:
        print("You have no portfolios to view.")
        return
    
    name = input("Enter portfolio name to view: ")
    if name not in portfolio_names:
        print("Invalid portfolio name.")
        return

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id", "name", "description" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, name))
            portfolio_record = cursor.fetchone()
            if not portfolio_record:
                print("Portfolio not found.")
                return
            print("Portfolio Details:")
            print(f"Name: {portfolio_record[1]}")
            print(f"Description: {portfolio_record[2]}")
            print("Stocks in Portfolio:")
            cursor.execute('SELECT "symbol", "shares", "purchase_price" FROM "Stocks" WHERE "portfolio_id" = %s', (portfolio_record[0],))
            for stock in cursor.fetchall():
                print(f"Symbol: {stock[0]}, Shares: {stock[1]}, Purchase Price: ${stock[2]:.2f}")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolios(user_id):
    list_user_portfolios(user_id)

def add_stock(user_id):
    portfolio_names = list_user_portfolios(user_id)
    if not portfolio_names:
        print("You have no portfolios to add stocks to.")
        return

    portfolio_name = input("Enter portfolio name to add stock to: ")
    if portfolio_name not in portfolio_names:
        print("Invalid portfolio name.")
        return

    symbol = input("Enter stock symbol: ")
    shares = float(input("Enter number of shares: "))
    current_price = get_current_stock_price(symbol)
    if current_price is None:
        print("Failed to fetch stock price.")
        return

    stock_id = generate_uuid()
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            cursor.execute('INSERT INTO "Stocks" ("stock_id", "user_id", "portfolio_id", "symbol", "shares", "purchase_price") VALUES (%s, %s, %s, %s, %s, %s)',
                           (stock_id, user_id, portfolio[0], symbol, shares, current_price))
            connection.commit()
            print("Stock added successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def delete_stock(user_id):
    portfolio_names = list_user_portfolios(user_id)
    if not portfolio_names:
        print("You have no portfolios to delete stocks from.")
        return

    portfolio_name = input("Enter portfolio name: ")
    if portfolio_name not in portfolio_names:
        print("Invalid portfolio name.")
        return

    symbol = input("Enter stock symbol to delete: ")
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            cursor.execute('DELETE FROM "Stocks" WHERE "portfolio_id" = %s AND "symbol" = %s', (portfolio[0], symbol))
            connection.commit()
            print("Stock deleted successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)