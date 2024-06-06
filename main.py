from flask import Flask, render_template, request, jsonify
from neural_net_optimizer import NeuralNetOptimizer
from monte_carlo_optimizer import MonteCarloOptimizer
from quantum_comp_optimizer import QuantumAnnealingOptimizer
from SQL_connector import DatabaseManager
import numpy as np
import re

app = Flask(__name__)

# Initialize optimizers
nn_optimizer = NeuralNetOptimizer()
mc_optimizer = MonteCarloOptimizer()
qa_optimizer = QuantumAnnealingOptimizer()

# Initialize database manager
db_manager = DatabaseManager(host='localhost', user='root', password='password', database='PortfolioOptimization')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        optimization_method = request.form['optimization_method']
        stock_data = request.form.getlist('stock_data[]')
        
        # Validate the stock data input
        invalid_stocks = [stock for stock in stock_data if not re.match(r'^[a-zA-Z0-9]+$', stock)]
        if invalid_stocks:
            return jsonify({"error": f"Invalid stock tickers: {', '.join(invalid_stocks)}. Please enter valid stock tickers."}), 400
        
        if not stock_data:
            return jsonify({"error": "No stock data provided."}), 400

        # Simulate fetching historical stock data
        historical_data_list = [nn_optimizer.historical_stock_data(stock) for stock in stock_data]
        valid_historical_data_list = [data for data in historical_data_list if not data.empty]
        invalid_stocks = [stock for stock, data in zip(stock_data, historical_data_list) if data.empty]

        if invalid_stocks:
            return jsonify({"error": f"Invalid stock tickers with no data: {', '.join(invalid_stocks)}. Please enter valid stock tickers."}), 400

        returns_list_cleaned = [data["Close"].pct_change().dropna().values for data in valid_historical_data_list]
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

        # Insert portfolio into database and get portfolio_id
        portfolio_id = db_manager.insert_portfolio(optimization_method)

        results = {}
        for stock, weight in zip(stock_data, normalized_weights):
            stock = stock.upper()
            db_manager.insert_portfolio_stock(portfolio_id, stock, float(weight.item()))
            results[stock] = float(weight.item())
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)