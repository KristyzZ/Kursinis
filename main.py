import tkinter as tk
from ui.portfolio_app import PortfolioApp


def main():
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
