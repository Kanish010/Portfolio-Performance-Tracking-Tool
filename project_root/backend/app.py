from flask import Flask, request, jsonify
from flask_cors import CORS
from Registration.register_login import handle_registration, handle_login, handle_view_profile, handle_update_profile, handle_delete_profile
from PortfolioManagement.port_mgmt import create_portfolio, edit_portfolio, delete_portfolio, view_portfolio_with_stocks, view_portfolios, add_stock, delete_stock

app = Flask(__name__)
CORS(app)

# Authentication Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    response = handle_registration(data['username'], data['email'], data['password'])
    return jsonify(response)

# app.py in /login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = handle_login(data['username'], data['password'])
    if response["success"]:
        return jsonify(response)
    return jsonify(response), 400  # Send a 400 status for errors

# Profile Routes
@app.route('/profile/<int:user_id>', methods=['GET'])
def view_profile(user_id):
    response = handle_view_profile(user_id)
    return jsonify(response)

@app.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    data = request.get_json()
    response = handle_update_profile(
        user_id,
        data.get('username'),
        data.get('email'),
        data.get('password')
    )
    return jsonify(response)

@app.route('/profile/<int:user_id>', methods=['DELETE'])
def delete_profile(user_id):
    response = handle_delete_profile(user_id)
    return jsonify(response)

# Portfolio Routes
@app.route('/portfolio/<int:user_id>', methods=['POST'])
def create_portfolio_route(user_id):
    data = request.get_json()
    response = create_portfolio(user_id, data['name'], data.get('description'))
    return jsonify(response)

@app.route('/portfolio/<int:user_id>', methods=['GET'])
def view_portfolios_route(user_id):
    response = view_portfolios(user_id)
    return jsonify(response)

@app.route('/portfolio/<int:user_id>/<portfolio_name>', methods=['GET'])
def view_portfolio_with_stocks_route(user_id, portfolio_name):
    response = view_portfolio_with_stocks(user_id, portfolio_name)
    return jsonify(response)

@app.route('/portfolio/<int:user_id>/<portfolio_name>', methods=['PUT'])
def edit_portfolio_route(user_id, portfolio_name):
    data = request.get_json()
    response = edit_portfolio(user_id, portfolio_name, data.get('new_name'), data.get('new_description'))
    return jsonify(response)

@app.route('/portfolio/<int:user_id>/<portfolio_name>', methods=['DELETE'])
def delete_portfolio_route(user_id, portfolio_name):
    response = delete_portfolio(user_id, portfolio_name)
    return jsonify(response)

# Stock Routes
@app.route('/portfolio/<int:user_id>/<portfolio_name>/stock', methods=['POST'])
def add_stock_route(user_id, portfolio_name):
    data = request.get_json()
    response = add_stock(user_id, portfolio_name, data['symbol'], data['shares'])
    return jsonify(response)

@app.route('/portfolio/<int:user_id>/<portfolio_name>/stock/<stock_id>', methods=['DELETE'])
def delete_stock_route(user_id, portfolio_name, stock_id):
    response = delete_stock(user_id, portfolio_name, stock_id)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)