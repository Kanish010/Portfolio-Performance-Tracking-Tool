CREATE DATABASE IF NOT EXISTS PortfolioOptimization;
USE PortfolioOptimization;

CREATE TABLE Stock (
    StockID INT PRIMARY KEY AUTO_INCREMENT,
    Symbol VARCHAR(10) NOT NULL,
    MarketPrice DECIMAL(10, 2) NOT NULL
);

CREATE TABLE HistoricalData (
    HistoricalID INT PRIMARY KEY AUTO_INCREMENT,
    StockID INT,
    Date DATE,
    ClosePrice DECIMAL(10, 2),
    FOREIGN KEY (StockID) REFERENCES Stock(StockID)
);

CREATE TABLE Portfolio (
    PortfolioID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PortfolioStocks (
    PortfolioStockID INT PRIMARY KEY AUTO_INCREMENT,
    PortfolioID INT,
    StockID INT,
    FOREIGN KEY (PortfolioID) REFERENCES Portfolio(PortfolioID),
    FOREIGN KEY (StockID) REFERENCES Stock(StockID)
);

CREATE TABLE PortfolioWeights (
    WeightID INT PRIMARY KEY AUTO_INCREMENT,
    PortfolioID INT NOT NULL,
    StockID INT NOT NULL,
    Weight DECIMAL(5, 2) NOT NULL,
    FOREIGN KEY (PortfolioID) REFERENCES Portfolio(PortfolioID),
    FOREIGN KEY (StockID) REFERENCES Stock(StockID)
);