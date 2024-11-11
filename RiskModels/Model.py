import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def get_stock_data(tickers, start_date='2022-01-01', end_date='2023-01-01'):
    """
    Fetch adjusted closing prices for the given tickers and date range.
    """
    try:
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        return data
    except Exception as e:
        print(f"Error fetching stock data for {tickers}: {e}")
        return pd.DataFrame()

def calculate_features(data):
    """
    Calculate advanced risk features for the portfolio.
    """
    # Calculate daily returns
    returns = data.pct_change().dropna()
    
    # Initialize features dictionary
    features = {}
    
    # Volatility (Standard Deviation of returns)
    features['Volatility'] = returns.std().mean()
    
    # Mean Return
    features['Mean_Return'] = returns.mean().mean()
    
    # Skewness
    features['Skewness'] = returns.skew().mean()
    
    # Kurtosis
    features['Kurtosis'] = returns.kurtosis().mean()
    
    # Maximum Drawdown
    cumulative_returns = (1 + returns).cumprod()
    cumulative_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - cumulative_max) / cumulative_max
    features['Max_Drawdown'] = drawdown.min().mean()
    
    # Sharpe Ratio
    risk_free_rate = 0.01 / 252  # Assuming 1% annual risk-free rate
    features['Sharpe_Ratio'] = (features['Mean_Return'] - risk_free_rate) / features['Volatility']
    
    # Beta (to market index, e.g., S&P 500)
    market_data = get_stock_data(['^GSPC'], start_date=data.index[0], end_date=data.index[-1])
    if market_data.empty:
        print("Error fetching market data for Beta calculation.")
        features['Beta'] = np.nan
    else:
        market_returns = market_data.pct_change().dropna()
        # Align the portfolio returns with market returns
        aligned_returns, aligned_market_returns = returns.align(market_returns, join='inner')
        portfolio_returns = aligned_returns.mean(axis=1)
        if len(portfolio_returns) < 2:
            print("Not enough data to calculate Beta.")
            features['Beta'] = np.nan
        else:
            cov_matrix = np.cov(portfolio_returns, aligned_market_returns)
            features['Beta'] = cov_matrix[0,1] / cov_matrix[1,1]
    
    return pd.DataFrame([features])

def load_pretrained_model():
    """
    Load a pre-trained machine learning model.
    For demonstration, we are simulating model training.
    In practice, train the model on historical data and load it using joblib or pickle.
    """
    from sklearn.datasets import make_classification
    # Simulate a classification problem with 3 classes (Low, Medium, High)
    X_dummy, y_dummy = make_classification(n_samples=1000, n_features=7, 
                                           n_informative=5, n_redundant=0,
                                           n_classes=3, random_state=42)
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_dummy, y_dummy)
    return clf

def predict_risk_level(features, model):
    """
    Predict the risk level using the machine learning model.
    """
    # Handle missing features (e.g., Beta could be NaN)
    if features.isnull().values.any():
        print("Warning: Some features are missing. Risk prediction may be inaccurate.")
    
    # Replace NaN values with the mean of the column
    features_filled = features.fillna(features.mean())
    
    # Scale features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_filled)
    
    # Predict risk level
    risk_level = model.predict(features_scaled)
    risk_dict = {0: 'Low', 1: 'Medium', 2: 'High'}
    return risk_dict.get(risk_level[0], "Unknown")

def robust_portfolio_optimization(returns):
    """
    Optimize portfolio weights to minimize risk using robust optimization.
    """
    from scipy.optimize import minimize

    # Define the objective function: negative Sharpe Ratio
    def objective(weights):
        portfolio_return = np.dot(weights, returns.mean())
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov(), weights)))
        # To maximize Sharpe Ratio, minimize the negative
        return - (portfolio_return / portfolio_volatility)
    
    # Constraints: weights sum to 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Bounds: weights between 0 and 1
    bounds = tuple((0, 1) for _ in range(returns.shape[1]))
    
    # Initial guess: equal distribution
    init_guess = np.array([1 / returns.shape[1]] * returns.shape[1])
    
    # Perform optimization
    result = minimize(objective, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if result.success:
        optimized_weights = result.x
        return optimized_weights
    else:
        print("Optimization failed. Using equal weights.")
        return init_guess

def main():
    # User inputs stock tickers
    tickers_input = input("Enter stock tickers separated by commas: ")
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(',')]
    
    # Fetch stock data
    data = get_stock_data(tickers)
    if data.empty:
        print("No data found for the given tickers. Exiting.")
        return
    
    # Handle cases where some tickers might not have data
    data = data.dropna(axis=1, how='all')
    if data.empty:
        print("All provided tickers have no data. Exiting.")
        return
    elif data.shape[1] != len(tickers):
        print("Some tickers did not return data and will be excluded from the portfolio.")
        tickers = data.columns.tolist()
    
    # Calculate initial features
    features = calculate_features(data)
    
    # Optimize portfolio weights using robust optimization
    returns = data.pct_change().dropna()
    optimized_weights = robust_portfolio_optimization(returns)
    print("\nOptimized Portfolio Weights:")
    for ticker, weight in zip(tickers, optimized_weights):
        print(f"{ticker}: {weight:.2%}")
    
    # Recalculate portfolio returns with optimized weights
    portfolio_returns = returns.dot(optimized_weights)
    
    # Recalculate features with optimized portfolio
    optimized_data = pd.DataFrame(portfolio_returns, columns=['Optimized_Portfolio'])
    optimized_features = calculate_features(optimized_data)
    
    # Combine initial and optimized features
    combined_features = pd.concat([features, optimized_features], axis=1)
    
    # Load the machine learning model
    model = load_pretrained_model()
    
    # Predict risk level
    risk = predict_risk_level(combined_features, model)
    
    # Display the results
    print(f"\nPortfolio Risk Assessment:")
    print(f"Calculated Features (Initial Portfolio):\n{features.to_string(index=False)}")
    print(f"Calculated Features (Optimized Portfolio):\n{optimized_features.to_string(index=False)}")
    print(f"Based on the machine learning model, the risk level is: {risk}")

if __name__ == "__main__":
    main()