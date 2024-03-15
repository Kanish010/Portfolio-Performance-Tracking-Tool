USE Portfolio_Optimization;

CREATE TABLE Portfolio (
    PortfolioID INT PRIMARY KEY AUTO_INCREMENT,
    DateCreated DATE NOT NULL
);

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

CREATE TABLE OptimizationTechnique (
    TechniqueID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE PortfolioComposition (
    CompositionID INT PRIMARY KEY AUTO_INCREMENT,
    PortfolioID INT,
    StockID INT,
    Weight DECIMAL(5, 4),
    FOREIGN KEY (PortfolioID) REFERENCES Portfolio(PortfolioID),
    FOREIGN KEY (StockID) REFERENCES Stock(StockID)
);


