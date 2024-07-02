import numpy as np
import yfinance as yf
import tensorflow as tf
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error

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

    def monte_carlo(self, returns_list_cleaned_aligned, num_simulations=10000, risk_free_rate=0.0):
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
                bounds=[(0.01, 0.5) for _ in range(num_assets)]
            )

            if result.success:
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
            float: Custom loss function value.
        """
        portfolio_return = np.sum(simulated_returns * weights)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk

        # Custom loss function
        loss = -sharpe_ratio + 0.1 * np.sum(weights**2)  # Regularization term to prevent overfitting
        return loss

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

        if not historical_data_list:
            raise ValueError("No valid stocks found. Please try again.")

        return historical_data_list

    def perform_optimization(self):
        """
        Performs portfolio optimization using Monte Carlo simulation.
        """
        stock_list = input("Enter stock symbols separated by commas: ").split(',')
        stock_list = [stock.strip().upper() for stock in stock_list]

        self.historical_data_list = self.stock_data(stock_list)

        if not self.historical_data_list:
            print("No valid stocks entered. Please try again.")
            return

        returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
        min_length = min(len(arr) for arr in returns_list_cleaned)
        returns_list_cleaned_aligned = [arr[:min_length] for arr in returns_list_cleaned]

        optimal_weights_mc = self.monte_carlo(returns_list_cleaned_aligned)

        # Calculate performance metrics
        portfolio_returns = np.dot(np.vstack(returns_list_cleaned_aligned).T, optimal_weights_mc)
        actual_returns = np.mean(np.vstack(returns_list_cleaned_aligned).T, axis=1)
        mse = mean_squared_error(actual_returns, portfolio_returns)
        cumulative_return = np.sum(portfolio_returns)
        sharpe_ratio = (np.mean(portfolio_returns) - 0.0) / np.std(portfolio_returns)

        # Display results
        print("🚀 Portfolio Optimization Results 🚀:")
        self.display_results(optimal_weights_mc, "Monte Carlo Optimized")
        print(f"Mean Squared Error: {mse:.6f}")
        print(f"Cumulative Return: {cumulative_return:.6f}")
        print(f"Sharpe Ratio: {sharpe_ratio:.4f}")

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
    mc_optimizer = MonteCarloOptimizer()
    mc_optimizer.perform_optimization()