from flask import Flask, render_template, request, jsonify
from neural_net_optimizer import NeuralNetOptimizer
from monte_carlo_optimizer import MonteCarloOptimizer
from quantum_comp_optimizer import QuantumAnnealingOptimizer
import numpy as np

app = Flask(__name__)

# Initialize optimizers
nn_optimizer = NeuralNetOptimizer()
mc_optimizer = MonteCarloOptimizer()
qa_optimizer = QuantumAnnealingOptimizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    num_stocks = int(request.form['num_stocks'])
    optimization_method = request.form['optimization_method']
    stock_data = request.form.getlist('stock_data[]')
    
    # Simulate fetching historical stock data
    historical_data_list = [nn_optimizer.historical_stock_data(stock) for stock in stock_data]
    returns_list_cleaned = [data["Close"].pct_change().dropna().values for data in historical_data_list]
    min_length = min(len(arr) for arr in returns_list_cleaned)
    returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

    if optimization_method == "Neural Network":
        optimal_weights = nn_optimizer.optimal_weights(returns_list_cleaned_aligned)[1]
    elif optimization_method == "Monte Carlo Simulation":
        optimal_weights = mc_optimizer.monte_carlo(returns_list_cleaned_aligned)
    elif optimization_method == "Quantum Annealing":
        cov_matrix = qa_optimizer.covariance_matrix(returns_list_cleaned_aligned)
        optimal_weights = qa_optimizer.quantum_portfolio_optimization(cov_matrix)

    total_weight = np.sum(optimal_weights)
    normalized_weights = (optimal_weights / total_weight) * 100

    results = {stock: float(weight) for stock, weight in zip(stock_data, normalized_weights)}
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
