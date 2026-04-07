# Fundamentos Matemáticos e Implementación de Canales (Rayleigh y Rician)

Este documento detalla rigurosamente la formulación matemática de los canales inalámbricos modelados y su traducción exacta a la implementación computacional en Python dentro del simulador. Está estructurado para ser una herramienta de defensa sobre las decisiones técnicas del proyecto.

---

## 1. Desvanecimiento Rayleigh (Rayleigh Fading)

### 1.1 Base Matemática

El modelo Rayleigh caracteriza la envolvente estadística de una señal de radio en un entorno urbano densamente poblado donde **no hay línea de visión directa (NLOS - Non-Line of Sight)**. La señal en el receptor se forma únicamente a partir de la superposición de infinitas ondas difusas (ecos, reflexiones, refracciones).

Acorde al **Teorema del Límite Central**, la superposición de un número grande de variables aleatorias independientes resulta en un proceso estocástico complejo gaussiano. La envolvente de esta señal sigue una distribución de Rayleigh.

Para simular esto computacionalmente de forma realista en el dominio temporal, se usa el **Modelo Determinista de Jakes**, que aproxima el espectro Doppler clásico (en forma de "U") como una suma de $N_s$ osciladores con frecuencias y fases distintas:

$$ h_{Rayleigh}(t) = \frac{1}{\sqrt{N_s}} \sum_{n=1}^{N_s} e^{j(2\pi f_D \cos(\alpha_n)t + \phi_n)} $$

Donde:
*   $f_D$: Es el ensanchamiento Doppler máximo (proporcional a la velocidad del móvil).
*   $\alpha_n$: Ángulo de llegada de la onda plana $n$-ésima.
*   $\phi_n$: Fase aleatoria uniformemente distribuida en el rango $[0, 2\pi)$.
*   $1/\sqrt{N_s}$: Constante de normalización que asegura que el proceso aleatorio mantenga como resultado una varianza promedio unitaria ($\sigma^2 = 1$).

### 1.2 Implementación en Código (`rayleighchannel.py`)

Esta sumatoria es traducida paso por paso en el bloque `jakes_fading()`:

```python
def jakes_fading(self, N, N_s=16):
    t = np.arange(N) / self.Fs
    phi_n = 2 * np.pi * np.random.rand(N_s)             # Fases aleatorias ϕ_n
    alpha_n = 2 * np.pi * np.arange(1, N_s+1) / N_s     # Ángulos determinísticos uniformes α_n
    
    h = np.zeros(N, dtype=complex)
    for n in range(N_s):
        # Expresión e^(j * (2*pi*fD*cos(α)*t + ϕ))
        h += np.exp(1j * (2*np.pi*self.fD*np.cos(alpha_n[n])*t + phi_n[n]))
    
    # Normalización matemática de potencia pura
    h = h * (1/np.sqrt(N_s))
    return h
```

---

## 2. Desvanecimiento Rician (Rician Fading)

### 2.1 Base Matemática

El modelo Rician expande los supuestos sumando la característica de un entorno rural o semi-urbano donde **sí hay una componente de Visión Directa o Dominante (LOS - Line of Sight)** muy fuerte en adición a los múltiples rebotes (NLOS).

Este modelo se parametriza a través del **Factor K**, que define la proporción ("ratio") entre la potencia recibida desde la vía directa ($P_{LOS}$) respecto a la potencia dispersada sumada de los demás trayectos ($P_{NLOS}$ o $2\sigma^2$):

$$ K = \frac{P_{LOS}}{P_{NLOS}} $$
$$ K_{dB} = 10 \log_{10}(K) $$

Para componer un desvanecimiento en el tiempo que respete esta estadística, se genera un vector de desvanecimiento complejo sumando un tono armónico puro determinista (LOS) a un proceso Rayleigh difuso aleatorio, ponderando ambas partes por las fracciones de la energía normalizada obtenida a través de $K$:

$$ h_{Rician}(t) = \sqrt{\frac{K}{K+1}} h_{LOS}(t) + \sqrt{\frac{1}{K+1}} h_{Rayleigh}(t) $$

Donde:
*   $h_{LOS}(t) = e^{j(2\pi f_D t + \theta_0)}$ : Componente determinista oscilando al límite del doppler máximo.

### 2.2 Implementación en Código (`ricianchannel.py`)

La suma de estas dos potencias, multiplicadas por la ganancia unitaria es calculada en `rician_fading()` de la siguiente manera:

```python
def rician_fading(self, N):
    # Genera componente NLOS usando el Modelo de Jakes
    rayleigh = self.jakes_fading(N)
    
    # Crea el componente componente LOS determinista con fase base θ0 aleatoria
    t = np.arange(N) / self.Fs
    theta = 2 * np.pi * np.random.rand()
    los = np.exp(1j * (2 * np.pi * self.fD * t + theta))
    
    # Implementa la sumatoria ponderada basada en el factor K (h_Rician)
    rician = (np.sqrt(self.K/(self.K+1)) * los) + (np.sqrt(1/(self.K+1)) * rayleigh)
    return rician
```

---

## 3. Simulación Multipath Diferenciada y Convolutiva (Filtro Adaptativo)

En sistemas reales los ecos llegan con diferentes niveles de retardo $\tau$ y se modelan mediante el **Perfil de Retardo de Potencia (PDP)** que en el código se representan por los vectores `self.delays` y `self.gains`.

### 3.1 Respuesta Matemática Aplicada
El canal actuando sobre una señal de entrada $x(t)$ se comporta conceptualmente como un filtro lineal variante en el tiempo cuya formulación asume la convolución:
$$ y(t) = \sum_{i=0}^{P-1} a_i(t) \cdot x(t - \tau_i) $$
Donde $a_i(t)$ es el coeficiente de desvanecimiento dinámico de la trayectoria $i$ combinado con la atenuación del sistema en el espacio libre. Su sumatoria de potencia base lineal es internamente normalizada a `1` al instanciar las clases usando un factor de división equivalente a:
`gains = gains / sqrt(sum(gains^2))`

### 3.2 Justificación de Código (Rician frente a Rayleigh)
La distinción analítica principal requerida al evaluar un PDP (canal banda ancha real, que simula múltiples trayectorias) en un modelo Rician es que **solo físicamente el primer trayecto más corto puede representar la visión directa**. Los trayectos u ecos retardados no tienen línea de visión y por lo tanto son empíricamente ecos Rayleigh (NLOS).

Dicho formalismo está plasmado en la función `filter()` del `ricianchannel.py`:

```python
for i in range(self.num_paths):
    delay_samples = int(np.round(self.delays[i] * self.Fs))
    
    # Tratamiento Físico Correcto:
    if i == 0:
        # La 1ra vía que llega asume la visión directa dominante
        fading = self.rician_fading(N)
    else:
        # Las copias retardadas son simples ecos multipath (NLOS)
        fading = self.jakes_fading(N)
        
    x_delayed = np.concatenate([np.zeros(delay_samples), x])[:N]
    y += self.gains[i] * fading * x_delayed
```
Sin embargo, en la clase homóloga `RayleighChannel`, el modelo estricto asume que toda condición de espacio está ocluida. La implementación lo refleja eliminando la validación del índice $i$: a cada tap o trayectoria convolutiva del proceso en bucle, solo se le aplica indiscriminadamente `self.jakes_fading(N)`, obedeciendo cabalmente el formalismo del perfil puramente difuso.
