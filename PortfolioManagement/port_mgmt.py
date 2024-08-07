import uuid
from mysql.connector import Error
from database import create_connection, close_connection
from PortfolioManagement.stock_price import get_current_stock_price

def generate_uuid():
    return str(uuid.uuid4())[:6]

def create_portfolio(user_id, name, description=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        portfolio_id = generate_uuid()
        try:
            cursor.execute(
                "SELECT portfolio_id FROM Portfolios WHERE user_id = %s AND name = %s", (user_id, name))
            if cursor.fetchone():
                return {"success": False, "message": "Portfolio name must be unique within the same user."}

            cursor.execute(
                "INSERT INTO Portfolios (portfolio_id, user_id, name, description) VALUES (%s, %s, %s, %s)",
                (portfolio_id, user_id, name, description)
            )
            connection.commit()
            print("Portfolio created successfully")
            return {"success": True, "portfolio_id": portfolio_id}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during portfolio creation."}
        finally:
            cursor.close()
            close_connection(connection)

def edit_portfolio(user_id, name, new_name=None, description=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM Portfolios WHERE user_id = %s AND name = %s", (user_id, name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Error: Portfolio not found.")
                return {"success": False, "message": "Portfolio not found."}

            portfolio_id = portfolio[0]
            if new_name:
                cursor.execute(
                    "SELECT portfolio_id FROM Portfolios WHERE user_id = %s AND name = %s", (user_id, new_name))
                if cursor.fetchone():
                    return {"success": False, "message": "New portfolio name must be unique within the same user."}

                cursor.execute("UPDATE Portfolios SET name = %s WHERE portfolio_id = %s", (new_name, portfolio_id))
            if description:
                cursor.execute("UPDATE Portfolios SET description = %s WHERE portfolio_id = %s", (description, portfolio_id))
            connection.commit()
            print("Portfolio updated successfully")
            return {"success": True}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during portfolio update."}
        finally:
            cursor.close()
            close_connection(connection)

def delete_portfolio(user_id, name):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM Portfolios WHERE user_id = %s AND name = %s", (user_id, name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Error: Portfolio not found.")
                return {"success": False, "message": "Portfolio not found."}

            portfolio_id = portfolio[0]
            cursor.execute("DELETE FROM Portfolios WHERE portfolio_id = %s", (portfolio_id,))
            connection.commit()
            print("Portfolio deleted successfully")
            return {"success": True}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during portfolio deletion."}
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolio_with_stocks(user_id, name):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id, user_id, name, description, created_at FROM Portfolios WHERE user_id = %s AND name = %s", (user_id, name))
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
                
                cursor.execute("SELECT stock_id, symbol, shares, purchase_price, total_value, purchase_date FROM Stocks WHERE portfolio_id = %s", (portfolio["portfolio_id"],))
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
                return {"success": True, "portfolio": portfolio}
            else:
                return {"success": False, "message": "Portfolio not found."}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred while retrieving the portfolio."}
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolios(user_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id, name, description, created_at FROM Portfolios WHERE user_id = %s", (user_id,))
            records = cursor.fetchall()
            portfolios = []
            for record in records:
                portfolios.append({
                    "portfolio_id": record[0],
                    "name": record[1],
                    "description": record[2],
                    "created_at": record[3]
                })
            return {"success": True, "portfolios": portfolios}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during portfolio listing."}
        finally:
            cursor.close()
            close_connection(connection)

def add_stock(user_id, portfolio_name, symbol, shares):
    current_price = get_current_stock_price(symbol)
    if current_price is None:
        return {"success": False, "message": "Failed to fetch current stock price."}
    
    stock_id = generate_uuid()
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM Portfolios WHERE user_id = %s AND name = %s", (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                print("Error: Portfolio not found.")
                return {"success": False, "message": "Portfolio not found."}
            
            portfolio_id = portfolio[0]
            cursor.execute(
                "INSERT INTO Stocks (stock_id, user_id, portfolio_id, symbol, shares, purchase_price) VALUES (%s, %s, %s, %s, %s, %s)",
                (stock_id, user_id, portfolio_id, symbol, shares, current_price)
            )
            connection.commit()
            print("Stock added successfully")
            return {"success": True}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred while adding the stock."}
        finally:
            cursor.close()
            close_connection(connection)

def delete_stock(user_id, stock_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT stock_id FROM Stocks WHERE stock_id = %s AND user_id = %s", (stock_id, user_id))
            stock = cursor.fetchone()
            if not stock:
                return {"success": False, "message": "Stock not found or you do not have permission to delete this stock."}
                
            cursor.execute("DELETE FROM Stocks WHERE stock_id = %s AND user_id = %s", (stock_id, user_id))
            connection.commit()
            print("Stock deleted successfully")
            return {"success": True}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred while deleting the stock."}
        finally:
            cursor.close()
            close_connection(connection)

def handle_create_portfolio(user_id):
    name = input("Enter portfolio name: ").strip()
    description = input("Enter portfolio description (optional): ").strip()
    
    response = create_portfolio(user_id, name, description)
    if not response["success"]:
        print(response["message"])
    else:
        print(f"Portfolio '{name}' created successfully")

def handle_edit_portfolio(user_id):
    response = view_portfolios(user_id)
    if not response["success"]:
        print(response["message"])
        return

    portfolios = response["portfolios"]
    print("Your Portfolios:")
    for portfolio in portfolios:
        print(f"Portfolio Name: {portfolio['name']}")

    name = input("Enter portfolio name to edit: ").strip()
    new_name = input("Enter new portfolio name (leave blank to keep current): ").strip() or None
    description = input("Enter new portfolio description (leave blank to keep current): ").strip() or None
    
    response = edit_portfolio(user_id, name, new_name, description)
    if not response["success"]:
        print(response["message"])
    else:
        print("Portfolio updated successfully")

def handle_delete_portfolio(user_id):
    response = view_portfolios(user_id)
    if not response["success"]:
        print(response["message"])
        return

    portfolios = response["portfolios"]
    print("Your Portfolios:")
    for portfolio in portfolios:
        print(f"Portfolio Name: {portfolio['name']}")

    name = input("Enter portfolio name to delete: ").strip()
    confirmation = input("Are you sure you want to delete this portfolio? This action cannot be undone. (yes/no): ").strip().lower()
    if confirmation == "yes":
        response = delete_portfolio(user_id, name)
        if not response["success"]:
            print(response["message"])
        else:
            print("Portfolio deleted successfully")
    else:
        print("Portfolio deletion cancelled.")

def handle_view_portfolio(user_id):
    response = view_portfolios(user_id)
    if not response["success"]:
        print(response["message"])
        return

    portfolios = response["portfolios"]
    print("Your Portfolios:")
    for portfolio in portfolios:
        print(f"Portfolio Name: {portfolio['name']}")

    name = input("Enter portfolio name to view: ").strip()
    response = view_portfolio_with_stocks(user_id, name)
    if not response["success"]:
        print(response["message"])
    else:
        portfolio = response["portfolio"]
        print(f"Portfolio ID: {portfolio['portfolio_id']}")
        print(f"User ID: {portfolio['user_id']}")
        print(f"Name: {portfolio['name']}")
        print(f"Description: {portfolio['description']}")
        print(f"Created At: {portfolio['created_at']}")
        print("Stocks:")
        for stock in portfolio["stocks"]:
            print(f"  Stock ID: {stock['stock_id']}, Symbol: {stock['symbol']}, Shares: {stock['shares']}, Purchase Price: {stock['purchase_price']}, Total Value: {stock['total_value']}, Purchase Date: {stock['purchase_date']}")

def handle_add_stock(user_id):
    response = view_portfolios(user_id)
    if not response["success"]:
        print(response["message"])
        return

    portfolios = response["portfolios"]
    print("Your Portfolios:")
    for portfolio in portfolios:
        print(f"Portfolio Name: {portfolio['name']}")

    portfolio_name = input("Enter portfolio name to add stock: ").strip()
    while True:
        symbol = input("Enter stock symbol: ").strip().upper()
        current_price = get_current_stock_price(symbol)
        if current_price is not None:
            break
        else:
            print("Invalid stock symbol. Please try again.")
    
    while True:
        try:
            shares = int(input("Enter number of shares: ").strip())
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer for the number of shares.")
    
    response = add_stock(user_id, portfolio_name, symbol, shares)
    if not response["success"]:
        print(response["message"])
    else:
        print(f"Stock {symbol} added successfully to portfolio '{portfolio_name}'")

def handle_delete_stock(user_id):
    response = view_portfolios(user_id)
    if not response["success"]:
        print(response["message"])
        return

    portfolios = response["portfolios"]
    print("Your Portfolios:")
    for portfolio in portfolios:
        print(f"Portfolio Name: {portfolio['name']}")

    portfolio_name = input("Enter portfolio name to delete stock from: ").strip()
    response = view_portfolio_with_stocks(user_id, portfolio_name)
    if not response["success"]:
        print(response["message"])
        return

    portfolio = response["portfolio"]
    print("Stocks:")
    for stock in portfolio["stocks"]:
        print(f"Stock ID: {stock['stock_id']}, Symbol: {stock['symbol']}, Shares: {stock['shares']}")

    stock_id = input("Enter stock ID to delete: ").strip()
    confirmation = input("Are you sure you want to delete this stock? This action cannot be undone. (yes/no): ").strip().lower()
    if confirmation == "yes":
        response = delete_stock(user_id, stock_id)
        if not response["success"]:
            print(response["message"])
        else:
            print("Stock deleted successfully")
    else:
        print("Stock deletion cancelled.")