import numpy as np


class RicianChannel:
    def __init__(self, Fs, fD, delays, gains, K_dB=6):
        """
        Canal Rician de banda angosta con linea de vista en la primera trayectoria.

        Fs: frecuencia de muestreo de la evolucion temporal del fading [Hz]
        fD: Doppler maximo [Hz]
        delays: retardos de cada trayectoria [s]
        gains: ganancias relativas de cada trayectoria [dB]
        K_dB: factor K [dB], relacion potencia LOS / potencia difusa
        """
        self.Fs = float(Fs)
        self.fD = float(fD)
        self.delays = np.asarray(delays, dtype=float)
        self.gains_db = np.asarray(gains, dtype=float)
        self.K = 10 ** (float(K_dB) / 10.0)

        if self.Fs <= 0:
            raise ValueError("Fs debe ser mayor que cero.")
        if self.fD < 0:
            raise ValueError("fD no puede ser negativo.")
        if self.delays.ndim != 1 or self.gains_db.ndim != 1:
            raise ValueError("delays y gains deben ser listas unidimensionales.")
        if len(self.delays) == 0:
            raise ValueError("Debe existir al menos una trayectoria.")
        if len(self.delays) != len(self.gains_db):
            raise ValueError("delays y gains deben tener la misma longitud.")
        if np.any(self.delays < 0):
            raise ValueError("Los retardos no pueden ser negativos.")

        self.gains = 10 ** (self.gains_db / 20.0)
        power_linear = self.gains**2
        sum_power = np.sum(power_linear)
        if sum_power <= 0:
            raise ValueError("La potencia total del PDP debe ser mayor que cero.")

        self.gains = self.gains / np.sqrt(sum_power)
        self.num_paths = len(self.delays)

    def jakes_fading(self, N, N_s=32, rng=None):
        """
        Genera el componente difuso Rayleigh mediante suma de sinusoides.
        """
        N = int(N)
        if N <= 0:
            return np.array([], dtype=complex)

        rng = rng if rng is not None else np.random.default_rng()

        if self.fD == 0:
            sample = (rng.normal() + 1j * rng.normal()) / np.sqrt(2.0)
            return np.full(N, sample, dtype=complex)

        t = np.arange(N) / self.Fs
        phi_n = 2.0 * np.pi * rng.random(N_s)
        alpha_n = 2.0 * np.pi * np.arange(1, N_s + 1) / N_s

        h = np.zeros(N, dtype=complex)
        for alpha, phi in zip(alpha_n, phi_n):
            h += np.exp(1j * (2.0 * np.pi * self.fD * np.cos(alpha) * t + phi))

        h = h / np.sqrt(N_s)
        mean_power = np.mean(np.abs(h) ** 2)
        if mean_power > 0:
            h = h / np.sqrt(mean_power)
        return h

    def rician_fading(self, N, rng=None):
        """
        Combina un componente LOS y un componente difuso segun el factor K.
        """
        N = int(N)
        if N <= 0:
            return np.array([], dtype=complex)

        rng = rng if rng is not None else np.random.default_rng()
        rayleigh = self.jakes_fading(N, rng=rng)
        t = np.arange(N) / self.Fs
        theta = 2.0 * np.pi * rng.random()
        los = np.exp(1j * (2.0 * np.pi * self.fD * t + theta))

        return (
            np.sqrt(self.K / (self.K + 1.0)) * los
            + np.sqrt(1.0 / (self.K + 1.0)) * rayleigh
        )

    def path_coefficients(self, N):
        """
        Retorna una matriz compleja [num_paths, N] con los coeficientes
        de fading y ganancia de cada trayectoria, sin fase de portadora.
        """
        rng = np.random.default_rng()
        fading = []
        for i in range(self.num_paths):
            if i == 0:
                fading.append(self.rician_fading(N, rng=rng))
            else:
                fading.append(self.jakes_fading(N, rng=rng))
        return self.gains[:, np.newaxis] * np.vstack(fading)

    def filter(self, x, fc=None, return_components=False):
        """
        Aplica el equivalente de banda angosta del canal a una senal x.
        Si fc se proporciona, incluye la fase de portadora exp(-j 2 pi fc tau).
        """
        x = np.asarray(x, dtype=complex)
        components = self.path_coefficients(len(x)) * x[np.newaxis, :]

        if fc is not None:
            carrier_phase = np.exp(-1j * 2.0 * np.pi * float(fc) * self.delays)
            components = components * carrier_phase[:, np.newaxis]

        y = np.sum(components, axis=0)
        if return_components:
            return y, components
        return y

    def large_scale_fading(self, d, fc, PL0=30, n=3.5, sigma=4, d0=1):
        """
        Modelo log-distance + shadowing log-normal.
        """
        d = np.asarray(d, dtype=float)
        if np.any(d <= 0) or d0 <= 0:
            raise ValueError("Las distancias deben ser mayores que cero.")

        shadowing = np.random.normal(0.0, sigma, size=d.shape)
        total_loss_dB = PL0 + 10.0 * n * np.log10(d / d0) + shadowing
        return 10 ** (-total_loss_dB / 20.0)

    def channel_response(self, freqs, h_taps):
        """
        Calcula H(f) = sum_i h_i exp(-j 2 pi f tau_i) para las frecuencias dadas.
        """
        freqs = np.asarray(freqs, dtype=float)
        h_taps = np.asarray(h_taps, dtype=complex)
        if len(h_taps) != self.num_paths:
            raise ValueError("h_taps debe tener un tap por trayectoria.")

        phase = np.exp(-1j * 2.0 * np.pi * self.delays[:, np.newaxis] * freqs[np.newaxis, :])
        return np.sum(h_taps[:, np.newaxis] * phase, axis=0)

    def impulse_response(self):
        """
        Devuelve los retardos y una realizacion instantanea de taps complejos.
        """
        taps = self.path_coefficients(1)[:, 0]
        return self.delays.copy(), taps
