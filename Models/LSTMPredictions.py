import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import yfinance as yf

import torch
import torch.nn as nn
import torch.optim as optim

# Constants
TICKER_SYMBOLS = ['AMGN']  # Replace with any stock symbols
START_DATE = '2020-01-01'
END_DATE = '2024-01-01'
TIME_STEP = 100
TRAIN_RATIO = 0.8
EPOCHS = 100
BATCH_SIZE = 64
LEARNING_RATE = 0.01
WEIGHT_DECAY = 0.001
HIDDEN_DIM = 32
NUM_LAYERS = 2
N_SPLITS = 5 
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Function to download and preprocess data
def download_and_preprocess(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)['Adj Close']
    data = data.resample('D').mean().ffill()
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    return pd.DataFrame(scaled_data, index=data.index, columns=data.columns)

# Helper functions for creating datasets and evaluation metrics
def create_xy(data, time_step=1):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:i + time_step])
        y.append(data[i + time_step])
    return np.array(X), np.array(y)

def calculate_metrics(y_true, y_pred):
    mae = np.mean(np.abs(y_true - y_pred))
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    mpe = np.mean((y_true - y_pred) / y_true) * 100
    return mae, mse, rmse, mape, mpe

# Function to evaluate the model
def evaluate_model(model, X, y):
    model.eval()
    with torch.no_grad():
        outputs = model(X).squeeze()
    y_pred = outputs.cpu().numpy()
    y_true = y.cpu().numpy()
    return calculate_metrics(y_true, y_pred)

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim, dropout_prob=0.2):
        super(LSTMModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=dropout_prob)
        self.dropout = nn.Dropout(dropout_prob)  # Dropout layer after LSTM
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        # Initialize hidden state and cell state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(DEVICE)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(DEVICE)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Apply dropout to the output of the last LSTM layer
        out = self.dropout(out[:, -1, :])
        
        # Pass through the fully connected layer
        out = self.fc(out)
        return out

# Main Execution
def main():
    # Download and preprocess data
    historical_data = download_and_preprocess(TICKER_SYMBOLS, START_DATE, END_DATE)
    
    # Initialize performance DataFrame
    model_perf_df = pd.DataFrame(columns=['MAE', 'MSE', 'RMSE', 'MAPE', 'MPE'])
    all_predictions = {}
    
    # Iterate over each ticker
    for ticker in TICKER_SYMBOLS:
        # Create datasets
        X, y = create_xy(historical_data[ticker].values, TIME_STEP)
        
        # Initialize TimeSeriesSplit for cross-validation
        tscv = TimeSeriesSplit(n_splits=N_SPLITS)
        
        # Store fold metrics for averaging
        fold_metrics = []
        
        for fold, (train_index, val_index) in enumerate(tscv.split(X)):
            print(f"Training fold {fold + 1}/{N_SPLITS} for ticker {ticker}...")
            
            # Split data into training and validation sets
            X_train, X_val = X[train_index], X[val_index]
            y_train, y_val = y[train_index], y[val_index]
            
            # Convert to tensors
            X_train = torch.tensor(X_train, dtype=torch.float32).unsqueeze(-1).to(DEVICE)
            y_train = torch.tensor(y_train, dtype=torch.float32).to(DEVICE)
            X_val = torch.tensor(X_val, dtype=torch.float32).unsqueeze(-1).to(DEVICE)
            y_val = torch.tensor(y_val, dtype=torch.float32).to(DEVICE)
            
            # Initialize model, loss, and optimizer
            model = LSTMModel(input_dim=1, hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS, output_dim=1).to(DEVICE)
            criterion = nn.MSELoss()
            optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
            
            # Training loop
            model.train()
            for epoch in range(1, EPOCHS + 1):
                optimizer.zero_grad()
                outputs = model(X_train).squeeze()
                loss = criterion(outputs, y_train)
                loss.backward()
                optimizer.step()
                
                if epoch % 10 == 0 or epoch == 1:
                    print(f'{ticker} - Fold {fold + 1} - Epoch [{epoch}/{EPOCHS}], Loss: {loss.item():.4f}')
            
            # Evaluate the model on the validation set
            mae, mse, rmse, mape, mpe = evaluate_model(model, X_val, y_val)
            print(f'{ticker} - Fold {fold + 1} - Validation MAE: {mae:.4f}, MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%, MPE: {mpe:.2f}%')
            
            # Store metrics for this fold
            fold_metrics.append([mae, mse, rmse, mape, mpe])
        
        # Calculate average metrics across all folds
        avg_metrics = np.mean(fold_metrics, axis=0)
        model_perf_df.loc[ticker] = avg_metrics
        print(f'\n{ticker} - Average CV MAE: {avg_metrics[0]:.4f}, MSE: {avg_metrics[1]:.4f}, RMSE: {avg_metrics[2]:.4f}, MAPE: {avg_metrics[3]:.2f}%, MPE: {avg_metrics[4]:.2f}%')
        
        # Optional: Store predictions for the last fold for visualization purposes
        model.eval()
        with torch.no_grad():
            predictions = model(X_val).squeeze().cpu().numpy()
        all_predictions[ticker] = predictions

    # Display performance metrics
    print("\nCross-Validation Model Performance Metrics:")
    print(model_perf_df)
    
    # Plotting for the last fold (optional)
    for ticker in TICKER_SYMBOLS:
        y_true = historical_data[ticker].iloc[-len(all_predictions[ticker]):].values
        y_pred = all_predictions[ticker]
        dates = historical_data.index[-len(all_predictions[ticker]):]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, y_true, label='True', marker='o')
        plt.plot(dates, y_pred, label='Predicted', linestyle='--')
        plt.xlabel('Date')
        plt.ylabel('Standardized Value')
        plt.title(f'True vs. Predicted Values for {ticker} - Last Fold')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    main()