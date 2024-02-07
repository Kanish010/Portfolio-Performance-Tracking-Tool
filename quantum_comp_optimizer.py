import numpy as np
import yfinance as yf
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit import Aer, execute
import tkinter as tk
from tkinter import simpledialog, messagebox

class QuantumAnnealingOptimizer:
    """
    A class for portfolio optimization using quantum annealing.
    """

    def __init__(self):
        self.historical_data_list = []

    def historical_stock_data(self, stock):
        """
        Fetches historical stock data using the Yahoo Finance API.

        Args:
            stock (str): The stock symbol.

        Returns:
            pandas.DataFrame: Historical stock data.
        """
        stock = yf.Ticker(stock)
        historical_data = stock.history(period="max")
        return historical_data

    def covariance_matrix(self, returns_list_cleaned_aligned):
        """
        Computes the covariance matrix of stock returns.

        Args:
            returns_list_cleaned_aligned (list): List of cleaned and aligned stock returns.

        Returns:
            numpy.ndarray: Covariance matrix of asset returns.
        """
        returns_array = np.vstack(returns_list_cleaned_aligned)
        return np.cov(returns_array)

    def quantum_annealing_portfolio_optimization(self, cov_matrix):
        """
        Performs portfolio optimization using quantum annealing.

        Args:
            cov_matrix (numpy.ndarray): Covariance matrix of asset returns.

        Returns:
            numpy.ndarray: Optimal weights for the portfolio.
        """
        # Define the objective function (e.g., minimizing portfolio risk)
        # Define the objective function (e.g., minimizing portfolio risk)
        num_assets = len(cov_matrix)
        qubo = np.zeros((num_assets, num_assets))
        for i in range(num_assets):
            for j in range(i, num_assets):
                qubo[i, j] = cov_matrix[i, j]
                qubo[j, i] = cov_matrix[i, j]

        # Set up QAOA
        optimizer = COBYLA()
        qaoa = QAOA(reps=1, optimizer=optimizer)

        # Choose a quantum simulator or real quantum device
        backend = Aer.get_backend('qasm_simulator')

        # Execute the quantum circuit
        result = qaoa.compute_minimum_eigenvalue(qubo)

        # Extract results
        optimal_weights = result.eigenstate

        return optimal_weights

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
                historical_data = self.historical_stock_data(stock)
                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    break
                else:
                    self.show_error_message(f"Invalid stock ticker or no data available for {stock}. Please choose again.")

        return historical_data_list

    def display_results(self, optimal_weights, title, result_text):
        """
        Displays the optimization results in the result text widget.

        Args:
            optimal_weights (numpy.ndarray): Optimal weights for the portfolio.
            title (str): Title for the optimization method.
            result_text (tk.Text): Text widget to display results.
        """
        result_text.insert(tk.END, f"\n{title} Portfolio:\n")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], optimal_weights):
            result_text.insert(tk.END, f"   {stock}: {weight:.2f}%\n")
        result_text.insert(tk.END, "\n")

    def portfolio_optimization(self, num_stock, invalid_label, result_text):
        """
        Performs portfolio optimization using quantum annealing.

        Args:
            num_stock (str): Number of stocks to consider in the portfolio.
            invalid_label (tk.Label): Label to display an error message.
            result_text (tk.Text): Text widget to display results.
        """
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

        cov_matrix = self.covariance_matrix(returns_list_cleaned_aligned)
        optimal_weights = self.quantum_annealing_portfolio_optimization(cov_matrix)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🚀 Portfolio Optimization Results 🚀:\n")
        self.display_results(optimal_weights, "Quantum Annealing Optimized", result_text)

    def show_error_message(self, message):
        """
        Displays an error message dialog.

        Args:
            message (str): The error message to display.
        """
        tk.messagebox.showerror("Error", message)

if __name__ == "__main__":
    optimizer = QuantumAnnealingOptimizer()
    # You can call the methods of the optimizer here as needed