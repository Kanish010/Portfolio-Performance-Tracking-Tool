import numpy as np
import cirq
from scipy.optimize import minimize
import tkinter as tk
from tkinter import messagebox

class QuantumAnnealingOptimizer:
    """
    A class for portfolio optimization using quantum annealing.
    """

    def __init__(self):
        self.historical_data_list = []

    def covariance_matrix(self, returns_list_cleaned_aligned):
        """
        Calculates the covariance matrix of asset returns.

        Args:
            returns_list_cleaned_aligned (list): List of cleaned and aligned stock returns.

        Returns:
            numpy.ndarray: Covariance matrix of asset returns.
        """
        return np.cov(np.vstack(returns_list_cleaned_aligned))

    def quantum_portfolio_optimization(self, covariance_matrix):
        """
        Performs portfolio optimization using quantum annealing.

        Args:
            covariance_matrix (numpy.ndarray): Covariance matrix of asset returns.

        Returns:
            numpy.ndarray: Optimal weights for the portfolio.
        """
        num_assets = len(covariance_matrix)
        qubits = [cirq.GridQubit(0, i) for i in range(num_assets)]
        
        # Set up quantum circuit
        circuit = cirq.Circuit()
        for i in range(num_assets):
            circuit.append(cirq.H(qubits[i]))  # Apply Hadamard gate to each qubit
            circuit.append(cirq.measure(qubits[i], key="m"+str(i)))  # Measure each qubit

        # Define the cost function
        def cost_function(weights):
            return np.dot(weights.T, np.dot(covariance_matrix, weights))

        # Define the quantum annealing objective function
        def objective_function(params):
            resolver = cirq.ParamResolver({"theta_" + str(i): params[i] for i in range(num_assets)})
            sim = cirq.Simulator()
            result = sim.run(circuit, resolver, repetitions=1000)  # Run the circuit multiple times to get measurements
            measurements = np.array([result.measurements["m"+str(i)] for i in range(num_assets)])  # Extract measurements
            weights = np.mean(measurements, axis=1)  # Calculate the mean of measurements
            return cost_function(weights)

        # Initial guess for parameters (angles)
        initial_guess = np.random.uniform(0, 2 * np.pi, num_assets)

        # Minimize the objective function to find optimal parameters
        result = minimize(objective_function, initial_guess, method="COBYLA")

        # Use the optimal parameters to calculate the optimal weights
        resolver = cirq.ParamResolver({"theta_" + str(i): result.x[i] for i in range(num_assets)})
        sim = cirq.Simulator()
        result = sim.run(circuit, resolver, repetitions=1000)  # Run the circuit multiple times to get measurements
        measurements = np.array([result.measurements["m"+str(i)] for i in range(num_assets)])  # Extract measurements
        optimal_weights = np.mean(measurements, axis=1)  # Calculate the mean of measurements

        return optimal_weights

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
        optimal_weights = self.quantum_portfolio_optimization(cov_matrix)

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "🚀 Portfolio Optimization Results 🚀:\n")
        self.display_results(optimal_weights, "Quantum Annealing Optimized", result_text)

    def show_error_message(self, message):
        """
        Displays an error message dialog.

        Args:
            message (str): The error message to display.
        """
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    optimizer = QuantumAnnealingOptimizer()
