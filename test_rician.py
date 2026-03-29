import numpy as np
from rayleighchannel import RayleighChannel

Fs = 10000
fD = 30/3.6 / 3e8 * 2e9
delays = [0, 0.000110, 0.000190, 0.000410]
gains = [0, -9.7, -19.2, -22.8]

chan_ray = RayleighChannel(Fs, fD, delays, gains, K_factor_linear=0)
chan_ric = RayleighChannel(Fs, fD, delays, gains, K_factor_linear=10**(10/10)) # K=10dB

sig = 1j * np.ones(2000)
y_ray = chan_ray.filter(sig)
y_ric = chan_ric.filter(sig)

print(f"Rayleigh std_db: {np.std(20*np.log10(np.abs(y_ray)))}")
print(f"Rician 10dB std_db: {np.std(20*np.log10(np.abs(y_ric)))}")
print(f"Rician mean_db: {np.mean(20*np.log10(np.abs(y_ric)))}")

