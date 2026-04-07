import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Lógicas separadas
from itu_profiles import get_itu_profile
from simulator import run_channel_simulation

class ChannelSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Canal Inalámbrico")
        self.root.geometry("1100x750")
        
        # Layout principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.params_frame = ttk.LabelFrame(self.main_frame, text="Parámetros de Simulación")
        self.params_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Configurar Notebook (Pestañas)
        self.notebook = ttk.Notebook(self.plot_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Tiempo
        self.tab_time = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_time, text="Dominio del Tiempo")
        self.fig_time, self.axs_time = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, master=self.tab_time)
        self.canvas_time.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 2: Frecuencia
        self.tab_freq = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_freq, text="Dominio de la Frecuencia")
        self.fig_freq, self.axs_freq = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas_freq = FigureCanvasTkAgg(self.fig_freq, master=self.tab_freq)
        self.canvas_freq.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 3: Espacio
        self.tab_space = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_space, text="Dominio Espacial")
        self.fig_space, self.ax_space = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas_space = FigureCanvasTkAgg(self.fig_space, master=self.tab_space)
        self.canvas_space.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.create_inputs()
        
    def create_inputs(self):
        pad_y = (10, 2)
        
        # Profile selector
        ttk.Label(self.params_frame, text="Perfil de Canal (UIT-R):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.profile_var = tk.StringVar()
        self.cb_profile = ttk.Combobox(self.params_frame, textvariable=self.profile_var, state='readonly')
        self.cb_profile['values'] = ('Personalizado', 'ITU Pedestrian A', 'ITU Pedestrian B', 'ITU Vehicular A', 'ITU Vehicular B')
        self.cb_profile.current(0)
        self.cb_profile.pack(fill=tk.X, padx=5)
        self.cb_profile.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        # Fading Model Selector
        ttk.Label(self.params_frame, text="Modelo de Fading:").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.fading_var = tk.StringVar(value="Rayleigh")
        
        frame_radio = ttk.Frame(self.params_frame)
        frame_radio.pack(fill=tk.X, padx=5)
        
        rb_rayleigh = ttk.Radiobutton(frame_radio, text="Rayleigh (NLoS)", variable=self.fading_var, value="Rayleigh", command=self.on_fading_change)
        rb_rayleigh.pack(side=tk.LEFT, padx=(0, 10))
        
        rb_rician = ttk.Radiobutton(frame_radio, text="Rician (LoS)", variable=self.fading_var, value="Rician", command=self.on_fading_change)
        rb_rician.pack(side=tk.LEFT)
        
        self.lbl_k = ttk.Label(self.params_frame, text="Factor K (dB):")
        self.lbl_k.pack(anchor=tk.W, pady=(5, 2), padx=5)
        self.e_k = ttk.Entry(self.params_frame)
        self.e_k.insert(0, "10")
        self.e_k.pack(fill=tk.X, padx=5)
        
        self.on_fading_change()
        
        # General Params
        ttk.Label(self.params_frame, text="Frecuencia Portadora fc (GHz):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_fc = ttk.Entry(self.params_frame, width=30)
        self.e_fc.insert(0, "2")
        self.e_fc.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Velocidad v (km/h):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_v = ttk.Entry(self.params_frame)
        self.e_v.insert(0, "30")
        self.e_v.pack(fill=tk.X, padx=5)
        
        # Small Scale
        ttk.Label(self.params_frame, text="Retardos (s) [separados por comas]:").pack(anchor=tk.W, pady=(20, 2), padx=5)
        self.e_delays = ttk.Entry(self.params_frame)
        self.e_delays.insert(0, "0, 0.000110, 0.000190, 0.000410, 0.000920")
        self.e_delays.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Ganancias (dB) [separadas por comas]:").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_gains = ttk.Entry(self.params_frame)
        self.e_gains.insert(0, "0, -9.7, -19.2, -22.8, -27")
        self.e_gains.pack(fill=tk.X, padx=5)
        
        # Large Scale (Entorno Urbano)
        ttk.Label(self.params_frame, text="Exponente de Pérdidas n:").pack(anchor=tk.W, pady=(20, 2), padx=5)
        self.e_n = ttk.Entry(self.params_frame)
        self.e_n.insert(0, "3.5")
        self.e_n.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Desviación Shadowing sigma:").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_sigma = ttk.Entry(self.params_frame)
        self.e_sigma.insert(0, "4")
        self.e_sigma.pack(fill=tk.X, padx=5)
        
        # Run Button
        btn_run = ttk.Button(self.params_frame, text="Simular Canal", command=self.run_simulation)
        btn_run.pack(pady=30, fill=tk.X, padx=5)

    def on_fading_change(self):
        if self.fading_var.get() == "Rician":
            self.e_k.state(['!disabled'])
        else:
            self.e_k.state(['disabled'])

    def on_profile_change(self, event=None):
        profile_name = self.profile_var.get()
        if profile_name == 'Personalizado':
            return
            
        data = get_itu_profile(profile_name)
        
        if data:
            self.e_delays.delete(0, tk.END)
            self.e_delays.insert(0, data['delays'])
            
            self.e_gains.delete(0, tk.END)
            self.e_gains.insert(0, data['gains'])
            
            self.e_v.delete(0, tk.END)
            self.e_v.insert(0, data['v'])

    def run_simulation(self):
        try:
            fc = float(self.e_fc.get()) * 1e9
            v_kmh = float(self.e_v.get())
            Fs = 10000.0  # Frecuencia de muestreo estática
            
            delays = [float(x.strip()) for x in self.e_delays.get().split(',')]
            gains = [float(x.strip()) for x in self.e_gains.get().split(',')]
            
            if len(delays) != len(gains):
                raise ValueError("La lista de retardos y ganancias deben tener el mismo número de elementos.")
            
            PL0 = 30.0  # Pérdida de referencia estática (dB)
            n = float(self.e_n.get())
            sigma = float(self.e_sigma.get())
            
            fading_type = self.fading_var.get()
            k_db = 0.0
            if fading_type == "Rician":
                k_db = float(self.e_k.get())
                
        except ValueError as ve:
            messagebox.showerror("Error de Entrada", f"Por favor verifique los parámetros:\n{ve}")
            return
        
        try:
            # Llamada al Back-End Computacional
            results = run_channel_simulation(
                fc=fc, v_kmh=v_kmh, Fs=Fs, 
                delays=delays, gains=gains, 
                PL0=PL0, n=n, sigma=sigma,
                fading_type=fading_type,
                K_dB=k_db
            )
            
            # Limpiamos todas las gráficas
            for ax in self.axs_time: ax.clear()
            for ax in self.axs_freq: ax.clear()
            self.ax_space.clear()
            
            # --- PESTAÑA 1: TIEMPO ---
            # 1A: Desvanecimiento pequeña escala (Suma total)
            self.axs_time[0].plot(results['time'], results['power_small_db'])
            self.axs_time[0].set_title("Desvanecimiento (Toda la Señal)")
            self.axs_time[0].set_xlabel("Tiempo (s)")
            self.axs_time[0].set_ylabel("Potencia [dB]")
            self.axs_time[0].grid(True)
            
            # 1B: Componentes Multi-paths individuales
            for i, comp_power in enumerate(results['multipath_components']):
                self.axs_time[1].plot(results['time'], comp_power, label=f"Eco {i+1}")
            self.axs_time[1].set_title("Componentes Multipaths Individuales")
            self.axs_time[1].set_xlabel("Tiempo (s)")
            self.axs_time[1].set_ylabel("Potencia [dB]")
            self.axs_time[1].legend(loc='upper right', fontsize='small')
            self.axs_time[1].grid(True)
            
            # --- PESTAÑA 2: FRECUENCIA ---
            # 2A: Perfil de Retardo de Potencia (PDP)
            delays_us = np.array(delays) * 1e6
            self.axs_freq[0].stem(delays_us, gains, basefmt=" ", markerfmt="ro", linefmt="r-")
            self.axs_freq[0].set_title("Perfil de Retardo de Potencia (PDP)")
            self.axs_freq[0].set_xlabel("Retardo [μs]")
            self.axs_freq[0].set_ylabel("Ganancia [dB]")
            self.axs_freq[0].grid(True)
            
            # 2B: Respuesta Frecuencia (Paso Banda)
            self.axs_freq[1].plot(results['freqs_fc']/1e9, results['mag_fc_db'])
            self.axs_freq[1].vlines([fc/1e9], np.min(results['mag_fc_db']), np.max(results['mag_fc_db']), colors='red', label=f"fc = {fc/1e9:.2f} GHz")
            self.axs_freq[1].set_title("Respuesta Frecuencial (Paso Banda)")
            self.axs_freq[1].set_xlabel("Frecuencia [GHz]")
            self.axs_freq[1].set_ylabel("Magnitud [dB]")
            self.axs_freq[1].legend()
            self.axs_freq[1].grid(True)
            
            # --- PESTAÑA 3: ESPACIO ---
            # 3A: Gran escala (Distancia)
            self.ax_space.plot(results['distancias'], results['potencias_large_db'])
            self.ax_space.set_title("Desvanecimiento de Gran Escala")
            self.ax_space.set_xlabel("Distancia (m)")
            self.ax_space.set_ylabel("Potencia [dB]")
            self.ax_space.grid(True)
            
            # Refrescar layout y Canvas
            self.fig_time.tight_layout(pad=3.0)
            self.fig_freq.tight_layout(pad=3.0)
            self.fig_space.tight_layout(pad=3.0)
            
            self.canvas_time.draw()
            self.canvas_freq.draw()
            self.canvas_space.draw()
            
        except Exception as e:
            messagebox.showerror("Error en la Simulación", f"Se produjo un error crítico durante la simulación:\n{e}")
