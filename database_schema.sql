CREATE DATABASE IF NOT EXISTS PortfolioOptimization;
USE PortfolioOptimization;

-- Portfolios table
CREATE TABLE Portfolios (
    PortfolioID INT AUTO_INCREMENT PRIMARY KEY,
    OptimizationMethod VARCHAR(50) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PortfolioStocks table
CREATE TABLE PortfolioStocks (
    PortfolioID INT NOT NULL,
    StockTicker VARCHAR(10) NOT NULL,
    StockWeight DECIMAL(5,2) NOT NULL,
    PRIMARY KEY (PortfolioID, StockTicker),
    FOREIGN KEY (PortfolioID) REFERENCES Portfolios(PortfolioID)
);

-- Stocks table
CREATE TABLE Stocks (
    StockID INT AUTO_INCREMENT PRIMARY KEY,
    StockTicker VARCHAR(10) NOT NULL UNIQUE
);

-- HistoricalData table
CREATE TABLE HistoricalData (
    StockID INT NOT NULL,
    Date DATE NOT NULL,
    MarketPrice DECIMAL(10,2),
    Open DECIMAL(10,2),
    Close DECIMAL(10,2),
    High DECIMAL(10,2),
    Low DECIMAL(10,2),
    Volume BIGINT,
    PRIMARY KEY (StockID, Date),
    FOREIGN KEY (StockID) REFERENCES Stocks(StockID)
);
