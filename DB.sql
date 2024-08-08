CREATE DATABASE IF NOT EXISTS PortfolioTrackingDB;
USE PortfolioTrackingDB;


CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Recreate the Portfolios table with UUID
CREATE TABLE IF NOT EXISTS Portfolios (
    portfolio_id CHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, name)  -- Ensure unique portfolio names per user
);

-- Recreate the Stocks table with UUID for stock_id
CREATE TABLE IF NOT EXISTS Stocks (
    stock_id CHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    portfolio_id CHAR(36) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    shares INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    total_value DECIMAL(10, 2) GENERATED ALWAYS AS (shares * purchase_price) STORED,  -- Calculated field
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolios(portfolio_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ChatHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36),
    role ENUM('system', 'user', 'assistant'),
    content TEXT,
    response TEXT, 
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP