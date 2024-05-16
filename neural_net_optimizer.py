import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import tensorflow as tf
import tkinter as tk

class NeuralNetOptimizer:
    """
    A class for portfolio optimization using neural network predictions.

    Attributes:
        historical_data_list (list): A list to store historical stock data.
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

    def neuralnetwork_prediction(self, returns_list_cleaned_aligned):
        """
        Uses a neural network to predict future stock returns based on historical returns.

        Args:
            returns_list_cleaned_aligned (list): List of cleaned and aligned stock returns.

        Returns:
            numpy.ndarray: Predicted future stock returns.
        """
        returns_array = np.vstack(returns_list_cleaned_aligned)
        x = returns_array[:-1, :]
        y = returns_array[1:, :]

        model = tf.keras.Sequential([
            tf.keras.layers.Dense(500, activation="relu"),
            tf.keras.layers.Dropout(0.5),
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
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss="mse")
        model.fit(x, y, epochs=250, verbose=0)

        predicted_returns = model.predict(x[-1:, :])
        return predicted_returns.flatten()

    def optimal_weights(self, returns_list_cleaned_aligned):
        """
        Calculates optimal portfolio weights using a neural network for return predictions.

        Args:
            returns_list_cleaned_aligned (list): List of cleaned and aligned stock returns.

        Returns:
            tuple: Tuple containing optimal weights for equal allocation and optimal allocation.
        """
        cov_matrix = np.cov(np.vstack(returns_list_cleaned_aligned))
        num_assets = len(returns_list_cleaned_aligned)
        equal_weights = np.ones(num_assets) / num_assets

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

    def ML_predictions(self, weights, predicted_returns, cov_matrix):
        """
        Objective function for portfolio optimization using neural network predictions.

        Args:
            weights (numpy.ndarray): Portfolio weights.
            predicted_returns (numpy.ndarray): Predicted future stock returns.
            cov_matrix (numpy.ndarray): Covariance matrix of asset returns.

        Returns:
            float: Objective function value.
        """
        portfolio_return = np.sum(predicted_returns * weights)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -portfolio_return + 0.5 * portfolio_risk

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
                stock = input("Enter Stock Symbol: ")  # Modify as needed for user input
                if not stock:
                    break

                stock = stock.upper()
                historical_data = self.historical_stock_data(stock)
                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    break
                else:
                    print(f"Invalid stock ticker or no data available for {stock}. Please choose again.")

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
        Performs portfolio optimization using neural network predictions.

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

        optimal_weights_equal, optimal_weights_optimal = self.optimal_weights(returns_list_cleaned_aligned)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🚀 Portfolio Optimization Results 🚀:\n")
        self.display_results(optimal_weights_optimal, "Optimal", result_text)

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
    optimizer = NeuralNetOptimizer()
