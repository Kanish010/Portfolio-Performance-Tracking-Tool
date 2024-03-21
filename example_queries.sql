USE PortfolioOptimization;
SELECT Stock.StockID, Stock.Symbol, Stock.MarketPrice, Portfolio.PortfolioID, Portfolio.Name
FROM Stock
CROSS JOIN Portfolio;




