import uuid
from psycopg2 import Error
from database import create_connection, close_connection
from PortfolioManagement.stock_price import get_current_stock_price

def generate_uuid():
    """Generates a 6-character UUID for use in primary keys."""
    return str(uuid.uuid4())[:6]

def input_integer(prompt):
    """Helper function to get a valid integer input from the user."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def create_portfolio(user_id):
    """Handles user input and database insertion for creating a portfolio."""
    name = input("Enter portfolio name: ").strip()
    description = input("Enter portfolio description (optional): ").strip() or None
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        portfolio_id = generate_uuid()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, name))
            if cursor.fetchone():
                print("Portfolio name must be unique within the same user.")
                return
            
            cursor.execute("INSERT INTO \"Portfolios\" (portfolio_id, user_id, name, description) VALUES (%s, %s, %s, %s)",
                           (portfolio_id, user_id, name, description))
            connection.commit()
            print("Portfolio created successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def edit_portfolio(user_id):
    """Handles user input and database updating for editing a portfolio."""
    portfolios = view_portfolios(user_id, display=True)
    if not portfolios:
        print("No portfolios found.")
        return
    
    current_name = input("Enter the current portfolio name to edit: ").strip()
    new_name = input("Enter new portfolio name (leave blank to keep current): ").strip() or None
    new_description = input("Enter new portfolio description (leave blank to keep current): ").strip() or None
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, current_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            
            portfolio_id = portfolio[0]
            if new_name:
                cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, new_name))
                if cursor.fetchone():
                    print("New portfolio name must be unique within the same user.")
                    return

                cursor.execute("UPDATE \"Portfolios\" SET name = %s WHERE portfolio_id = %s", (new_name, portfolio_id))
            if new_description:
                cursor.execute("UPDATE \"Portfolios\" SET description = %s WHERE portfolio_id = %s", (new_description, portfolio_id))
            connection.commit()
            print("Portfolio updated successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def delete_portfolio(user_id):
    """Handles user input and database deletion for deleting a portfolio."""
    portfolios = view_portfolios(user_id, display=True)
    if not portfolios:
        print("No portfolios found.")
        return
    
    name = input("Enter the portfolio name to delete: ").strip()
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            
            portfolio_id = portfolio[0]
            cursor.execute("DELETE FROM \"Portfolios\" WHERE portfolio_id = %s", (portfolio_id,))
            connection.commit()
            print("Portfolio deleted successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolio_with_stocks(user_id):
    """Handles user input and displays the stocks within a selected portfolio."""
    portfolios = view_portfolios(user_id, display=True)
    if not portfolios:
        print("No portfolios found.")
        return
    
    name = input("Enter the portfolio name to view: ").strip()
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id, user_id, name, description, created_at FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, name))
            portfolio_record = cursor.fetchone()
            if portfolio_record:
                portfolio = {
                    "portfolio_id": portfolio_record[0],
                    "user_id": portfolio_record[1],
                    "name": portfolio_record[2],
                    "description": portfolio_record[3],
                    "created_at": portfolio_record[4],
                    "stocks": []
                }
                
                cursor.execute("SELECT stock_id, symbol, shares, purchase_price, total_value, purchase_date FROM \"Stocks\" WHERE portfolio_id = %s", (portfolio["portfolio_id"],))
                stock_records = cursor.fetchall()
                for stock_record in stock_records:
                    portfolio["stocks"].append({
                        "stock_id": stock_record[0],
                        "symbol": stock_record[1],
                        "shares": stock_record[2],
                        "purchase_price": stock_record[3],
                        "total_value": stock_record[4],
                        "purchase_date": stock_record[5]
                    })
                print(f"\nPortfolio: {portfolio['name']}")
                print(f"Description: {portfolio['description']}")
                print(f"Created At: {portfolio['created_at']}")
                print("Stocks in Portfolio:")
                if portfolio["stocks"]:
                    for stock in portfolio["stocks"]:
                        print(f"  - Stock ID: {stock['stock_id']}, Symbol: {stock['symbol']}, Shares: {stock['shares']}, "
                              f"Purchase Price: {stock['purchase_price']}, Total Value: {stock['total_value']}, "
                              f"Purchase Date: {stock['purchase_date']}")
                else:
                    print("  No stocks in this portfolio.")
            else:
                print("Portfolio not found.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolios(user_id, display=True):
    """Fetches and optionally displays all portfolios for a user."""
    connection = create_connection()
    portfolios = []
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id, name, description, created_at FROM \"Portfolios\" WHERE user_id = %s", (user_id,))
            records = cursor.fetchall()
            portfolios = [{
                "portfolio_id": record[0],
                "name": record[1],
                "description": record[2],
                "created_at": record[3]
            } for record in records]
            
            if display and portfolios:
                print("\nYour Portfolios:")
                for portfolio in portfolios:
                    print(f"- {portfolio['name']}")
            elif not portfolios:
                print("No portfolios found.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)
    return portfolios

def add_stock(user_id):
    """Handles user input and database insertion for adding a stock to a portfolio."""
    portfolios = view_portfolios(user_id, display=True)
    if not portfolios:
        print("No portfolios found.")
        return
    
    portfolio_name = input("Enter the portfolio name to add stock to: ").strip()
    symbol = input("Enter stock symbol: ").strip().upper()
    shares = input_integer("Enter number of shares: ")
    
    current_price = get_current_stock_price(symbol)
    if current_price is None:
        print("Failed to fetch current stock price. Please check the stock symbol.")
        return
    
    stock_id = generate_uuid()
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            
            portfolio_id = portfolio[0]
            cursor.execute("INSERT INTO \"Stocks\" (stock_id, user_id, portfolio_id, symbol, shares, purchase_price) VALUES (%s, %s, %s, %s, %s, %s)",
                           (stock_id, user_id, portfolio_id, symbol, shares, current_price))
            connection.commit()
            print("Stock added successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def delete_stock(user_id):
    """Handles user input and database deletion for deleting a stock from a portfolio."""
    portfolios = view_portfolios(user_id, display=True)
    if not portfolios:
        print("No portfolios found.")
        return
    
    portfolio_name = input("Enter the portfolio name to delete stock from: ").strip()
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Portfolio not found.")
                return
            
            portfolio_id = portfolio[0]
            cursor.execute("SELECT stock_id, symbol FROM \"Stocks\" WHERE portfolio_id = %s", (portfolio_id,))
            stocks = cursor.fetchall()
            if not stocks:
                print("No stocks found in this portfolio.")
                return
            
            print("\nStocks in Portfolio:")
            for stock in stocks:
                print(f"- Stock ID: {stock[0]}, Symbol: {stock[1]}")
                
            stock_id = input("Enter the stock ID to delete: ").strip()
            cursor.execute("DELETE FROM \"Stocks\" WHERE stock_id = %s AND user_id = %s", (stock_id, user_id))
            connection.commit()
            print("Stock deleted successfully.")
        except Error as e:
            print(f"Database Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def portfolio_menu(user_id):
    """Directs to portfolio management options based on user choice using a loop."""
    menu_options = {
        '1': create_portfolio,
        '2': edit_portfolio,
        '3': delete_portfolio,
        '4': view_portfolio_with_stocks,
        '5': add_stock,
        '6': delete_stock,
        '7': lambda user_id: print("Returning to Main Menu.")
    }
    
    while True:
        print("\nPortfolio Management:")
        print("1. Create Portfolio")
        print("2. Edit Portfolio")
        print("3. Delete Portfolio")
        print("4. View Portfolio")
        print("5. Add Stock to Portfolio")
        print("6. Delete Stock from Portfolio")
        print("7. Back to Main Menu")
        
        user_choice = input("Enter your choice: ").strip()
        
        if user_choice in menu_options:
            if user_choice == '7':  # Break the loop to go back to the main menu
                menu_options[user_choice](user_id)
                break
            else:
                menu_options[user_choice](user_id)
        else:
            print("Invalid choice. Please try again.")