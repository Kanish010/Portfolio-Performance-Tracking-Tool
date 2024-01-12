from portfolio_optimizer import PortfolioOptimizer
from portfolio_gui import PortfolioGUI

if __name__ == "__main__":
    optimizer = PortfolioOptimizer()
    gui = PortfolioGUI(optimizer)
    gui.run_gui()