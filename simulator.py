import numpy as np
from rayleighchannel import RayleighChannel
from ricianchannel import RicianChannel

def run_channel_simulation(fc, v_kmh, Fs, delays, gains, PL0, n, sigma, fading_type="Rayleigh", K_dB=6):
    """
    Recibe variables de entrada limpias (provenientes de la GUI sin dependencia a `tkinter`),
    ejecuta la instanciación teórica de la simulación del canal base de propagación 
    y retorna diccionarios con los ejes computados para delegarle su dibujo libre a otra clase.
    """
    
    # 1. Cálculos base físicos
    v_ms = v_kmh / 3.6
    c = 3e8
    fD = (v_ms/c)*fc

    # Instanciamos el modelo de canal real
    if fading_type == "Rician":
        chan = RicianChannel(Fs, fD, delays, gains, K_dB=K_dB)
    else:
        chan = RayleighChannel(Fs, fD, delays, gains)
    
    # 2. Desvanecimiento de Pequeña Escala (Dominio Temporal)
    N_samples = 2000
    sig = 1j * np.ones(N_samples)
    y_small = chan.filter(sig)
    time = np.arange(len(y_small))/Fs
    power_small_db = 20*np.log10(np.abs(y_small) + 1e-10)
    
    # 2.1 Componentes Multipath Individuales
    multipath_components = []
    for i in range(len(delays)):
        if fading_type == "Rician" and i == 0:
            f = chan.rician_fading(N_samples)
        else:
            f = chan.jakes_fading(N_samples)
        comp_power_db = 20*np.log10(np.abs(chan.gains[i] * f) + 1e-10)
        multipath_components.append(comp_power_db)
    
    # 3. Desvanecimiento de Gran Escala (Dominio Espacial)
    distancias = np.linspace(1, 100, 50)
    potencias_large_db = [20*np.log10(chan.large_scale_fading(d, fc, PL0=PL0, n=n, sigma=sigma)) for d in distancias]
    
    # 4. Respuesta Frecuencial (Dominio Frecuencial / Banda Base)
    N_freq = 1024
    freqs_base = np.linspace(-Fs, Fs, N_freq)
    _, h_taps = chan.impulse_response()
    H_base = chan.channel_response(freqs_base, h_taps)
    mag_base_db = 20*np.log10(np.abs(H_base) + 1e-10)
    
    # 5. Respuesta Frecuencial (Paso Banda original sobre fc)
    # Evitamos aliasing visual limitando el ancho de banda a graficar a 10 MHz (±5 MHz) y subiendo puntos
    bw_hz = 5e6
    freqs_fc = np.linspace(fc - bw_hz, fc + bw_hz, 4096)
    H_fc = chan.channel_response(freqs_fc, h_taps)
    mag_fc_db = 20*np.log10(np.abs(H_fc) + 1e-10)
    
    return {
        'time': time,
        'power_small_db': power_small_db,
        'distancias': distancias,
        'potencias_large_db': potencias_large_db,
        'freqs_base': freqs_base,
        'mag_base_db': mag_base_db,
        'freqs_fc': freqs_fc,
        'mag_fc_db': mag_fc_db,
        'multipath_components': multipath_components
    }
