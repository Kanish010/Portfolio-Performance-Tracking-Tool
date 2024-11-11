# auth.py
import bcrypt
from psycopg2 import Error
from database import create_connection, close_connection
from datetime import datetime

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, email, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        try:
            cursor.execute('SELECT "user_id" FROM "Users" WHERE "username" = %s', (username,))
            if cursor.fetchone():
                return {"success": False, "message": "Username already exists."}
            
            cursor.execute('SELECT "user_id" FROM "Users" WHERE "email" = %s', (email,))
            if cursor.fetchone():
                return {"success": False, "message": "Email already exists."}
            
            cursor.execute(
                'INSERT INTO "Users" ("username", "email", "password_hash") VALUES (%s, %s, %s) RETURNING "user_id"',
                (username, email, hashed_password)
            )
            user_id = cursor.fetchone()[0]
            connection.commit()
            return {"success": True, "user_id": user_id}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during registration."}
        finally:
            cursor.close()
            close_connection(connection)

def authenticate_user(username, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "user_id", "password_hash" FROM "Users" WHERE "username" = %s', (username,))
            record = cursor.fetchone()
            if not record or not verify_password(password, record[1]):
                return {"success": False, "message": "Invalid username or password."}
            
            cursor.execute(
                'UPDATE "Users" SET "last_login" = %s WHERE "user_id" = %s',
                (datetime.now(), record[0])
            )
            connection.commit()
            return {"success": True, "user_id": record[0]}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during authentication."}
        finally:
            cursor.close()
            close_connection(connection)

def update_user_profile(user_id, new_username=None, new_email=None, new_password=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            if new_username:
                cursor.execute('UPDATE "Users" SET "username" = %s WHERE "user_id" = %s', (new_username, user_id))
            if new_email:
                cursor.execute('UPDATE "Users" SET "email" = %s WHERE "user_id" = %s', (new_email, user_id))
            if new_password:
                hashed_password = hash_password(new_password)
                cursor.execute('UPDATE "Users" SET "password_hash" = %s WHERE "user_id" = %s', (hashed_password, user_id))
            connection.commit()
            return {"success": True, "message": "Profile updated successfully."}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during profile update."}
        finally:
            cursor.close()
            close_connection(connection)

def get_user_profile(user_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT "username", "email", "last_login" FROM "Users" WHERE "user_id" = %s', (user_id,))
            record = cursor.fetchone()
            if record:
                return {"success": True, "profile": {"username": record[0], "email": record[1], "last_login": record[2]}}
            else:
                return {"success": False, "message": "User not found."}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during profile retrieval."}
        finally:
            cursor.close()
            close_connection(connection)

def delete_user_profile(user_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute('DELETE FROM "Users" WHERE "user_id" = %s', (user_id,))
            connection.commit()
            return {"success": True, "message": "Profile deleted successfully."}
        except Error as e:
            print(f"Database Error: {e}")
            return {"success": False, "message": "An error occurred during profile deletion."}
        finally:
            cursor.close()
            close_connection(connection)