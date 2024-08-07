# registration_login.py
from Registration.auth import register_user, authenticate_user, update_user_profile, get_user_profile, delete_user_profile

def handle_registration():
    username = input("Enter a username: ").strip()
    email = input("Enter your email: ").strip()
    password = input("Enter a password: ").strip()
    
    response = register_user(username, email, password)
    if not response["success"]:
        print(response["message"])
    else:
        print(f"User {username} registered successfully")
    return response.get("user_id")

def handle_login():
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()
    
    response = authenticate_user(username, password)
    if not response["success"]:
        print(response["message"])
    else:
        print(f"User {username} authenticated successfully")
    return response.get("user_id")

def handle_view_profile(user_id):
    response = get_user_profile(user_id)
    if not response["success"]:
        print(response["message"])
    else:
        profile = response["profile"]
        print(f"Username: {profile['username']}")
        print(f"Email: {profile['email']}")
        print(f"Last Login: {profile['last_login']}")

def handle_update_profile(user_id):
    print("Update Profile Options:")
    new_username = input("Enter new username (leave blank to keep current): ").strip() or None
    new_email = input("Enter new email (leave blank to keep current): ").strip() or None
    new_password = input("Enter new password (leave blank to keep current): ").strip() or None
    
    response = update_user_profile(user_id, new_username, new_email, new_password)
    if not response["success"]:
        print(response["message"])
    else:
        print(response["message"])

def handle_delete_profile(user_id):
    confirmation = input("Are you sure you want to delete your profile? This action cannot be undone. (yes/no): ").strip().lower()
    if confirmation == "yes":
        response = delete_user_profile(user_id)
        if not response["success"]:
            print(response["message"])
        else:
            print(response["message"])
            return True
    else:
        print("Profile deletion cancelled.")
    return False