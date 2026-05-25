import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from itu_profiles import get_itu_profile
from simulator import run_channel_simulation

class ChannelSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Canal Inalámbrico")
        self.root.geometry("1150x780")
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.params_frame = ttk.LabelFrame(self.main_frame, text="Parámetros de Simulación")
        self.params_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.plot_frame = ttk.Frame(self.main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.plot_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tab_time = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_time, text="Dominio del Tiempo")
        self.fig_time, self.ax_time = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, master=self.tab_time)
        self.canvas_time.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.tab_freq = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_freq, text="Dominio de la Frecuencia")
        self.fig_freq, self.axs_freq = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas_freq = FigureCanvasTkAgg(self.fig_freq, master=self.tab_freq)
        self.canvas_freq.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.tab_space = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_space, text="Dominio Espacial")
        self.fig_space, self.ax_space = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas_space = FigureCanvasTkAgg(self.fig_space, master=self.tab_space)
        self.canvas_space.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.tab_comp = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_comp, text="Componentes Individuales")
        self.fig_comp, self.ax_comp = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas_comp = FigureCanvasTkAgg(self.fig_comp, master=self.tab_comp)
        self.canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.tab_corr_t = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_corr_t, text="Autocorrelación (Tc)")
        self.fig_corr_t, self.ax_corr_t = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas_corr_t = FigureCanvasTkAgg(self.fig_corr_t, master=self.tab_corr_t)
        self.canvas_corr_t.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.tab_corr_f = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_corr_f, text="Correlación Frec. (Bc)")
        self.fig_corr_f, self.ax_corr_f = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas_corr_f = FigureCanvasTkAgg(self.fig_corr_f, master=self.tab_corr_f)
        self.canvas_corr_f.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.create_inputs()
        
    def create_inputs(self):
        pad_y = (10, 2)
        
        ttk.Label(self.params_frame, text="Perfil de Canal (UIT-R):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.profile_var = tk.StringVar()
        self.cb_profile = ttk.Combobox(self.params_frame, textvariable=self.profile_var, state='readonly')
        self.cb_profile['values'] = (
            'Personalizado',
            'ITU Pedestrian A',
            'ITU Pedestrian B',
            'ITU Vehicular A',
            'ITU Vehicular B'
        )
        self.cb_profile.current(0)
        self.cb_profile.pack(fill=tk.X, padx=5)
        self.cb_profile.bind('<<ComboboxSelected>>', self.on_profile_change)
        
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
        
        ttk.Label(self.params_frame, text="Frecuencia Portadora fc (GHz):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_fc = ttk.Entry(self.params_frame, width=30)
        self.e_fc.insert(0, "2")
        self.e_fc.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Velocidad v (km/h):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_v = ttk.Entry(self.params_frame)
        self.e_v.insert(0, "30")
        self.e_v.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Retardos (us) [separados por comas]:").pack(anchor=tk.W, pady=(20, 2), padx=5)
        self.e_delays = ttk.Entry(self.params_frame)
        self.e_delays.insert(0, "0, 0.110, 0.190, 0.410, 0.920")
        self.e_delays.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Ganancias (dB) [separadas por comas]:").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_gains = ttk.Entry(self.params_frame)
        self.e_gains.insert(0, "0, -9.7, -19.2, -22.8, -27")
        self.e_gains.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Exponente de Pérdidas n:").pack(anchor=tk.W, pady=(20, 2), padx=5)
        self.e_n = ttk.Entry(self.params_frame)
        self.e_n.insert(0, "3.5")
        self.e_n.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.params_frame, text="Desviación Shadowing sigma (dB):").pack(anchor=tk.W, pady=pad_y, padx=5)
        self.e_sigma = ttk.Entry(self.params_frame)
        self.e_sigma.insert(0, "4")
        self.e_sigma.pack(fill=tk.X, padx=5)
        
        btn_run = ttk.Button(self.params_frame, text="Simular Canal", command=self.run_simulation)
        btn_run.pack(pady=30, fill=tk.X, padx=5)

        ttk.Label(self.params_frame, text="Resultados:", font=('', 10, 'bold')).pack(anchor=tk.W, pady=(10, 2), padx=5)
        self.lbl_fd = ttk.Label(self.params_frame, text="fD: -")
        self.lbl_fd.pack(anchor=tk.W, pady=2, padx=5)
        self.lbl_tau = ttk.Label(self.params_frame, text="tau_rms: -")
        self.lbl_tau.pack(anchor=tk.W, pady=2, padx=5)
        self.lbl_tc = ttk.Label(self.params_frame, text="Tc: -")
        self.lbl_tc.pack(anchor=tk.W, pady=2, padx=5)
        self.lbl_bc = ttk.Label(self.params_frame, text="Bc: -")
        self.lbl_bc.pack(anchor=tk.W, pady=2, padx=5)

    @staticmethod
    def format_time(seconds):
        if seconds == float('inf'):
            return "Infinito"
        if seconds < 1e-6:
            return f"{seconds*1e9:.2f} ns"
        if seconds < 1e-3:
            return f"{seconds*1e6:.2f} us"
        if seconds < 1:
            return f"{seconds*1e3:.2f} ms"
        return f"{seconds:.2f} s"

    @staticmethod
    def format_frequency(hz):
        if hz == float('inf'):
            return "Infinito"
        if hz >= 1e9:
            return f"{hz/1e9:.2f} GHz"
        if hz >= 1e6:
            return f"{hz/1e6:.2f} MHz"
        if hz >= 1e3:
            return f"{hz/1e3:.2f} kHz"
        return f"{hz:.2f} Hz"

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
            Fs = 10000.0
            
            delays_us = [float(x.strip()) for x in self.e_delays.get().split(',')]
            delays = [d * 1e-6 for d in delays_us]
            
            gains = [float(x.strip()) for x in self.e_gains.get().split(',')]
            
            if len(delays) != len(gains):
                raise ValueError("La lista de retardos y ganancias deben tener el mismo número de elementos.")
            if fc <= 0:
                raise ValueError("La frecuencia portadora debe ser mayor que cero.")
            if v_kmh < 0:
                raise ValueError("La velocidad no puede ser negativa.")
            if any(delay < 0 for delay in delays):
                raise ValueError("Los retardos no pueden ser negativos.")
            
            PL0 = 30.0
            n = float(self.e_n.get())
            sigma = float(self.e_sigma.get())
            if n <= 0:
                raise ValueError("El exponente de pérdidas debe ser mayor que cero.")
            if sigma < 0:
                raise ValueError("La desviación de shadowing no puede ser negativa.")
            
            fading_type = self.fading_var.get()
            k_db = 0.0
            if fading_type == "Rician":
                k_db = float(self.e_k.get())
                
        except ValueError as ve:
            messagebox.showerror("Error de Entrada", f"Por favor verifique los parámetros:\n{ve}")
            return
        
        try:
            results = run_channel_simulation(
                fc=fc, v_kmh=v_kmh, Fs=Fs, 
                delays=delays, gains=gains, 
                PL0=PL0, n=n, sigma=sigma,
                fading_type=fading_type,
                K_dB=k_db
            )
            
            self.ax_time.clear()
            for ax in self.axs_freq: ax.clear()
            self.ax_space.clear()
            self.ax_comp.clear()
            self.ax_corr_t.clear()
            self.ax_corr_f.clear()
            
            self.ax_time.plot(results['time'], results['power_small_db'])
            self.ax_time.set_title("Desvanecimiento de Pequeña Escala")
            self.ax_time.set_xlabel("Tiempo (s)")
            self.ax_time.set_ylabel("Magnitud [dB]")
            self.ax_time.grid(True)
            
            delays_us = np.array(delays) * 1e6
            self.axs_freq[0].stem(delays_us, gains, basefmt=" ", markerfmt="ro", linefmt="r-")
            self.axs_freq[0].set_title("Perfil de Retardo de Potencia (PDP)")
            self.axs_freq[0].set_xlabel("Retardo [μs]")
            self.axs_freq[0].set_ylabel("Ganancia [dB]")
            self.axs_freq[0].grid(True)
            
            freq_offset_mhz = (results['freqs_fc'] - fc) / 1e6
            self.axs_freq[1].plot(freq_offset_mhz, results['mag_fc_db'])
            self.axs_freq[1].axvline(0, color='red', linestyle='--', label=f"fc = {fc/1e9:.2f} GHz")
            self.axs_freq[1].set_title("Respuesta Frecuencial (Paso Banda)")
            self.axs_freq[1].set_xlabel("Desplazamiento respecto a fc [MHz]")
            self.axs_freq[1].set_ylabel("Magnitud [dB]")
            self.axs_freq[1].legend()
            self.axs_freq[1].grid(True)
            
            self.ax_space.plot(results['distancias'], results['potencias_large_db'])
            self.ax_space.set_title("Pérdida de Gran Escala")
            self.ax_space.set_xlabel("Distancia (m)")
            self.ax_space.set_ylabel("Ganancia de canal [dB]")
            self.ax_space.grid(True)
            
            Tc = results['Tc']
            Bc = results['Bc']

            self.lbl_fd.config(text=f"fD: {self.format_frequency(results['fD'])}")
            self.lbl_tau.config(text=f"tau_rms: {self.format_time(results['tau_rms'])}")
            self.lbl_tc.config(text=f"Tc: {self.format_time(Tc)}")
            self.lbl_bc.config(text=f"Bc: {self.format_frequency(Bc)}")
            
            for i, comp in enumerate(results['multipath_components']):
                self.ax_comp.plot(results['time'], comp, alpha=0.5, label=f"Rayo {i+1}")
            self.ax_comp.plot(results['time'], results['power_small_db'], color='black', linewidth=2, label="Suma Total")
            self.ax_comp.set_title("Componentes Individuales vs. Señal Total")
            self.ax_comp.set_xlabel("Tiempo (s)")
            self.ax_comp.set_ylabel("Potencia [dB]")
            self.ax_comp.legend()
            self.ax_comp.grid(True)
            
            self.ax_corr_t.plot(results['delta_t'] * 1e3, results['R_t'])
            self.ax_corr_t.axhline(y=0.5, color='r', linestyle='--', label="Correlación 0.5")
            if np.isfinite(Tc):
                self.ax_corr_t.axvline(Tc * 1e3, color='k', linestyle=':', label=f"Tc = {self.format_time(Tc)}")
            self.ax_corr_t.set_title("Autocorrelación Temporal")
            self.ax_corr_t.set_xlabel("Delta t [ms]")
            self.ax_corr_t.set_ylabel("Coeficiente de Correlación")
            self.ax_corr_t.legend()
            self.ax_corr_t.grid(True)
            
            df_plot = results['delta_f'] / 1e6
            self.ax_corr_f.plot(df_plot, results['R_f'])
            self.ax_corr_f.axhline(y=0.5, color='r', linestyle='--', label="Correlación 0.5")
            if np.isfinite(Bc):
                self.ax_corr_f.axvline(Bc / 1e6, color='k', linestyle=':', label=f"Bc = {self.format_frequency(Bc)}")
            self.ax_corr_f.set_title("Correlación en Frecuencia")
            self.ax_corr_f.set_xlabel("Delta f [MHz]")
            self.ax_corr_f.set_ylabel("Coeficiente de Correlación")
            self.ax_corr_f.legend()
            self.ax_corr_f.grid(True)

            self.fig_time.tight_layout(pad=3.0)
            self.fig_freq.tight_layout(pad=3.0)
            self.fig_space.tight_layout(pad=3.0)
            self.fig_comp.tight_layout(pad=3.0)
            self.fig_corr_t.tight_layout(pad=3.0)
            self.fig_corr_f.tight_layout(pad=3.0)
            
            self.canvas_time.draw()
            self.canvas_freq.draw()
            self.canvas_space.draw()
            self.canvas_comp.draw()
            self.canvas_corr_t.draw()
            self.canvas_corr_f.draw()
            
        except Exception as e:
            messagebox.showerror("Error en la Simulación", f"Se produjo un error durante la simulación:\n{e}")
