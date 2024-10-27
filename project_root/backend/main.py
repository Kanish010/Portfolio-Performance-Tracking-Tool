from Registration.register_login import handle_registration, handle_login, handle_view_profile, handle_update_profile, handle_delete_profile
from PortfolioManagement.port_mgmt import create_portfolio, edit_portfolio, delete_portfolio, view_portfolio_with_stocks, view_portfolios, add_stock, delete_stock

def profile_menu(user_id):
    while True:
        print("\nProfile Management:")
        print("1. View Profile")
        print("2. Update Profile")
        print("3. Delete Profile")
        print("4. Back to Main Menu")
        user_choice = input("Enter your choice: ").strip()
        
        if user_choice == '1':
            handle_view_profile(user_id)
        elif user_choice == '2':
            handle_update_profile(user_id)
        elif user_choice == '3':
            if handle_delete_profile(user_id):
                print("Account deleted successfully. You are now logged out.")
                return None  # Indicate tåhat the user should be logged out
        elif user_choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")
    return user_id  # Return user_id if still logged in

def portfolio_management_menu(user_id):
    while True:
        print("\nPortfolio Management:")
        print("1. Create Portfolio")
        print("2. Edit Portfolio")
        print("3. Delete Portfolio")
        print("4. View Portfolio")
        print("5. Add Stock to Portfolio")
        print("6. Delete Stock from Portfolio")
        print("7. Back to User Menu")
        user_choice = input("Enter your choice: ").strip()
        
        if user_choice == '1':
            create_portfolio(user_id)
        elif user_choice == '2':
            edit_portfolio(user_id)
        elif user_choice == '3':
            delete_portfolio(user_id)
        elif user_choice == '4':
            view_portfolio_with_stocks(user_id)
        elif user_choice == '5':
            add_stock(user_id)
        elif user_choice == '6':
            delete_stock(user_id)
        elif user_choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    print("Welcome to the Portfolio Performance Tracking Tool")
    while True:
        print("\nMain Menu:")
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
                    print("\nUser Menu:")
                    print("1. Profile Management")
                    print("2. Portfolio Management")
                    print("3. Logout")
                    user_choice = input("Enter your choice: ").strip()
                    
                    if user_choice == '1':
                        user_id = profile_menu(user_id)
                        if user_id is None:
                            break  # Exit to main menu if user is logged out by deletion
                    elif user_choice == '2':
                        portfolio_management_menu(user_id)
                    elif user_choice == '3':
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