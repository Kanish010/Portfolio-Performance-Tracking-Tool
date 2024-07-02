import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

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

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)
        x_train, x_val, y_train, y_val = train_test_split(x_scaled, y, test_size=0.2, random_state=42)

        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(1, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.01))
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005), loss="mse")
        
        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)

        history = model.fit(x_train, y_train, epochs=200, batch_size=32, validation_data=(x_val, y_val), verbose=0, callbacks=[early_stopping, lr_scheduler])

        self.plot_learning_curve(history)

        predicted_returns = model.predict(scaler.transform(x[-1:, :]))
        return predicted_returns.flatten()

    def plot_learning_curve(self, history):
        """
        Plots the learning curve of the neural network training process.

        Args:
            history (tf.keras.callbacks.History): Training history of the neural network.
        """
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Learning Curve')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()

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

    def stock_data(self, stock_list):
        """
        Collects historical data for a specified list of stocks.

        Args:
            stock_list (list): List of stock symbols.

        Returns:
            list: List of tuples containing stock symbols and their historical data.
        """
        historical_data_list = []

        for stock in stock_list:
            stock = stock.upper()
            historical_data = self.historical_stock_data(stock)
            if not historical_data.empty:
                historical_data_list.append((stock, historical_data))
            else:
                print(f"Invalid stock ticker or no data available for {stock}.")

        return historical_data_list

    def perform_optimization(self):
        """
        Performs portfolio optimization using neural network predictions.
        """
        stock_list = input("Enter stock symbols separated by commas: ").split(',')
        stock_list = [stock.strip() for stock in stock_list]

        self.historical_data_list = self.stock_data(stock_list)

        if not self.historical_data_list:
            print("No valid stocks entered. Please try again.")
            return

        returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
        min_length = min(len(arr) for arr in returns_list_cleaned)
        returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

        optimal_weights_equal, optimal_weights_optimal = self.optimal_weights(returns_list_cleaned_aligned)

        self.display_results(optimal_weights_equal, "Equal Allocation")
        self.display_results(optimal_weights_optimal, "Optimal Allocation")

    def display_results(self, optimal_weights, title):
        """
        Displays the results of portfolio optimization.

        Args:
            optimal_weights (numpy.ndarray): Optimal weights for the portfolio.
            title (str): Title for the optimization method.
        """
        print(f"\n{title} Portfolio:")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], optimal_weights):
            print(f"   {stock}: {weight:.2f}%")
        print("\n")

if __name__ == "__main__":
    optimizer = NeuralNetOptimizer()
    optimizer.perform_optimization()