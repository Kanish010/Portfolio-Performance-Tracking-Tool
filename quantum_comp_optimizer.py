import numpy as np
import yfinance as yf
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit import Aer, execute
import tkinter as tk
from tkinter import messagebox

class QuantumAnnealingOptimizer:
    """
    A class for portfolio optimization using quantum annealing.
    """

    def __init__(self):
        self.historical_data_list = []

    def calculate_energy(self, qubo, solution):
        """
        Calculates the energy of a solution for a given QUBO matrix.

        Args:
            qubo (numpy.ndarray): Quadratic unconstrained binary optimization problem.
            solution (numpy.ndarray): Binary solution vector.

        Returns:
            float: Energy of the solution.
        """
        return np.dot(solution, np.dot(qubo, solution))

    def generate_neighbor(self, solution):
        """
        Generates a neighboring solution by flipping multiple random bits.

        Args:
            solution (numpy.ndarray): Binary solution vector.

        Returns:
            numpy.ndarray: Neighboring solution.
        """
        neighbor_solution = solution.copy()
        flip_indices = np.random.choice(len(solution), size=len(solution) // 2, replace=False)
        neighbor_solution[flip_indices] = 1 - neighbor_solution[flip_indices]
        return neighbor_solution

    def simulated_annealing(self, qubo, num_iterations=5000, initial_temperature=1.0):
        """
        Performs simulated annealing optimization.

        Args:
            qubo (numpy.ndarray): Quadratic unconstrained binary optimization problem.
            num_iterations (int): Number of iterations for simulated annealing.
            initial_temperature (float): Initial temperature for simulated annealing.

        Returns:
            numpy.ndarray: Optimal solution found by simulated annealing.
        """
        num_variables = len(qubo)
        current_solution = np.ones(num_variables) / num_variables  # Initialize with equal weights
        current_energy = self.calculate_energy(qubo, current_solution)
        temperature = initial_temperature

        # Simulated Annealing algorithm
        for _ in range(num_iterations):
            # Generate a random neighboring solution
            neighbor_solution = self.generate_neighbor(current_solution)
            neighbor_energy = self.calculate_energy(qubo, neighbor_solution)

            # If the neighbor solution is better or with probability exp(-delta_E / T),
            # accept the neighbor solution
            if neighbor_energy < current_energy or np.random.rand() < np.exp(-(neighbor_energy - current_energy) / temperature):
                current_solution = neighbor_solution
                current_energy = neighbor_energy
            
            # Update temperature using geometric cooling schedule
            temperature *= 0.95 ** (_ / num_iterations)

        return current_solution

    def generate_neighbor(self, solution):
        """
        Generates a neighboring solution by randomly perturbing the current solution.

        Args:
            solution (numpy.ndarray): Current solution vector.

        Returns:
            numpy.ndarray: Neighboring solution.
        """
        perturbation = np.random.uniform(-0.05, 0.05, size=len(solution))
        neighbor_solution = solution + perturbation
        # Normalize the solution to ensure it sums to 1
        neighbor_solution /= np.sum(neighbor_solution)
        return neighbor_solution

    def covariance_matrix(self, returns_list_cleaned_aligned):
        """
        Calculates the covariance matrix of asset returns.

        Args:
            returns_list_cleaned_aligned (list): List of cleaned and aligned stock returns.

        Returns:
            numpy.ndarray: Covariance matrix of asset returns.
        """
        return np.cov(np.vstack(returns_list_cleaned_aligned))

    def quantum_annealing_portfolio_optimization(self, covariance_matrix, num_iterations=5000):
        """
        Performs portfolio optimization using quantum annealing.

        Args:
            covariance_matrix (numpy.ndarray): Covariance matrix of asset returns.
            num_iterations (int): Number of iterations for simulated annealing.

        Returns:
            numpy.ndarray: Optimal weights for the portfolio.
        """
        # Construct the Ising model Hamiltonian
        num_assets = len(covariance_matrix)
        qubo = np.zeros((num_assets, num_assets))
        for i in range(num_assets):
            for j in range(i, num_assets):
                qubo[i, j] = covariance_matrix[i, j]
                qubo[j, i] = covariance_matrix[i, j]

        # Perform quantum annealing (or simulated annealing) to find the optimal solution
        result = self.simulated_annealing(qubo, num_iterations)

        # Normalize the weights to add up to 100%
        optimal_weights = result / np.sum(result)

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
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    optimizer = QuantumAnnealingOptimizer()
    # You can call the methods of the optimizer here as needed