import uuid
from psycopg2 import Error
from database import create_connection, close_connection
from PortfolioManagement.stock_price import get_current_stock_price

def generate_uuid():
    """Generates a 6-character UUID for use in primary keys."""
    return str(uuid.uuid4())[:6]

def create_portfolio(user_id, name, description=None):
    """Creates a new portfolio for a user."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        portfolio_id = generate_uuid()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, name))
            if cursor.fetchone():
                return {"success": False, "message": "Portfolio name must be unique within the same user."}
            
            cursor.execute("INSERT INTO \"Portfolios\" (portfolio_id, user_id, name, description) VALUES (%s, %s, %s, %s)",
                           (portfolio_id, user_id, name, description))
            connection.commit()
            return {"success": True, "message": "Portfolio created successfully"}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)

def edit_portfolio(user_id, current_name, new_name=None, new_description=None):
    """Edits an existing portfolio's name or description."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, current_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                return {"success": False, "message": "Portfolio not found."}
            
            portfolio_id = portfolio[0]
            if new_name:
                cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, new_name))
                if cursor.fetchone():
                    return {"success": False, "message": "New portfolio name must be unique within the same user."}

                cursor.execute("UPDATE \"Portfolios\" SET name = %s WHERE portfolio_id = %s", (new_name, portfolio_id))
            if new_description:
                cursor.execute("UPDATE \"Portfolios\" SET description = %s WHERE portfolio_id = %s", (new_description, portfolio_id))
            connection.commit()
            return {"success": True, "message": "Portfolio updated successfully"}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)

def delete_portfolio(user_id, name):
    """Deletes an existing portfolio."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, name))
            portfolio = cursor.fetchone()
            if not portfolio:
                return {"success": False, "message": "Portfolio not found."}
            
            portfolio_id = portfolio[0]
            cursor.execute("DELETE FROM \"Portfolios\" WHERE portfolio_id = %s", (portfolio_id,))
            connection.commit()
            return {"success": True, "message": "Portfolio deleted successfully"}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolio_with_stocks(user_id, name):
    """Fetches the details of a portfolio along with its stocks."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id, user_id, name, description, created_at FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, name))
            portfolio_record = cursor.fetchone()
            if not portfolio_record:
                return {"success": False, "message": "Portfolio not found."}

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
            return {"success": True, "portfolio": portfolio}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)

def view_portfolios(user_id):
    """Fetches all portfolios for a user."""
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
            
            return {"success": True, "portfolios": portfolios} if portfolios else {"success": False, "message": "No portfolios found."}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)

def add_stock(user_id, portfolio_name, symbol, shares):
    """Adds a stock to a specified portfolio."""
    current_price = get_current_stock_price(symbol)
    if current_price is None:
        return {"success": False, "message": "Failed to fetch current stock price. Please check the stock symbol."}
    
    stock_id = generate_uuid()
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                return {"success": False, "message": "Portfolio not found."}
            
            portfolio_id = portfolio[0]
            cursor.execute("INSERT INTO \"Stocks\" (stock_id, user_id, portfolio_id, symbol, shares, purchase_price) VALUES (%s, %s, %s, %s, %s, %s)",
                           (stock_id, user_id, portfolio_id, symbol, shares, current_price))
            connection.commit()
            return {"success": True, "message": "Stock added successfully"}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)

def delete_stock(user_id, portfolio_name, stock_id):
    """Deletes a stock from a specified portfolio."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT portfolio_id FROM \"Portfolios\" WHERE user_id = %s AND name = %s", (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                return {"success": False, "message": "Portfolio not found."}
            
            portfolio_id = portfolio[0]
            cursor.execute("DELETE FROM \"Stocks\" WHERE stock_id = %s AND portfolio_id = %s", (stock_id, portfolio_id))
            connection.commit()
            return {"success": True, "message": "Stock deleted successfully"}
        except Error as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            close_connection(connection)