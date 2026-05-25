import numpy as np
from scipy.special import j0

from rayleighchannel import RayleighChannel
from ricianchannel import RicianChannel


EPS = 1e-12


def _to_db(amplitude):
    return 20.0 * np.log10(np.abs(amplitude) + EPS)


def _rms_delay_spread(delays, gains_db):
    powers = 10 ** (gains_db / 10.0)
    powers = powers / np.sum(powers)
    tau_mean = np.sum(powers * delays)
    tau_second = np.sum(powers * delays**2)
    return np.sqrt(max(0.0, tau_second - tau_mean**2))


def run_channel_simulation(
    fc,
    v_kmh,
    Fs,
    delays,
    gains,
    PL0,
    n,
    sigma,
    fading_type="Rayleigh",
    K_dB=6,
):
    """
    Ejecuta la simulacion del canal sin depender de tkinter.

    Los retardos se reciben en segundos. Fs representa la frecuencia de muestreo
    de la evolucion temporal del fading, no la resolucion de los retardos
    multicamino; la selectividad por retardo se evalua analiticamente en H(f).
    """
    fc = float(fc)
    v_kmh = float(v_kmh)
    base_Fs = float(Fs)
    delays = np.asarray(delays, dtype=float)
    gains = np.asarray(gains, dtype=float)

    if fc <= 0:
        raise ValueError("La frecuencia portadora debe ser mayor que cero.")
    if base_Fs <= 0:
        raise ValueError("Fs debe ser mayor que cero.")
    if delays.ndim != 1 or gains.ndim != 1 or len(delays) == 0:
        raise ValueError("Retardos y ganancias deben ser listas no vacias.")
    if len(delays) != len(gains):
        raise ValueError("Retardos y ganancias deben tener el mismo numero de elementos.")
    if np.any(delays < 0):
        raise ValueError("Los retardos no pueden ser negativos.")

    c = 3e8
    v_ms = v_kmh / 3.6
    fD = abs(v_ms / c) * fc

    time_Fs = max(base_Fs, 20.0 * fD) if fD > 0 else base_Fs
    time_Fs = min(time_Fs, 100_000.0)
    N_samples = int(np.clip(round(0.25 * time_Fs), 2_000, 20_000))

    if fading_type == "Rician":
        chan = RicianChannel(time_Fs, fD, delays, gains, K_dB=K_dB)
    else:
        chan = RayleighChannel(time_Fs, fD, delays, gains)

    # Desvanecimiento de pequena escala: suma coherente de las mismas componentes.
    sig = np.ones(N_samples, dtype=complex)
    path_taps_time = chan.path_coefficients(N_samples)
    carrier_phase = np.exp(-1j * 2.0 * np.pi * fc * delays)
    components_complex = path_taps_time * carrier_phase[:, np.newaxis] * sig[np.newaxis, :]
    y_small = np.sum(components_complex, axis=0)

    time = np.arange(N_samples) / time_Fs
    power_small_db = _to_db(y_small)
    multipath_components = [_to_db(component) for component in components_complex]

    # Desvanecimiento de gran escala.
    distancias = np.linspace(1.0, 100.0, 80)
    large_scale_gain = chan.large_scale_fading(distancias, fc, PL0=PL0, n=n, sigma=sigma, d0=1.0)
    potencias_large_db = _to_db(large_scale_gain)

    # Parametros de coherencia.
    Tc = 0.423 / fD if fD > 0 else float("inf")
    tau_rms = _rms_delay_spread(delays, gains)
    Bc = 1.0 / (5.0 * tau_rms) if tau_rms > 0 else float("inf")

    # Respuesta frecuencial: snapshot consistente con la primera muestra temporal.
    h_taps = path_taps_time[:, 0]
    bw_hz = 5e6
    freq_offsets = np.linspace(-bw_hz, bw_hz, 4096)
    freqs_base = freq_offsets
    H_base = chan.channel_response(freqs_base, h_taps)
    mag_base_db = _to_db(H_base)

    freqs_fc = fc + freq_offsets
    H_fc = chan.channel_response(freqs_fc, h_taps)
    mag_fc_db = _to_db(H_fc)

    # Autocorrelacion temporal teorica del modelo Doppler.
    if fD > 0:
        corr_t_max = min(max(5.0 * Tc, 0.05), time[-1])
        delta_t = np.linspace(0.0, corr_t_max, 1000)
        diffuse_corr = j0(2.0 * np.pi * fD * delta_t)
        if fading_type == "Rician":
            K = chan.K
            R_t = np.abs((K * np.exp(1j * 2.0 * np.pi * fD * delta_t) + diffuse_corr) / (K + 1.0))
        else:
            R_t = np.abs(diffuse_corr)
    else:
        delta_t = np.linspace(0.0, time[-1], 1000)
        R_t = np.ones_like(delta_t)

    # Correlacion frecuencial obtenida directamente del PDP.
    powers = 10 ** (gains / 10.0)
    powers = powers / np.sum(powers)
    if np.isfinite(Bc):
        corr_f_max = min(max(5.0 * Bc, 1e6), 20e6)
    else:
        corr_f_max = bw_hz
    delta_f = np.linspace(0.0, corr_f_max, 1000)
    R_f = np.abs(np.sum(powers[:, np.newaxis] * np.exp(-1j * 2.0 * np.pi * delays[:, np.newaxis] * delta_f[np.newaxis, :]), axis=0))

    return {
        "time": time,
        "power_small_db": power_small_db,
        "distancias": distancias,
        "potencias_large_db": potencias_large_db,
        "freqs_base": freqs_base,
        "mag_base_db": mag_base_db,
        "freqs_fc": freqs_fc,
        "mag_fc_db": mag_fc_db,
        "multipath_components": multipath_components,
        "Tc": Tc,
        "Bc": Bc,
        "tau_rms": tau_rms,
        "fD": fD,
        "time_Fs": time_Fs,
        "delta_t": delta_t,
        "R_t": R_t,
        "delta_f": delta_f,
        "R_f": R_f,
    }
