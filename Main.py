import tkinter as tk
from tkinter import ttk, simpledialog, scrolledtext, messagebox
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
import tensorflow as tf 

# PortfolioOptimizer class handles portfolio optimization logic
class PortfolioOptimizer:
    def __init__(self):
        # List to store historical stock data
        self.historical_data_list = []

    # Retrieve historical stock data using yfinance library
    def historical_stock_data(self, stock):
        stock = yf.Ticker(stock)
        historical_data = stock.history(period="max")
        return historical_data

    # Train a neural network and make predictions on future stock returns
    def neuralnetwork_prediction(self, returns_list_cleaned_aligned):
        returns_array = np.vstack(returns_list_cleaned_aligned)
        x = returns_array[:-1, :]
        y = returns_array[1:, :]

        # Define and train a neural network model with dropout
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(500, activation="relu"),
            tf.keras.layers.Dropout(0.5),  # Adjust the dropout rate as needed
            tf.keras.layers.Dense(400, activation="relu"),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.Dense(300, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(200, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(100, activation="relu"),
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer="adam", loss="mse")
        model.fit(x, y, epochs=250, verbose=0)

        # Predict returns using the trained neural network
        predicted_returns = model.predict(x[-1:, :])
        return predicted_returns.flatten()

    # Optimize portfolio weights using predicted returns from neural network
    def optimal_weights(self, returns_list_cleaned_aligned):
        cov_matrix = np.cov(np.vstack(returns_list_cleaned_aligned))
        num_assets = len(returns_list_cleaned_aligned)
        equal_weights = np.ones(num_assets) / num_assets

        # Use neural network predictions in the optimization process
        predicted_returns = self.neuralnetwork_prediction(returns_list_cleaned_aligned)

        result = minimize(
            self.ML_predictions, np.random.rand(num_assets),
            args=(predicted_returns, cov_matrix),
            method="SLSQP", constraints=({"type": "eq", "fun": lambda w: np.sum(w) - 1},
                                          {"type": "ineq", "fun": lambda w: w}),
            bounds=[(0, 1) for _ in range(num_assets)]
        )

        optimal_weights_equal_percent = equal_weights * 100
        optimal_weights_optimal_percent = result.x * 100

        return optimal_weights_equal_percent, optimal_weights_optimal_percent

    # Objective function for portfolio optimization using neural network predictions
    def ML_predictions(self, weights, predicted_returns, cov_matrix):
        # Use neural network predicted returns in the portfolio optimization objective function
        portfolio_return = np.sum(predicted_returns * weights)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -portfolio_return + 0.5 * portfolio_risk

    # Monte Carlo simulation for portfolio optimization
    def monte_carlo(self, returns_list_cleaned_aligned, num_simulations=2500, risk_free_rate=0.0):
        cov_matrix = np.cov(np.vstack(returns_list_cleaned_aligned))
        num_assets = len(returns_list_cleaned_aligned)
        weights_list = []

        for _ in range(num_simulations):
            simulated_mean = np.mean(np.vstack(returns_list_cleaned_aligned).T, axis=0)
            simulated_returns = np.random.multivariate_normal(simulated_mean, cov_matrix, size=1)

            def objective_function(weights, simulated_returns, cov_matrix, risk_free_rate):
                portfolio_return = np.sum(simulated_returns * weights)
                portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
                return -sharpe_ratio

            result = minimize(
                objective_function, np.random.rand(num_assets),
                args=(simulated_returns, cov_matrix, risk_free_rate),
                method="SLSQP", constraints=({"type": "eq", "fun": lambda w: np.sum(w) - 1},
                                              {"type": "ineq", "fun": lambda w: w}),
                bounds=[(0, 1) for _ in range(num_assets)]
            )

            weights_list.append(result.x)

        optimal_weights = np.mean(weights_list, axis=0)
        return optimal_weights

    # Collect user input for stock symbols and retrieve historical data
    def stock_data(self, num_stock, invalid_label):
        historical_data_list = []

        for _ in range(num_stock):
            while True:
                stock = simpledialog.askstring("Enter Stock Symbol", "Enter the stock symbol: ")
                if not stock:
                    break

                stock = stock.upper()
                historical_data = self.historical_stock_data(stock)
                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    break
                else:
                    self.show_error_message(f"Invalid stock ticker or no data available for {stock}. Please choose again.")

        return historical_data_list

    # Display portfolio optimization results in the GUI
    def display_results(self, optimal_weights, title, result_text):
        result_text.insert(tk.END, f"\n{title} Portfolio:\n")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], optimal_weights):
            result_text.insert(tk.END, f"   {stock}: {weight:.2f}%\n")
        result_text.insert(tk.END, "\n")

    # Perform portfolio optimization based on user inputs
    def portfolio_optimization(self, num_stock, invalid_label, result_text):
        num_stock = int(num_stock)
        if num_stock < 2:
            self.show_error_message("Please enter a number greater than 1.")
            return

        invalid_label.config(text="")
        self.historical_data_list = self.stock_data(num_stock, invalid_label)

        if not self.historical_data_list:
            invalid_label.config(text="No valid stocks entered. Please try again.")
            return

        returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
        min_length = min(len(arr) for arr in returns_list_cleaned)
        returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

        optimal_weights_equal, optimal_weights_optimal = self.optimal_weights(returns_list_cleaned_aligned)
        optimal_weights_mc = self.monte_carlo(returns_list_cleaned_aligned)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🚀 Portfolio Optimization Results 🚀:\n")
        self.display_results(optimal_weights_optimal, "Optimal", result_text)
        self.display_results(optimal_weights_mc, "Monte Carlo Optimized", result_text)
        self.display_results(optimal_weights_equal, "Equal-weighted", result_text)

        for stock, historical_data in self.historical_data_list:
            self.plot_data(historical_data, stock)
        plt.show()

    # Plot historical stock data
    def plot_data(self, data, stock):
        plt.figure(figsize=(10, 6))
        plt.plot(data["Close"], label=f"{stock} Closing Price", color="purple")
        plt.title(f"{stock} Stock Prices Over Time")
        plt.xlabel("Date")
        plt.ylabel("Closing Price (USD)")
        plt.legend(), plt.grid()

    # Display error messages using tkinter messagebox
    def show_error_message(self, message):
        tk.messagebox.showerror("Error", message)

