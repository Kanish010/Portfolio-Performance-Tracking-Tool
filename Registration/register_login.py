# register_login.py
from Registration.auth import register_user, authenticate_user, update_user_profile, get_user_profile, delete_user_profile

def handle_registration():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    response = register_user(username, email, password)
    if response["success"]:
        print("Registration successful.")
    else:
        print("Error:", response["message"])

def handle_login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = authenticate_user(username, password)
    if response["success"]:
        print("Login successful.")
        return response["user_id"]
    else:
        print("Error:", response["message"])
        return None

def handle_view_profile(user_id):
    response = get_user_profile(user_id)
    if response["success"]:
        profile = response["profile"]
        print(f"Username: {profile['username']}")
        print(f"Email: {profile['email']}")
        print(f"Last login: {profile['last_login']}")
    else:
        print("Error:", response["message"])

def handle_update_profile(user_id):
    new_username = input("Enter new username (leave blank to keep current): ")
    new_email = input("Enter new email (leave blank to keep current): ")
    new_password = input("Enter new password (leave blank to keep current): ")
    response = update_user_profile(user_id, new_username or None, new_email or None, new_password or None)
    print(response["message"])

def handle_delete_profile(user_id):
    confirm = input("Are you sure you want to delete your profile? (y/n): ").lower()
    if confirm == 'y':
        response = delete_user_profile(user_id)
        print(response["message"])
        return response["success"]
    return False