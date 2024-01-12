import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from portfolio_optimizer import PortfolioOptimizer

# PortfolioGUI class handles the graphical user interface
class PortfolioGUI:
    def __init__(self, optimizer):
        self.optimizer = optimizer
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
        num_stock_input = self.num_stock_entry.get()

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
            self.optimizer.portfolio_optimization(num_stock, invalid_label, self.result_text)
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

if __name__ == "__main__":
    optimizer = PortfolioOptimizer()
    gui = PortfolioGUI(optimizer)
    gui.run_gui()