# PortfolioGUI class handles the graphical user interface
class PortfolioGUI:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.root = tk.Tk()
        self.root.title("Portfolio Optimization GUI")
        self.gui_style()
        self.input_widgets()
        self.result_text = self.result_widget()
        self.feedback_label = self.feedback_widget()
        self.progress_bar = None
        self.root.geometry("500x550")

    def gui_style(self):
        style = ttk.Style()
        style.configure("TButton", padding=(10, 5), font=("Calibri", 12))

    def input_widgets(self):
        num_stock_label = ttk.Label(self.root, text="Number of stocks:")
        num_stock_label.pack(pady=10)

        self.num_stock_entry = ttk.Entry(self.root, font=("Helvetica", 12))
        self.num_stock_entry.pack(pady=10)

        invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
        invalid_label.pack(pady=10)

        run_button = ttk.Button(self.root, text="Run Portfolio Optimization", command=self.run_optimization)
        run_button.pack(pady=20)

    def result_widget(self):
        result_text = scrolledtext.ScrolledText(self.root, width=50, height=15, font=("Calibri", 12))
        result_text.pack(pady=20)
        return result_text

    def feedback_widget(self):
        feedback_label = ttk.Label(self.root, text="", foreground="cyan", font=("Calibri", 12))
        feedback_label.pack(pady=10)
        return feedback_label

    def run_optimization(self):
        num_stock_input = self.num_stock_entry.get()

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
            self.optimizer.portfolio_optimization(num_stock, invalid_label, self.result_text)
            self.feedback_label.config(text="Optimization completed successfully.")
        except Exception as e:
            self.feedback_label.config(text=f"Error during optimization: {str(e)}")
        finally:
            self.enable_run_button()

    def disable_run_button(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget["state"] = "disabled"
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

    def enable_run_button(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget["state"] = "normal"
        self.progress_bar.stop()
        self.progress_bar.destroy()

    def run_gui(self):
        self.root.mainloop()

if __name__ == "__main__":
    optimizer = PortfolioOptimizer()
    gui = PortfolioGUI(optimizer)
    gui.run_gui()
