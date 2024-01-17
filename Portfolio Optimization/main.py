from neural_net_optimizer import NeuralNetPortfolioOptimizer
from monte_carlo_optimizer import MonteCarloPortfolioOptimizer
from portfolio_gui import PortfolioGUI

if __name__ == "__main__":
    nn_optimizer = NeuralNetPortfolioOptimizer()
    mc_optimizer = MonteCarloPortfolioOptimizer()
    gui = PortfolioGUI(nn_optimizer, mc_optimizer)
    gui.run_gui()
