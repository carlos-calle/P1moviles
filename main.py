import tkinter as tk
from gui import ChannelSimulatorApp

def main():
    """
    Punto de entrada lógico de la aplicación.
    Levanta la instancia tonta del root de Tkinter y delega el manejo a gui.py.
    """
    root = tk.Tk()
    app = ChannelSimulatorApp(root)
    
    # Inicia una simulación automáticamente después de arrancar para tener los gráficos pre-dibujados
    root.after(100, app.run_simulation)
    
    # Bucle infinito del gestor de ventanas
    root.mainloop()

if __name__ == "__main__":
    main()
