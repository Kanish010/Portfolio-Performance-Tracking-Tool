import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import numpy as np
from neural_net_optimizer import NeuralNetOptimizer
from monte_carlo_optimizer import MonteCarloOptimizer

class PortfolioGUI:
    """
    A graphical user interface (GUI) for portfolio optimization using neural network and Monte Carlo methods.

    Attributes:
        nn_optimizer (NeuralNetOptimizer): Instance of NeuralNetOptimizer for neural network-based optimization.
        mc_optimizer (MonteCarloOptimizer): Instance of MonteCarloOptimizer for Monte Carlo simulation-based optimization.
        historical_data_list (list): A list to store historical stock data.
        root (tk.Tk): The main window of the GUI.
        result_text (scrolledtext.ScrolledText): Text widget to display optimization results.
        feedback_label (ttk.Label): Label to provide feedback during optimization.
        progress_bar (ttk.Progressbar): Progress bar widget for indicating optimization progress.
    """

    def __init__(self, nn_optimizer, mc_optimizer):
        self.nn_optimizer = nn_optimizer
        self.mc_optimizer = mc_optimizer
        self.historical_data_list = []
        self.root = tk.Tk()
        self.root.title("Portfolio Optimization GUI")
        self.gui_style()
        self.input_widgets()
        self.result_text = self.result_widget()
        self.feedback_label = self.feedback_widget()
        self.progress_bar = None
        self.disclaimer_label = self.disclaimer_widget()
        self.root.geometry("500x650")

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

        optimization_methods = ["Choose Optimization Method", "Neural Network", "Monte Carlo Simulation"]
        self.optimization_method_var = tk.StringVar(value=optimization_methods[0])  
        self.optimization_method_menu = ttk.OptionMenu(self.root, self.optimization_method_var, *optimization_methods)
        self.optimization_method_menu.pack(pady=5)

        invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
        invalid_label.pack(pady=10)

        run_button = ttk.Button(self.root, text="Run Portfolio Optimization", command=self.run_optimization)
        run_button.pack(pady=20)

        # Bind a function to the OptionMenu variable to update the menu
        self.optimization_method_var.trace("w", self.update_option_menu)

    def update_option_menu(self, *args):
        """
        Updates the OptionMenu when the optimization method is changed.
        """
        current_method = self.optimization_method_var.get()
        new_options = ["Neural Network", "Monte Carlo"] if current_method == "Neural Network" else ["Monte Carlo", "Neural Network"]
        self.optimization_method_menu['menu'].delete(0, 'end')
        for option in new_options:
            self.optimization_method_menu['menu'].add_command(label=option, command=tk._setit(self.optimization_method_var, option))
            
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
        disclaimer_label.pack(pady=10, side="bottom")  # Use pack with side option
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

        # Disable the button and run the optimization
        self.disable_run_button()
        try:
            invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
            self.historical_data_list = self.stock_data(num_stock, invalid_label)

            if not self.historical_data_list:
                invalid_label.config(text="No valid stocks entered. Please try again.")
                return

            returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
            min_length = min(len(arr) for arr in returns_list_cleaned)
            returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

            if self.optimization_method_var.get() == "Neural Network":
                # Neural Net Optimization
                optimal_weights_nn = self.nn_optimizer.optimal_weights(returns_list_cleaned_aligned)[1]
                self.display_results(optimal_weights_nn, "Neural Net Optimized")
            elif self.optimization_method_var.get() == "Monte Carlo":
                # Monte Carlo Optimization
                optimal_weights_mc = self.mc_optimizer.monte_carlo(returns_list_cleaned_aligned)
                self.display_results(optimal_weights_mc, "Monte Carlo Optimized")

            self.feedback_label.config(text="Optimization completed successfully.")
        except Exception as e:
            self.feedback_label.config(text=f"Error during optimization: {str(e)}")
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
        self.progress_bar.pack(pady=10)
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
        Collects historical data for a specified number of stocks.

        Args:
            num_stock (int): Number of stocks to collect data for.
            invalid_label (ttk.Label): Label to display an error message.

        Returns:
            list: List of tuples containing stock symbols and their historical data.
        """
        historical_data_list = []

        for _ in range(num_stock):
            while True:
                stock = simpledialog.askstring("Enter Stock Symbol", "Enter the stock symbol: ")
                if not stock:
                    break

                stock = stock.upper().replace(" ", "")
                historical_data = self.nn_optimizer.historical_stock_data(stock)
                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    break
                else:
                    self.show_error_message(f"Invalid stock ticker or no data available for {stock}. Please choose again.")

        return historical_data_list

    def display_results(self, optimal_weights, title):
        """
        Displays the optimization results in the result text widget.

        Args:
            optimal_weights (numpy.ndarray): Optimal weights for the portfolio.
            title (str): Title for the optimization method.
        """
        self.result_text.insert(tk.END, f"\n{title} Portfolio:\n")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], optimal_weights):
            self.result_text.insert(tk.END, f"   {stock}: {weight:.2f}%\n")
        self.result_text.insert(tk.END, "\n")

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
    gui = PortfolioGUI(nn_optimizer, mc_optimizer)
    gui.run_gui()