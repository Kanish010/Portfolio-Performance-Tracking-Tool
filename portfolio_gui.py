import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox, filedialog
import pandas as pd
import numpy as np
from SQL_connector import DatabaseManager
from neural_net_optimizer import NeuralNetOptimizer
from monte_carlo_optimizer import MonteCarloOptimizer
from quantum_comp_optimizer import QuantumAnnealingOptimizer

class PortfolioGUI:
    """
    A graphical user interface (GUI) for portfolio optimization using neural network, Monte Carlo, and quantum annealing methods.

    Attributes:
        nn_optimizer (NeuralNetOptimizer): Instance of NeuralNetOptimizer for neural network-based optimization.
        mc_optimizer (MonteCarloOptimizer): Instance of MonteCarloOptimizer for Monte Carlo simulation-based optimization.
        qa_optimizer (QuantumAnnealingOptimizer): Instance of QuantumAnnealingOptimizer for quantum annealing-based optimization.
        historical_data_list (list): A list to store historical stock data.
        root (tk.Tk): The main window of the GUI.
        result_text (scrolledtext.ScrolledText): Text widget to display optimization results.
        feedback_label (ttk.Label): Label to provide feedback during optimization.
        progress_bar (ttk.Progressbar): Progress bar widget for indicating optimization progress.
    """

    def __init__(self, nn_optimizer, mc_optimizer, qa_optimizer):
        self.nn_optimizer = nn_optimizer
        self.mc_optimizer = mc_optimizer
        self.qa_optimizer = qa_optimizer  
        self.historical_data_list = []
        self.root = tk.Tk()
        self.root.title("Portfolio Optimization GUI")
        self.gui_style()
        self.input_widgets()
        self.result_text = self.result_widget()
        self.feedback_label = self.feedback_widget()
        self.progress_bar = None
        self.disclaimer_label = self.disclaimer_widget()
        self.root.geometry("500x575")

    def gui_style(self):
        """
        Configures the style for the GUI using ttk.Style.
        """
        style = ttk.Style()
        style.configure("TRoundButton", padding=(10, 5), font=("Calibri", 12))

    def input_widgets(self):
        """
        Creates input widgets for the number of stocks, the optimization method selection, and the "Run Portfolio Optimization" button.
        """
        num_stock_label = ttk.Label(self.root, text="Number of stocks:")
        num_stock_label.pack(pady=10)

        self.num_stock_entry = ttk.Entry(self.root, font=("Helvetica", 12))
        self.num_stock_entry.pack(pady=10)

        load_button = ttk.Button(self.root, text="Load Stock Tickers from Excel", command=self.load_tickers_from_excel)
        load_button.pack(pady=5, padx=10)  # Added button to load tickers from Excel

        optimization_methods = ["Choose Optimization Method", "Neural Network", "Monte Carlo Simulation", "Quantum Annealing"]
        self.optimization_method_var = tk.StringVar(value=optimization_methods[0])  
        self.optimization_method_menu = ttk.OptionMenu(self.root, self.optimization_method_var, *optimization_methods)
        self.optimization_method_menu.pack(pady=5)

        invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
        invalid_label.pack(pady=10)

        run_button = ttk.Button(self.root, text="Run Portfolio Optimization", command=self.run_optimization)
        run_button.pack(pady=5, padx=10)

        self.optimization_method_var.trace("w", self.update_option_menu)

    def update_option_menu(self, *args):
        """
        Updates the OptionMenu when the optimization method is changed.
        """
        current_method = self.optimization_method_var.get()
        new_options = []
        if current_method == "Neural Network":
            new_options = ["Monte Carlo Simulation", "Quantum Annealing"]
        elif current_method == "Monte Carlo Simulation":
            new_options = ["Neural Network", "Quantum Annealing"]
        elif current_method == "Quantum Annealing":
            new_options = ["Neural Network", "Monte Carlo Simulation"]
        else:
            raise ValueError("Unexpected optimization method")

        self.optimization_method_menu["menu"].delete(0, "end")
        for option in new_options:
            self.optimization_method_menu["menu"].add_command(label=option, command=tk._setit(self.optimization_method_var, option))

    def result_widget(self):
        """
        Creates a scrolled text widget for displaying optimization results.

        Returns:
            scrolledtext.ScrolledText: The result text widget.
        """
        result_text = scrolledtext.ScrolledText(self.root, width=50, height=15, font=("Calibri", 12))
        result_text.pack(pady=20)
        return result_text

    def feedback_widget(self):
        """
        Creates a label for providing feedback during optimization.

        Returns:
            ttk.Label: The feedback label.
        """
        feedback_label = ttk.Label(self.root, text="", foreground="cyan", font=("Calibri", 12))
        feedback_label.pack(pady=10)
        return feedback_label

    def disclaimer_widget(self):
        """
        Creates a label for displaying a disclaimer.

        Returns:
            ttk.Label: The disclaimer label.
        """
        disclaimer_label = ttk.Label(self.root, text="Disclaimer: This is NOT financial advice.", font=("Calibri", 10), foreground="red")
        disclaimer_label.pack(pady=5, padx=10, side="bottom")
        return disclaimer_label

    def run_optimization(self):
        """
        Initiates portfolio optimization based on user input.
        """
        num_stock_input = self.num_stock_entry.get().replace(" ", "")

        try:
            num_stock = int(num_stock_input)
            if num_stock < 2:
                messagebox.showerror("Error", "Please enter a number greater than 1.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of stocks. Enter a valid positive integer greater than 1.")
            return

        self.feedback_label.config(text="Optimization in progress...")
        self.root.update()

        self.disable_run_button()
        try:
            optimization_method = self.optimization_method_var.get()
            if optimization_method not in ["Neural Network", "Monte Carlo Simulation", "Quantum Annealing"]:
                messagebox.showerror("Error", "Invalid optimization method selected.")
                return

            db_manager = DatabaseManager()
            portfolio_id = db_manager.insert_portfolio(optimization_method)

            invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
            self.historical_data_list = self.stock_data(num_stock, invalid_label)

            if len(self.historical_data_list) < 2:
                invalid_label.config(text="Not enough valid stocks entered. Please try again.")
                return

            returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
            min_length = min(len(arr) for arr in returns_list_cleaned)
            returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

            if optimization_method == "Neural Network":
                optimal_weights = self.nn_optimizer.optimal_weights(returns_list_cleaned_aligned)[1]
            elif optimization_method == "Monte Carlo Simulation":
                optimal_weights = self.mc_optimizer.monte_carlo(returns_list_cleaned_aligned)
            elif optimization_method == "Quantum Annealing":
                cov_matrix = self.qa_optimizer.covariance_matrix(returns_list_cleaned_aligned)
                optimal_weights = self.qa_optimizer.quantum_portfolio_optimization(cov_matrix)

            self.save_portfolio_stocks(portfolio_id, optimal_weights)
            self.display_results(optimal_weights, optimization_method)
            self.feedback_label.config(text="Optimization completed successfully.")
        except Exception as e:
            self.feedback_label.config(text=f"Error during optimization: {str(e)}")
            print(f"Error during optimization: {str(e)}")
        finally:
            self.enable_run_button()

    def disable_run_button(self):
        """
        Disables the "Run Portfolio Optimization" button and displays a progress bar.
        """
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget["state"] = "disabled"
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack(pady=5, padx=10)
        self.progress_bar.start()

    def enable_run_button(self):
        """
        Enables the "Run Portfolio Optimization" button and removes the progress bar.
        """
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget["state"] = "normal"
        self.progress_bar.stop()
        self.progress_bar.destroy()

    def run_gui(self):
        """
        Starts the GUI main loop.
        """
        self.root.mainloop()

    def stock_data(self, num_stock, invalid_label):
        """
        Collects historical data for a specified number of stocks and saves the stock symbols to a MySQL database.

        Args:
            num_stock (int): Number of stocks to collect data for.
            invalid_label (ttk.Label): Label to display an error message.

        Returns:
            list: List of tuples containing stock symbols and their historical data.
        """
        historical_data_list = []
        db_manager = DatabaseManager()

        count = 0
        while count < num_stock:
            stock = simpledialog.askstring("Enter Stock Symbol", f"Enter stock symbol {count + 1}/{num_stock}:")
            if not stock:
                messagebox.showerror("Error", f"Stock symbol {count + 1} cannot be empty. Please enter a valid stock symbol.")
                continue

            stock = stock.upper().replace(" ", "")
            print(f"Fetching data for stock: {stock}")  # Debug print

            try:
                historical_data = self.nn_optimizer.historical_stock_data(stock)
                print(f"Fetched historical data for {stock}")  # Debug print

                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    # Insert stock into Stocks table
                    db_manager.insert_stock(stock)
                    count += 1
                else:
                    self.show_error_message(f"Invalid stock ticker or no data available for {stock}. Please choose again.")
            except Exception as e:
                print(f"Error fetching or inserting data for stock {stock}: {e}")  # Debug print
                self.show_error_message(f"Error fetching or inserting data for stock {stock}: {e}")

        print("Completed fetching and inserting stock data")  # Debug print
        return historical_data_list

    def load_tickers_from_excel(self):
        """
        Prompts the user to select an Excel file and loads stock tickers from it.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            try:
                df = pd.read_excel(file_path)
                if 'Ticker' in df.columns:
                    tickers = df['Ticker'].dropna().astype(str).str.upper().tolist()
                    num_stock = len(tickers)
                    self.num_stock_entry.delete(0, tk.END)
                    self.num_stock_entry.insert(0, str(num_stock))
                    self.historical_data_list = self.get_stock_data_from_list(tickers)
                    self.feedback_label.config(text="Tickers loaded successfully.")
                    self.optimize_portfolio()
                else:
                    self.show_error_message("Excel file must contain a 'Ticker' column.")
            except Exception as e:
                self.show_error_message(f"Failed to load Excel file: {str(e)}")

    def get_stock_data_from_list(self, tickers):
        """
        Retrieves historical data for a list of stock tickers.

        Args:
            tickers (list): List of stock tickers.

        Returns:
            list: List of tuples containing stock symbols and their historical data.
        """
        historical_data_list = []
        db_manager = DatabaseManager()

        for stock in tickers:
            print(f"Fetching data for stock: {stock}")  # Debug print

            try:
                historical_data = self.nn_optimizer.historical_stock_data(stock)
                print(f"Fetched historical data for {stock}")  # Debug print

                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    # Insert stock into Stocks table
                    db_manager.insert_stock(stock)
                else:
                    self.show_error_message(f"Invalid stock ticker or no data available for {stock}. Skipping.")
            except Exception as e:
                print(f"Error fetching or inserting data for stock {stock}: {e}")  # Debug print
                self.show_error_message(f"Error fetching or inserting data for stock {stock}: {e}")

        print("Completed fetching and inserting stock data")  # Debug print
        return historical_data_list

    def save_portfolio_stocks(self, portfolio_id, optimal_weights):
        """
        Saves the optimized portfolio stocks into the database.

        Args:
            portfolio_id (int): ID of the portfolio.
            optimal_weights (numpy.ndarray): Optimal weights for the portfolio.
        """
        db_manager = DatabaseManager()
        total_weight = np.sum(optimal_weights)
        normalized_weights = (optimal_weights / total_weight) * 100

        for (stock, _), weight in zip(self.historical_data_list, normalized_weights):
            db_manager.insert_portfolio_stock(portfolio_id, stock, weight)

    def display_results(self, optimal_weights, title):
        """
        Displays the optimization results in the result text widget.

        Args:
            optimal_weights (numpy.ndarray): Optimal weights for the portfolio.
            title (str): Title for the optimization method.
        """
        if isinstance(optimal_weights, np.ndarray):
            optimal_weights = optimal_weights.flatten()

        total_weight = np.sum(optimal_weights)
        normalized_weights = (optimal_weights / total_weight) * 100

        self.result_text.insert(tk.END, f"\n{title} Portfolio:\n")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], normalized_weights):
            self.result_text.insert(tk.END, f"   {stock}: {weight:.2f}%\n")
        self.result_text.insert(tk.END, "\n")

    def optimize_portfolio(self):
        """
        Optimizes the portfolio based on the selected optimization method.
        """
        optimization_method = self.optimization_method_var.get()
        if optimization_method not in ["Neural Network", "Monte Carlo Simulation", "Quantum Annealing"]:
            self.show_error_message("Invalid optimization method selected.")
            return

        returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
        min_length = min(len(arr) for arr in returns_list_cleaned)
        returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

        if optimization_method == "Neural Network":
            optimal_weights = self.nn_optimizer.optimal_weights(returns_list_cleaned_aligned)[1]
        elif optimization_method == "Monte Carlo Simulation":
            optimal_weights = self.mc_optimizer.monte_carlo(returns_list_cleaned_aligned)
        elif optimization_method == "Quantum Annealing":
            cov_matrix = self.qa_optimizer.covariance_matrix(returns_list_cleaned_aligned)
            optimal_weights = self.qa_optimizer.quantum_portfolio_optimization(cov_matrix)

        self.display_results(optimal_weights, optimization_method)

    def show_error_message(self, message):
        """
        Displays an error message dialog.

        Args:
            message (str): The error message to display.
        """
        tk.messagebox.showerror("Error", message)

if __name__ == "__main__":
    nn_optimizer = NeuralNetOptimizer()
    mc_optimizer = MonteCarloOptimizer()
    qa_optimizer = QuantumAnnealingOptimizer() 
    gui = PortfolioGUI(nn_optimizer, mc_optimizer, qa_optimizer)
    gui.run_gui()