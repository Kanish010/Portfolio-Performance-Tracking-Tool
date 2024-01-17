import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import tensorflow as tf
import tkinter as tk
import matplotlib.pyplot as plt

class NeuralNetOptimizer:
    def __init__(self):
        self.historical_data_list = []

    def historical_stock_data(self, stock):
        stock = yf.Ticker(stock)  
        historical_data = stock.history(period="max")
        return historical_data

    def neuralnetwork_prediction(self, returns_list_cleaned_aligned):
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
        model.compile(optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001), loss="mse")
        model.fit(x, y, epochs=250, verbose=0)

        predicted_returns = model.predict(x[-1:, :])
        return predicted_returns.flatten()

    def optimal_weights(self, returns_list_cleaned_aligned):
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
        portfolio_return = np.sum(predicted_returns * weights)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -portfolio_return + 0.5 * portfolio_risk

    def stock_data(self, num_stock, invalid_label):
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
        result_text.insert(tk.END, f"\n{title} Portfolio:\n")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], optimal_weights):
            result_text.insert(tk.END, f"   {stock}: {weight:.2f}%\n")
        result_text.insert(tk.END, "\n")

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

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🚀 Portfolio Optimization Results 🚀:\n")
        self.display_results(optimal_weights_optimal, "Optimal", result_text)

        for stock, historical_data in self.historical_data_list:
            self.plot_data(historical_data, stock)
        plt.show()

    def show_error_message(self, message):
        tk.messagebox.showerror("Error", message)

if __name__ == "__main__":
    optimizer = NeuralNetOptimizer()
    # Example: Call methods or perform actions using the optimizer object