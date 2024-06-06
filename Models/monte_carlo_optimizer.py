import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import tkinter as tk
from tkinter import simpledialog

class MonteCarloOptimizer:
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

    def monte_carlo(self, returns_list_cleaned_aligned, num_simulations=2500, risk_free_rate=0.0):
        """
        Performs Monte Carlo simulation for portfolio optimization.

        Args:
            returns_list_cleaned_aligned (list): List of cleaned and aligned stock returns.
            num_simulations (int): Number of Monte Carlo simulations.
            risk_free_rate (float): The risk-free rate for the Sharpe ratio calculation.

        Returns:
            numpy.ndarray: Optimal weights for the portfolio.
        """
        cov_matrix = np.cov(np.vstack(returns_list_cleaned_aligned))
        num_assets = len(returns_list_cleaned_aligned)
        weights_list = []

        for _ in range(num_simulations):
            simulated_mean = np.mean(np.vstack(returns_list_cleaned_aligned).T, axis=0)
            simulated_returns = np.random.multivariate_normal(simulated_mean, cov_matrix, size=1)

            result = minimize(
                self.objective_function, np.random.rand(num_assets),
                args=(simulated_returns, cov_matrix, risk_free_rate),
                method="SLSQP", constraints=({"type": "eq", "fun": lambda w: np.sum(w) - 1},
                                              {"type": "ineq", "fun": lambda w: w}),
                bounds=[(0, 1) for _ in range(num_assets)]
            )

            weights_list.append(result.x)

        optimal_weights = np.mean(weights_list, axis=0)
        return optimal_weights

    def objective_function(self, weights, simulated_returns, cov_matrix, risk_free_rate):
        """
        Objective function for portfolio optimization.

        Args:
            weights (numpy.ndarray): Portfolio weights.
            simulated_returns (numpy.ndarray): Simulated returns for the portfolio.
            cov_matrix (numpy.ndarray): Covariance matrix of asset returns.
            risk_free_rate (float): The risk-free rate for the Sharpe ratio calculation.

        Returns:
            float: Negative of the Sharpe ratio.
        """
        portfolio_return = np.sum(simulated_returns * weights)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
        return -sharpe_ratio

    def stock_data(self, num_stock, invalid_label):
        """
        Collects historical data for a specified number of stocks.

        Args:
            num_stock (int): Number of stocks to collect data for.
            invalid_label (tk.Label): Label to display an error message.

        Returns:
            list: List of tuples containing stock symbols and their historical data.
        """
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

    def display_results(self, optimal_weights, title, result_text):
        """
        Displays the results of portfolio optimization.

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
        Performs portfolio optimization using Monte Carlo simulation.

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

        optimal_weights_mc = self.monte_carlo(returns_list_cleaned_aligned)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🚀 Portfolio Optimization Results 🚀:\n")
        self.display_results(optimal_weights_mc, "Monte Carlo Optimized", result_text)

        for stock, historical_data in self.historical_data_list:
            self.plot_data(historical_data, stock)

    def show_error_message(self, message):
        """
        Displays an error message dialog.

        Args:
            message (str): The error message to display.
        """
        tk.messagebox.showerror("Error", message)

if __name__ == "__main__":
    mc_optimizer = MonteCarloOptimizer()
