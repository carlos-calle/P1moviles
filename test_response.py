import numpy as np
from rayleighchannel import RayleighChannel
import matplotlib.pyplot as plt

Fs = 10000
fD = 55
delays = [0, 0.000110, 0.000190, 0.000410]
gains = [0, -9.7, -19.2, -22.8]

chan_ric = RayleighChannel(Fs, fD, delays, gains, K_factor_linear=10)
freqs = np.linspace(-5000, 5000, 1024)
H_old = chan_ric.channel_response(1024, freqs)

def new_CR(self, N_freq, freqs):
    H = np.zeros_like(freqs, dtype=complex)
    for i in range(self.num_paths):
        fading_i = self.jakes_fading(1)[0]
        if i == 0 and self.K_factor > 0:
            K = self.K_factor
            los = 1
            fading_i = np.sqrt(K / (K + 1)) * los + np.sqrt(1 / (K + 1)) * fading_i
        H += self.gains[i] * fading_i * np.exp(-1j*2*np.pi*freqs*self.delays[i])
    return H

RayleighChannel.channel_response2 = new_CR
H_new = chan_ric.channel_response2(1024, freqs)

print(f"Old variance: {np.var(np.abs(H_old))}")
print(f"New variance: {np.var(np.abs(H_new))}")

