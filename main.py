import tkinter as tk
from gui import ChannelSimulatorApp

def main():
    """
    Punto de entrada de la aplicación.
    """
    root = tk.Tk()
    app = ChannelSimulatorApp(root)
    root.after(100, app.run_simulation)
    root.mainloop()

if __name__ == "__main__":
    main()
