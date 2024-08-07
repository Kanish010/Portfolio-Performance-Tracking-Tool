# main.py
from registration_login import handle_registration, handle_login, handle_view_profile, handle_update_profile, handle_delete_profile

def main():
    print("Welcome to the Portfolio Performance Tracking Tool")
    while True:
        print("\nOptions:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            user_id = handle_registration()
        elif choice == '2':
            user_id = handle_login()
            if user_id:
                while True:
                    print("\nUser Options:")
                    print("1. View Profile")
                    print("2. Update Profile")
                    print("3. Delete Profile")
                    print("4. Logout")
                    user_choice = input("Enter your choice: ").strip()
                    
                    if user_choice == '1':
                        handle_view_profile(user_id)
                    elif user_choice == '2':
                        handle_update_profile(user_id)
                    elif user_choice == '3':
                        if handle_delete_profile(user_id):
                            break
                    elif user_choice == '4':
                        print("Logged out successfully.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()