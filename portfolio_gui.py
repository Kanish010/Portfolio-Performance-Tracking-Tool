import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import numpy as np
from neural_net_optimizer import NeuralNetOptimizer
from monte_carlo_optimizer import MonteCarloOptimizer

class PortfolioGUI:
    def __init__(self, nn_optimizer, mc_optimizer):
        self.nn_optimizer = nn_optimizer
        self.mc_optimizer = mc_optimizer
        self.historical_data_list = []
        self.root = tk.Tk()
        self.root.title("Portfolio Optimization GUI")
        self.gui_style()
        self.input_widgets()
        self.result_text = self.result_widget()
        self.feedback_label = self.feedback_widget()
        self.progress_bar = None
        self.root.geometry("500x550")

    def gui_style(self):
        style = ttk.Style()
        style.configure("TButton", padding=(10, 5), font=("Calibri", 12))

    def input_widgets(self):
        num_stock_label = ttk.Label(self.root, text="Number of stocks:")
        num_stock_label.pack(pady=10)

        self.num_stock_entry = ttk.Entry(self.root, font=("Helvetica", 12))
        self.num_stock_entry.pack(pady=10)

        invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
        invalid_label.pack(pady=10)

        run_button = ttk.Button(self.root, text="Run Portfolio Optimization", command=self.run_optimization)
        run_button.pack(pady=20)

    def result_widget(self):
        result_text = scrolledtext.ScrolledText(self.root, width=50, height=15, font=("Calibri", 12))
        result_text.pack(pady=20)
        return result_text

    def feedback_widget(self):
        feedback_label = ttk.Label(self.root, text="", foreground="cyan", font=("Calibri", 12))
        feedback_label.pack(pady=10)
        return feedback_label

    def run_optimization(self):
        num_stock_input = self.num_stock_entry.get().replace(" ", "")

        try:
            num_stock = int(num_stock_input)
            if num_stock < 2:
                messagebox.showerror("Error", "Please enter a number greater than 1.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number of stocks. Enter a valid positive integer greater than 1.")
            return

        self.feedback_label.config(text="Optimization in progress...")
        self.root.update()

        # Disable the button and run the optimization
        self.disable_run_button()
        try:
            invalid_label = ttk.Label(self.root, text="", foreground="red", font=("Helvetica", 12))
            self.historical_data_list = self.stock_data(num_stock, invalid_label)
            
            if not self.historical_data_list:
                invalid_label.config(text="No valid stocks entered. Please try again.")
                return

            returns_list_cleaned = [data["Close"].pct_change().dropna().values for _, data in self.historical_data_list]
            min_length = min(len(arr) for arr in returns_list_cleaned)
            returns_list_cleaned_aligned = [np.resize(arr, min_length) for arr in returns_list_cleaned]

            # Neural Net Optimization
            optimal_weights_nn = self.nn_optimizer.optimal_weights(returns_list_cleaned_aligned)[1]
            self.display_results(optimal_weights_nn, "Neural Net Optimized")

            # Monte Carlo Optimization
            optimal_weights_mc = self.mc_optimizer.monte_carlo(returns_list_cleaned_aligned)
            self.display_results(optimal_weights_mc, "Monte Carlo Optimized")

            self.feedback_label.config(text="Optimization completed successfully.")
        except Exception as e:
            self.feedback_label.config(text=f"Error during optimization: {str(e)}")
        finally:
            self.enable_run_button()

    def disable_run_button(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget["state"] = "disabled"
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

    def enable_run_button(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget["state"] = "normal"
        self.progress_bar.stop()
        self.progress_bar.destroy()

    def run_gui(self):
        self.root.mainloop()

    def stock_data(self, num_stock, invalid_label):
        historical_data_list = []

        for _ in range(num_stock):
            while True:
                stock = simpledialog.askstring("Enter Stock Symbol", "Enter the stock symbol: ")
                if not stock:
                    break

                stock = stock.upper().replace(" ", "")
                historical_data = self.nn_optimizer.historical_stock_data(stock)
                if not historical_data.empty:
                    historical_data_list.append((stock, historical_data))
                    break
                else:
                    self.show_error_message(f"Invalid stock ticker or no data available for {stock}. Please choose again.")

        return historical_data_list

    def display_results(self, optimal_weights, title):
        self.result_text.insert(tk.END, f"\n{title} Portfolio:\n")
        for stock, weight in zip([stock for stock, _ in self.historical_data_list], optimal_weights):
            self.result_text.insert(tk.END, f"   {stock}: {weight:.2f}%\n")
        self.result_text.insert(tk.END, "\n")

    def show_error_message(self, message):
        tk.messagebox.showerror("Error", message)

if __name__ == "__main__":
    nn_optimizer = NeuralNetOptimizer()
    mc_optimizer = MonteCarloOptimizer()
    gui = PortfolioGUI(nn_optimizer, mc_optimizer)
    gui.run_gui()