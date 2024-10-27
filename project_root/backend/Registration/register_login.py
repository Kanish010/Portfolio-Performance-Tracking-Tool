# registration_login.py
from Registration.auth import register_user, authenticate_user, update_user_profile, get_user_profile, delete_user_profile

def handle_registration(username, email, password):
    """Registers a new user and returns a response dictionary."""
    response = register_user(username, email, password)
    return response

def handle_login(username, password):
    """Authenticates a user and returns a response dictionary."""
    response = authenticate_user(username, password)
    return response

def handle_view_profile(user_id):
    """Fetches the user's profile and returns a response dictionary."""
    response = get_user_profile(user_id)
    if response["success"]:
        profile = response["profile"]
        return {
            "success": True,
            "profile": {
                "username": profile["username"],
                "email": profile["email"],
                "last_login": profile["last_login"]
            }
        }
    else:
        return {"success": False, "message": response["message"]}

def handle_update_profile(user_id, new_username=None, new_email=None, new_password=None):
    """Updates the user's profile and returns a response dictionary."""
    response = update_user_profile(user_id, new_username, new_email, new_password)
    return response

def handle_delete_profile(user_id):
    """Deletes a user's profile and returns a response dictionary."""
    response = delete_user_profile(user_id)
    if response["success"]:
        return {"success": True, "message": "Profile deleted successfully."}
    else:
        return {"success": False, "message": response["message"]}