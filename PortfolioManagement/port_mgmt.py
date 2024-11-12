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

def list_portfolio_stocks(portfolio_id):
    """Fetches and prints all stocks in a given portfolio."""
    connection = create_connection()
    stocks = []
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "symbol", "shares", "purchase_price", "avg_purchase_price" FROM "Stocks" WHERE "portfolio_id" = %s', (portfolio_id,))
            stocks = cursor.fetchall()
            if stocks:
                print("\nStocks in this Portfolio:")
                for idx, stock in enumerate(stocks, start=1):
                    print(f"{idx}. Symbol: {stock[0]}, Shares: {stock[1]}, Latest Purchase Price: ${stock[2]:.2f}, Avg Purchase Price: ${stock[3]:.2f}")
            else:
                print("No stocks found in this portfolio.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)
    return stocks

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
            
            # Display stocks in the portfolio
            list_portfolio_stocks(portfolio_record[0])
            
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

    # Loop until a valid stock symbol is entered
    while True:
        symbol = input("Enter stock symbol: ").upper()
        current_price = get_current_stock_price(symbol)
        if current_price is not None:
            break
        print("Invalid stock symbol. Please try again.")

    # Loop until a valid integer is entered for shares
    while True:
        try:
            shares = int(input("Enter number of shares: "))
            if shares <= 0:
                print("Shares must be a positive integer.")
                continue
            break
        except ValueError:
            print("Invalid input for shares. Please enter a valid integer.")

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            portfolio_id = portfolio[0]

            # Check if the stock already exists
            cursor.execute('SELECT "shares", "avg_purchase_price" FROM "Stocks" WHERE "portfolio_id" = %s AND "symbol" = %s', (portfolio_id, symbol))
            existing_stock = cursor.fetchone()
            if existing_stock:
                # Update shares and calculate new average purchase price
                existing_shares, avg_price = map(float, existing_stock)  # Ensure avg_price is float
                total_cost = avg_price * existing_shares + current_price * shares
                new_shares = existing_shares + shares
                new_avg_price = total_cost / new_shares
                cursor.execute('UPDATE "Stocks" SET "shares" = %s, "purchase_price" = %s, "avg_purchase_price" = %s WHERE "portfolio_id" = %s AND "symbol" = %s',
                               (new_shares, current_price, new_avg_price, portfolio_id, symbol))
                print("Stock updated successfully.")
            else:
                # Insert as a new stock
                stock_id = generate_uuid()
                cursor.execute('INSERT INTO "Stocks" ("stock_id", "user_id", "portfolio_id", "symbol", "shares", "purchase_price", "avg_purchase_price") VALUES (%s, %s, %s, %s, %s, %s, %s)',
                               (stock_id, user_id, portfolio_id, symbol, shares, current_price, current_price))
                print("Stock added successfully.")
            connection.commit()
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

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            portfolio_id = portfolio[0]

            # Display current stocks in the portfolio
            stocks = list_portfolio_stocks(portfolio_id)
            if not stocks:
                print("No stocks found in this portfolio.")
                return

            symbol = input("Enter stock symbol to delete shares from: ").upper()
            cursor.execute('SELECT "shares" FROM "Stocks" WHERE "portfolio_id" = %s AND "symbol" = %s', (portfolio_id, symbol))
            stock = cursor.fetchone()
            if not stock:
                print("Stock not found in this portfolio.")
                return

            current_shares = stock[0]
            delete_shares = int(input(f"Enter number of shares to delete (max {current_shares}): "))
            if delete_shares > current_shares:
                print("Cannot delete more shares than currently owned.")
                return

            if delete_shares < current_shares:
                # Update shares if deleting part of the stock
                new_shares = current_shares - delete_shares
                cursor.execute('UPDATE "Stocks" SET "shares" = %s WHERE "portfolio_id" = %s AND "symbol" = %s',
                               (new_shares, portfolio_id, symbol))
                print(f"{delete_shares} shares deleted successfully.")
            else:
                # Delete stock entry if deleting all shares
                cursor.execute('DELETE FROM "Stocks" WHERE "portfolio_id" = %s AND "symbol" = %s', (portfolio_id, symbol))
                print("Stock deleted successfully.")

            connection.commit()
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)