import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import sys
import io
from functools import partial
from contextlib import contextmanager
from Registration.register_login import (
    handle_registration,
    handle_login,
    handle_view_profile,
    handle_update_profile,
    handle_delete_profile
)
from PortfolioManagement.port_mgmt import (
    create_portfolio,
    edit_portfolio,
    delete_portfolio,
    view_portfolio_with_stocks,
    view_portfolios,
    add_stock,
    delete_stock
)

# Context manager to override input and capture print output
@contextmanager
def capture_io(inputs):
    """
    Overrides the built-in input function to supply predefined inputs
    and captures all print outputs.
    """
    original_input = __builtins__.input
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    def mock_input(prompt=""):
        if inputs:
            return inputs.pop(0)
        else:
            return original_input(prompt)

    __builtins__.input = mock_input
    try:
        yield sys.stdout
    finally:
        __builtins__.input = original_input
        sys.stdout = original_stdout

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portfolio Performance Tracking Tool")
        self.geometry("800x600")
        self.resizable(False, False)

        # Container for all frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # Dictionary to hold different frames
        self.frames = {}
        for F in (StartPage, RegisterPage, LoginPage, UserMenuPage,
                  ProfileManagementPage, PortfolioManagementPage):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.user_id = None
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Welcome to the Portfolio Performance Tracking Tool", font=("Helvetica", 18))
        label.pack(pady=50)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        register_btn = tk.Button(button_frame, text="Register",
                                 command=lambda: controller.show_frame(RegisterPage),
                                 width=20, height=2)
        register_btn.grid(row=0, column=0, padx=10, pady=10)

        login_btn = tk.Button(button_frame, text="Login",
                              command=lambda: controller.show_frame(LoginPage),
                              width=20, height=2)
        login_btn.grid(row=0, column=1, padx=10, pady=10)

        exit_btn = tk.Button(button_frame, text="Exit",
                             command=self.quit,
                             width=20, height=2)
        exit_btn.grid(row=0, column=2, padx=10, pady=10)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Register", font=("Helvetica", 18))
        label.pack(pady=20)

        # Registration form
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.username_entry = tk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Email:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.email_entry = tk.Entry(form_frame, width=30)
        self.email_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Password:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.password_entry = tk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        register_btn = tk.Button(button_frame, text="Register", command=self.register_user, width=15)
        register_btn.grid(row=0, column=0, padx=10)

        back_btn = tk.Button(button_frame, text="Back to Start", command=lambda: controller.show_frame(StartPage), width=15)
        back_btn.grid(row=0, column=1, padx=10)

    def register_user(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not email or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        # Prepare inputs for handle_registration
        inputs = [username, email, password]

        try:
            with capture_io(inputs) as output:
                handle_registration()
            result = output.getvalue()
            if "Registration successful." in result:
                messagebox.showinfo("Success", "Registration successful. You can now log in.")
                self.controller.show_frame(LoginPage)
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Login", font=("Helvetica", 18))
        label.pack(pady=20)

        # Login form
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Username:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.username_entry = tk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Password:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.password_entry = tk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        login_btn = tk.Button(button_frame, text="Login", command=self.login_user, width=15)
        login_btn.grid(row=0, column=0, padx=10)

        back_btn = tk.Button(button_frame, text="Back to Start", command=lambda: controller.show_frame(StartPage), width=15)
        back_btn.grid(row=0, column=1, padx=10)

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        # Prepare inputs for handle_login
        inputs = [username, password]

        try:
            with capture_io(inputs) as output:
                user_id = handle_login()
            result = output.getvalue()
            if "Login successful." in result:
                self.controller.user_id = user_id
                messagebox.showinfo("Success", "Login successful.")
                self.controller.show_frame(UserMenuPage)
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class UserMenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="User Menu", font=("Helvetica", 18))
        label.pack(pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        profile_btn = tk.Button(button_frame, text="Profile Management",
                                command=lambda: controller.show_frame(ProfileManagementPage),
                                width=25, height=2)
        profile_btn.grid(row=0, column=0, padx=10, pady=10)

        portfolio_btn = tk.Button(button_frame, text="Portfolio Management",
                                   command=lambda: controller.show_frame(PortfolioManagementPage),
                                   width=25, height=2)
        portfolio_btn.grid(row=0, column=1, padx=10, pady=10)

        logout_btn = tk.Button(button_frame, text="Logout", command=self.logout, width=25, height=2)
        logout_btn.grid(row=0, column=2, padx=10, pady=10)

    def logout(self):
        self.controller.user_id = None
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")
        self.controller.show_frame(StartPage)

class ProfileManagementPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Profile Management", font=("Helvetica", 18))
        label.pack(pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        view_btn = tk.Button(button_frame, text="View Profile", command=self.view_profile, width=20)
        view_btn.grid(row=0, column=0, padx=10, pady=10)

        update_btn = tk.Button(button_frame, text="Update Profile", command=self.update_profile, width=20)
        update_btn.grid(row=0, column=1, padx=10, pady=10)

        delete_btn = tk.Button(button_frame, text="Delete Profile", command=self.delete_profile, width=20)
        delete_btn.grid(row=0, column=2, padx=10, pady=10)

        back_btn = tk.Button(self, text="Back to User Menu",
                             command=lambda: controller.show_frame(UserMenuPage),
                             width=20)
        back_btn.pack(pady=20)

    def view_profile(self):
        try:
            with capture_io([]) as output:
                handle_view_profile(self.controller.user_id)
            result = output.getvalue()
            profile_info = result.strip()
            if profile_info:
                # Display profile info in a scrolled text window
                ProfileInfoWindow(self.controller, profile_info)
            else:
                messagebox.showerror("Error", "Unable to retrieve profile.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_profile(self):
        UpdateProfileWindow(self.controller)

    def delete_profile(self):
        # Prepare input for confirmation
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete your profile?")
        if confirm:
            inputs = ['y']
            try:
                with capture_io(inputs) as output:
                    success = handle_delete_profile(self.controller.user_id)
                result = output.getvalue()
                if "Profile deleted successfully." in result:
                    messagebox.showinfo("Deleted", "Profile deleted successfully.")
                    self.controller.user_id = None
                    self.controller.show_frame(StartPage)
                else:
                    messagebox.showerror("Error", result.strip())
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

class ProfileInfoWindow(tk.Toplevel):
    def __init__(self, controller, profile_info):
        super().__init__(controller)
        self.title("Profile Information")
        self.geometry("500x300")
        self.resizable(False, False)

        label = tk.Label(self, text="Profile Information", font=("Helvetica", 14))
        label.pack(pady=10)

        text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=60, height=10)
        text_area.pack(pady=10)
        text_area.insert(tk.END, profile_info)
        text_area.config(state='disabled')

        close_btn = tk.Button(self, text="Close", command=self.destroy, width=10)
        close_btn.pack(pady=10)

class UpdateProfileWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Update Profile")
        self.geometry("500x400")
        self.resizable(False, False)

        label = tk.Label(self, text="Update Profile", font=("Helvetica", 14))
        label.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="New Username:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.new_username_entry = tk.Entry(form_frame, width=30)
        self.new_username_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="New Email:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.new_email_entry = tk.Entry(form_frame, width=30)
        self.new_email_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="New Password:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.new_password_entry = tk.Entry(form_frame, show="*", width=30)
        self.new_password_entry.grid(row=2, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        update_btn = tk.Button(button_frame, text="Update", command=self.update_profile, width=15)
        update_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=15)
        cancel_btn.grid(row=0, column=1, padx=10)

    def update_profile(self):
        new_username = self.new_username_entry.get().strip()
        new_email = self.new_email_entry.get().strip()
        new_password = self.new_password_entry.get().strip()

        # Prepare inputs
        inputs = [new_username if new_username else '', new_email if new_email else '', new_password if new_password else '']

        try:
            with capture_io(inputs) as output:
                handle_update_profile(self.controller.user_id)
            result = output.getvalue()
            messagebox.showinfo("Update Profile", result.strip())
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class PortfolioManagementPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Portfolio Management", font=("Helvetica", 18))
        label.pack(pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        create_btn = tk.Button(button_frame, text="Create Portfolio", command=self.create_portfolio, width=25)
        create_btn.grid(row=0, column=0, padx=10, pady=10)

        edit_btn = tk.Button(button_frame, text="Edit Portfolio", command=self.edit_portfolio, width=25)
        edit_btn.grid(row=0, column=1, padx=10, pady=10)

        delete_btn = tk.Button(button_frame, text="Delete Portfolio", command=self.delete_portfolio, width=25)
        delete_btn.grid(row=0, column=2, padx=10, pady=10)

        view_btn = tk.Button(button_frame, text="View Portfolio", command=self.view_portfolio, width=25)
        view_btn.grid(row=1, column=0, padx=10, pady=10)

        add_stock_btn = tk.Button(button_frame, text="Add Stock to Portfolio", command=self.add_stock, width=25)
        add_stock_btn.grid(row=1, column=1, padx=10, pady=10)

        delete_stock_btn = tk.Button(button_frame, text="Delete Stock from Portfolio", command=self.delete_stock, width=25)
        delete_stock_btn.grid(row=1, column=2, padx=10, pady=10)

        back_btn = tk.Button(self, text="Back to User Menu",
                             command=lambda: controller.show_frame(UserMenuPage),
                             width=25)
        back_btn.pack(pady=20)

    def create_portfolio(self):
        CreatePortfolioWindow(self.controller)

    def edit_portfolio(self):
        EditPortfolioWindow(self.controller)

    def delete_portfolio(self):
        DeletePortfolioWindow(self.controller)

    def view_portfolio(self):
        try:
            # Fetch portfolio names directly from the database
            portfolio_names = list_user_portfolios_gui(self.controller.user_id)
            if not portfolio_names:
                messagebox.showinfo("Info", "You have no portfolios to view.")
                return

            # Prompt user to select a portfolio
            selected_portfolio = SelectPortfolioDialog(self.controller, portfolio_names, "Select Portfolio to View")
            self.wait_window(selected_portfolio)

            if selected_portfolio.selected_portfolio:
                portfolio_name = selected_portfolio.selected_portfolio
                # Prepare input for handle_view_portfolio_with_stocks
                inputs = [portfolio_name]
                with capture_io(inputs) as output:
                    view_portfolio_with_stocks(self.controller.user_id)
                result = output.getvalue()
                if "Portfolio Details:" in result:
                    # Display portfolio details and stocks
                    PortfolioInfoWindow(self.controller, result.strip())
                else:
                    messagebox.showinfo("Info", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def add_stock(self):
        AddStockWindow(self.controller)

    def delete_stock(self):
        DeleteStockWindow(self.controller)

class SelectPortfolioDialog(tk.Toplevel):
    def __init__(self, controller, portfolio_names, title="Select Portfolio"):
        super().__init__(controller)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.controller = controller
        self.selected_portfolio = None

        label = tk.Label(self, text=title, font=("Helvetica", 14))
        label.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Portfolio:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.portfolio_combo = ttk.Combobox(form_frame, values=portfolio_names, state="readonly", width=25)
        self.portfolio_combo.grid(row=0, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        select_btn = tk.Button(button_frame, text="Select", command=self.select_portfolio, width=10)
        select_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=10)
        cancel_btn.grid(row=0, column=1, padx=10)

    def select_portfolio(self):
        selected = self.portfolio_combo.get()
        if not selected:
            messagebox.showerror("Error", "Please select a portfolio.")
            return
        self.selected_portfolio = selected
        self.destroy()

class PortfolioInfoWindow(tk.Toplevel):
    def __init__(self, controller, portfolio_info):
        super().__init__(controller)
        self.title("Portfolio Information")
        self.geometry("700x500")
        self.resizable(False, False)

        label = tk.Label(self, text="Portfolio Information", font=("Helvetica", 14))
        label.pack(pady=10)

        text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=25)
        text_area.pack(pady=10)
        text_area.insert(tk.END, portfolio_info)
        text_area.config(state='disabled')

        close_btn = tk.Button(self, text="Close", command=self.destroy, width=10)
        close_btn.pack(pady=10)

class CreatePortfolioWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Create Portfolio")
        self.geometry("500x300")
        self.resizable(False, False)

        label = tk.Label(self, text="Create Portfolio", font=("Helvetica", 14))
        label.pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Portfolio Name:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.portfolio_name_entry = tk.Entry(form_frame, width=30)
        self.portfolio_name_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Description:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.description_entry = tk.Entry(form_frame, width=30)
        self.description_entry.grid(row=1, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        create_btn = tk.Button(button_frame, text="Create", command=self.create_portfolio, width=15)
        create_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=15)
        cancel_btn.grid(row=0, column=1, padx=10)

    def create_portfolio(self):
        name = self.portfolio_name_entry.get().strip()
        description = self.description_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Portfolio name is required.")
            return

        inputs = [name, description]

        try:
            with capture_io(inputs) as output:
                create_portfolio(self.controller.user_id)
            result = output.getvalue()
            if "Portfolio created successfully." in result:
                messagebox.showinfo("Success", "Portfolio created successfully.")
                self.destroy()
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class EditPortfolioWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Edit Portfolio")
        self.geometry("500x350")
        self.resizable(False, False)

        label = tk.Label(self, text="Edit Portfolio", font=("Helvetica", 14))
        label.pack(pady=10)

        # Fetch portfolio names directly from the database
        try:
            portfolio_names = list_user_portfolios_gui(self.controller.user_id)
            if not portfolio_names:
                messagebox.showinfo("Info", "You have no portfolios to edit.")
                self.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.destroy()
            return

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Portfolio:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.portfolio_combo = ttk.Combobox(form_frame, values=portfolio_names, state="readonly", width=25)
        self.portfolio_combo.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="New Name:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.new_name_entry = tk.Entry(form_frame, width=30)
        self.new_name_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="New Description:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.new_description_entry = tk.Entry(form_frame, width=30)
        self.new_description_entry.grid(row=2, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        edit_btn = tk.Button(button_frame, text="Edit", command=self.edit_portfolio, width=15)
        edit_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=15)
        cancel_btn.grid(row=0, column=1, padx=10)

    def edit_portfolio(self):
        selected = self.portfolio_combo.get()
        new_name = self.new_name_entry.get().strip()
        new_description = self.new_description_entry.get().strip()

        if not selected:
            messagebox.showerror("Error", "Please select a portfolio to edit.")
            return

        inputs = [selected, new_name, new_description]

        try:
            with capture_io(inputs) as output:
                edit_portfolio(self.controller.user_id)
            result = output.getvalue()
            if "Portfolio updated successfully." in result:
                messagebox.showinfo("Success", "Portfolio updated successfully.")
                self.destroy()
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class DeletePortfolioWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Delete Portfolio")
        self.geometry("500x250")
        self.resizable(False, False)

        label = tk.Label(self, text="Delete Portfolio", font=("Helvetica", 14))
        label.pack(pady=10)

        # Fetch portfolio names directly from the database
        try:
            portfolio_names = list_user_portfolios_gui(self.controller.user_id)
            if not portfolio_names:
                messagebox.showinfo("Info", "You have no portfolios to delete.")
                self.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.destroy()
            return

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Portfolio:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.portfolio_combo = ttk.Combobox(form_frame, values=portfolio_names, state="readonly", width=25)
        self.portfolio_combo.grid(row=0, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        delete_btn = tk.Button(button_frame, text="Delete", command=self.delete_portfolio, width=15)
        delete_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=15)
        cancel_btn.grid(row=0, column=1, padx=10)

    def delete_portfolio(self):
        selected = self.portfolio_combo.get()

        if not selected:
            messagebox.showerror("Error", "Please select a portfolio to delete.")
            return

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the portfolio '{selected}'?")
        if not confirm:
            return

        inputs = [selected]

        try:
            with capture_io(inputs) as output:
                delete_portfolio(self.controller.user_id)
            result = output.getvalue()
            if "Portfolio deleted successfully." in result:
                messagebox.showinfo("Deleted", "Portfolio deleted successfully.")
                self.destroy()
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class AddStockWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Add Stock")
        self.geometry("500x300")
        self.resizable(False, False)

        label = tk.Label(self, text="Add Stock to Portfolio", font=("Helvetica", 14))
        label.pack(pady=10)

        # Fetch portfolio names directly from the database
        try:
            portfolio_names = list_user_portfolios_gui(self.controller.user_id)
            if not portfolio_names:
                messagebox.showinfo("Info", "You have no portfolios to add stocks to.")
                self.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.destroy()
            return

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Portfolio:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.portfolio_combo = ttk.Combobox(form_frame, values=portfolio_names, state="readonly", width=25)
        self.portfolio_combo.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Stock Symbol:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.symbol_entry = tk.Entry(form_frame, width=30)
        self.symbol_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Number of Shares:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.shares_entry = tk.Entry(form_frame, width=30)
        self.shares_entry.grid(row=2, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        add_btn = tk.Button(button_frame, text="Add Stock", command=self.add_stock, width=15)
        add_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=15)
        cancel_btn.grid(row=0, column=1, padx=10)

    def add_stock(self):
        portfolio_name = self.portfolio_combo.get()
        symbol = self.symbol_entry.get().strip().upper()
        shares = self.shares_entry.get().strip()

        if not portfolio_name or not symbol or not shares:
            messagebox.showerror("Error", "All fields are required.")
            return

        if not shares.isdigit() or int(shares) <= 0:
            messagebox.showerror("Error", "Number of shares must be a positive integer.")
            return

        inputs = [portfolio_name, symbol, shares]

        try:
            with capture_io(inputs) as output:
                add_stock(self.controller.user_id)
            result = output.getvalue()
            if "Stock added successfully." in result or "Stock updated successfully." in result:
                messagebox.showinfo("Success", "Stock added successfully.")
                self.destroy()
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class DeleteStockWindow(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.title("Delete Stock")
        self.geometry("500x350")
        self.resizable(False, False)

        label = tk.Label(self, text="Delete Stock from Portfolio", font=("Helvetica", 14))
        label.pack(pady=10)

        # Fetch portfolio names directly from the database
        try:
            portfolio_names = list_user_portfolios_gui(self.controller.user_id)
            if not portfolio_names:
                messagebox.showinfo("Info", "You have no portfolios to delete stocks from.")
                self.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.destroy()
            return

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Portfolio:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.portfolio_combo = ttk.Combobox(form_frame, values=portfolio_names, state="readonly", width=25)
        self.portfolio_combo.grid(row=0, column=1, pady=5, padx=5)
        self.portfolio_combo.bind("<<ComboboxSelected>>", self.load_stocks)

        tk.Label(form_frame, text="Select Stock:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.stock_combo = ttk.Combobox(form_frame, values=[], state="readonly", width=25)
        self.stock_combo.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Number of Shares to Delete:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.delete_shares_entry = tk.Entry(form_frame, width=30)
        self.delete_shares_entry.grid(row=2, column=1, pady=5, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        delete_btn = tk.Button(button_frame, text="Delete Stock", command=self.delete_stock, width=15)
        delete_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy, width=15)
        cancel_btn.grid(row=0, column=1, padx=10)

    def load_stocks(self, event):
        portfolio_name = self.portfolio_combo.get()
        if not portfolio_name:
            return

        try:
            stocks = list_portfolio_stocks_gui(self.controller.user_id, portfolio_name)
            stock_symbols = [stock[0] for stock in stocks]
            self.stock_combo['values'] = stock_symbols
            if not stock_symbols:
                messagebox.showinfo("Info", "No stocks in this portfolio.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_stock(self):
        portfolio_name = self.portfolio_combo.get()
        stock_symbol = self.stock_combo.get()
        delete_shares = self.delete_shares_entry.get().strip()

        if not portfolio_name or not stock_symbol or not delete_shares:
            messagebox.showerror("Error", "All fields are required.")
            return

        if not delete_shares.isdigit() or int(delete_shares) <= 0:
            messagebox.showerror("Error", "Number of shares to delete must be a positive integer.")
            return

        inputs = [portfolio_name, stock_symbol, delete_shares]

        try:
            with capture_io(inputs) as output:
                delete_stock(self.controller.user_id)
            result = output.getvalue()
            if "Stock deleted successfully." in result or "shares deleted successfully." in result:
                messagebox.showinfo("Success", "Stock deleted successfully.")
                self.destroy()
            else:
                messagebox.showerror("Error", result.strip())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Utility functions to interact with backend using GUI
def list_user_portfolios_gui(user_id):
    """
    Fetches the list of portfolio names for the given user_id.
    Returns a list of portfolio names.
    """
    connection = None
    try:
        # Use the same create_connection and close_connection functions as in port_mgmt.py
        from database import create_connection, close_connection
        connection = create_connection()
        portfolios = []
        if connection:
            cursor = connection.cursor()
            cursor.execute('SELECT "name" FROM "Portfolios" WHERE "user_id" = %s', (user_id,))
            portfolios = cursor.fetchall()
            cursor.close()
            close_connection(connection)
        portfolio_names = [portfolio[0] for portfolio in portfolios]
        return portfolio_names
    except Exception as e:
        raise e

def list_portfolio_stocks_gui(user_id, portfolio_name):
    """
    Fetches the list of stocks for the given user_id and portfolio_name.
    Returns a list of tuples containing stock symbols and other details.
    """
    connection = None
    try:
        from database import create_connection, close_connection
        connection = create_connection()
        stocks = []
        if connection:
            cursor = connection.cursor()
            cursor.execute('SELECT "portfolio_id" FROM "Portfolios" WHERE "user_id" = %s AND "name" = %s', (user_id, portfolio_name))
            portfolio = cursor.fetchone()
            if not portfolio:
                cursor.close()
                close_connection(connection)
                return []
            portfolio_id = portfolio[0]
            cursor.execute('SELECT "symbol", "shares", "purchase_price", "avg_purchase_price" FROM "Stocks" WHERE "portfolio_id" = %s', (portfolio_id,))
            stocks = cursor.fetchall()
            cursor.close()
            close_connection(connection)
        return stocks
    except Exception as e:
        raise e

# Initialize and run the application
def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()