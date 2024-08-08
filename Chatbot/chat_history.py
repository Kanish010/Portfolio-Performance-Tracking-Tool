import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def close_connection(connection):
    if connection.is_connected():
        connection.close()

def save_message(session_id, role, content, response=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            if role == 'user':
                query = "INSERT INTO ChatHistory (session_id, role, content) VALUES (%s, %s, %s)"
                cursor.execute(query, (session_id, role, content))
            elif role == 'assistant':
                query = "INSERT INTO ChatHistory (session_id, role, content, response) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (session_id, role, "", content))
            connection.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def load_history(session_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "SELECT role, content, response FROM ChatHistory WHERE session_id = %s ORDER BY timestamp"
            cursor.execute(query, (session_id,))
            rows = cursor.fetchall()
            history = []
            for row in rows:
                if row[0] == 'User':
                    history.append({"role": row[0], "content": row[1]})
                elif row[0] == 'Bot':
                    history.append({"role": row[0], "content": row[2]})
            return history
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            close_connection(connection)
    return []