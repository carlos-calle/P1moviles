# 4. Metodología – Desarrollo de la práctica

### Procedimiento y metodología utilizado
El desarrollo de la práctica se fundamenta en la simulación computacional del comportamiento de señales de radiofrecuencia en canales inalámbricos dispersivos. La metodología sigue una estructura paso a paso:
1. **Configuración de Variables Físicas:** Se introducen los parámetros operativos como la frecuencia portadora ($f_c$) y la velocidad relativa del receptor móvil ($v$).
2. **Definición del Perfil Multicamino (PDP):** Se seleccionan los retardos ($\tau_i$) y ganancias relativas ($P_i$) de los distintos caminos que recorre la señal, ya sea de forma manual o utilizando los perfiles estandarizados por la UIT-R M.1225.
3. **Selección del Modelo Estadístico:** Se elige entre el modelo **Rayleigh** (para entornos urbanos densos sin línea de vista - NLoS) o el modelo **Rician** (para entornos con un trayecto dominante o línea de vista - LoS, ajustando el factor de rician $K$).
4. **Ejecución de la Simulación Matemática:** El motor (backend) de la aplicación calcula la respuesta del canal. Emplea suma de sinusoides para modelar el efecto Doppler clásico de Jakes/Clarke. También genera la respuesta al impulso, la respuesta en frecuencia y el desvanecimiento a gran escala (Log-distancia + Shadowing).
5. **Representación Gráfica:** Finalmente, los resultados se mapean en la interfaz gráfica (GUI) mediante pestañas de tiempo, frecuencia, espacio, componentes individuales y correlaciones de coherencia, permitiendo inspeccionar los fenómenos estudiados desde varias perspectivas.

### Condiciones de canal y entornos de propagación
Para abarcar diferentes realidades físicas, se evalúan las condiciones estandarizadas **UIT-R M.1225**:
*   **Pedestrian A y B (Entorno Peatonal):** Simulan usuarios caminando (aprox. 3 km/h). Estos canales se caracterizan por una bajísima dispersión frecuencial (ensanchamiento Doppler pequeño), lo que significa que el canal cambia muy lentamente en el tiempo. Los retardos de los multicaminos son reducidos (menores a 1-3 $\mu s$).
*   **Vehicular A y B (Entorno Vehicular):** Simulan móviles a altas velocidades (60 a 120 km/h o más). El ensanchamiento Doppler es alto, provocando un desvanecimiento extremadamente rápido en el tiempo. En el caso de Vehicular B, existen dispersiones de retardo considerables (hasta 20 $\mu s$), lo que emula reflexiones lejanas (ej. montañas o edificios distantes).

### Observaciones a realizarse
*   **En el dominio del tiempo:** Se observarán las rápidas y profundas caídas de potencia (Deep Fades) provocadas por la interferencia constructiva y destructiva de los trayectos. La pestaña de componentes muestra las trayectorias individuales y la suma coherente usada para formar la señal total. Simultáneamente, se evaluará la caída media de la señal con la distancia (dominio espacial).
*   **En el dominio de la frecuencia:** Se examinará la respuesta espectral del canal (H(f)) para identificar si la banda del canal sufre una atenuación uniforme o si existen "muescas" (notches) donde ciertas frecuencias son fuertemente atenuadas debido a los retardos multicamino.

### Herramientas de software a utilizar
*   **Entorno base:** Python 3.x
*   **Librerías principales:**
    *   `numpy`: Esencial para el álgebra lineal, generación de variables estocásticas, y el manejo eficiente de vectores de señales en el tiempo y la frecuencia.
    *   `matplotlib`: Utilizada para el trazado de las respuestas en el dominio del tiempo, perfil de retardo de potencia (tallo/stem plot), respuesta frecuencial y correlaciones.
    *   `scipy`: Utilizada para evaluar la función de Bessel asociada a la autocorrelación temporal del modelo de Jakes.
    *   `tkinter` / `ttk`: Librería nativa para la construcción interactiva de la Interfaz Gráfica de Usuario (GUI).

---

# 5. Evaluación – Análisis de Resultados

*(Nota: Los siguientes puntos describen los resultados y comportamientos teóricos-prácticos que se evidencian al ejecutar el simulador)*

### Canal Rayleigh: Evaluación en el dominio del tiempo y distancia
*   **Desvanecimientos a Gran y Pequeña Escala:** 
    *   En la gráfica espacial, se observa una caída logarítmica de la potencia media al alejarse el RX del TX, sobre la cual se superponen fluctuaciones lentas aleatorias producto del ensombrecimiento (*Shadowing* log-normal). 
    *   En la gráfica temporal (a distancia fija), se observan fluctuaciones abruptas (decenas de dB) en periodos de milisegundos, evidenciando el desvanecimiento de pequeña escala de Rayleigh.
*   **Distintas frecuencias de operación ($f_c$):** A mayor frecuencia portadora ($f_c$), la longitud de onda ($\lambda$) disminuye. Esto incrementa el desplazamiento Doppler máximo ($f_D = v/\lambda$), haciendo que los cruces por cero en la amplitud sean más frecuentes.
*   **Distintas velocidades relativas ($v$):** Un aumento en la velocidad aumenta proporcionalmente el ensanchamiento Doppler ($f_D$). Visualmente, el desvanecimiento de pequeña escala fluctúa muchísimo más rápido (picos y valles más juntos en el tiempo).
*   **Distintas copias multicamino:** Aumentar el número de caminos incrementa la interferencia en la señal original. Sin embargo, por el teorema del límite central, la envolvente de la señal resultante convergerá firmemente a una distribución de Rayleigh.

### Canal Rayleigh: Evaluación en el dominio de la frecuencia
*   **Distintas frecuencias de operación ($f_c$):** Mover la frecuencia de operación desplaza la ventana de observación en el espectro, pero el ancho de banda de coherencia del canal (regido por la dispersión de retardos de los ecos) permanece igual.
*   **Distintas velocidades relativas ($v$):** La velocidad no afecta la forma de la atenuación selectiva en frecuencia en un instante de tiempo congelado ($t=0$). La velocidad afecta qué tan rápido cambia dicha respuesta en frecuencia a lo largo del tiempo.
*   **Distintas copias multi-camino y características:** Aumentar los retardos temporales de las copias (es decir, aumentar el $\tau_{rms}$ de dispersión de retardos) provoca que en la gráfica de *Respuesta Frecuencial* las oscilaciones o "muescas" (notches) se vuelvan más estrechas y abundantes a lo largo del espectro. 

### Parámetros de Coherencia
*   **Tiempo de Coherencia ($T_c$):** Inversamente proporcional al desplazamiento Doppler máximo ($T_c \approx 0.423 / f_D$). En los perfiles Peatonales, $T_c$ es grande (el canal es estable durante la transmisión de muchos símbolos). En perfiles Vehiculares, $T_c$ es pequeño.
*   **Ancho de Banda de Coherencia ($B_c$):** Inversamente proporcional a la dispersión de retardos RMS ($\tau_{rms}$). En el perfil *Vehicular B*, los altos retardos generan un $B_c$ muy pequeño, por lo que el canal será fuertemente selectivo en frecuencia.

### Categorías de degradación por dispersión en el tiempo
*   **Dominio del Tiempo:** La señal original se "ensancha" temporalmente debido a las copias retardadas. Si la duración del símbolo enviado ($T_s$) es menor o cercana a la dispersión de retardo ($\tau_{max}$), se produce **Interferencia Intersimbólica (ISI)**, degradando severamente la señal sin importar la relación señal a ruido (SNR).
*   **Dominio de la Frecuencia:** Un ensanchamiento temporal implica que el canal tiene un ancho de banda de coherencia estrecho ($B_c$). Si el ancho de banda de la señal ($B_s$) es mayor que $B_c$, distintas partes del espectro de la señal se atenuarán de forma diferente, distorsionando la información.

### Condiciones que producen los tipos de desvanecimiento
*   **Desvanecimiento Plano (Flat Fading):** Ocurre cuando el ancho de banda de la señal es mucho menor al ancho de banda de coherencia del canal ($B_s \ll B_c$), o equivalente, cuando la duración del símbolo es mucho mayor a la dispersión de retardos ($T_s \gg \tau_{rms}$). Toda la señal se atenúa por igual.
*   **Desvanecimiento Selectivo en Frecuencia:** Ocurre cuando el ancho de banda de la señal supera el ancho de banda de coherencia ($B_s > B_c$). Diferentes componentes frecuenciales sufren ganancias distintas (notches).
*   **Desvanecimiento Rápido (Fast Fading):** Ocurre cuando el tiempo de coherencia del canal es menor que la duración del símbolo ($T_c < T_s$). El canal cambia drásticamente en medio de la transmisión de un solo símbolo. Relacionado a altas velocidades.
*   **Desvanecimiento Lento (Slow Fading):** Ocurre cuando el canal cambia a un ritmo mucho más lento que el período de los símbolos transmitidos ($T_c \gg T_s$). Relacionado a bajas velocidades (perfil peatonal).

### Análisis para un canal Rician
*   Si se selecciona el modelo **Rician**, existe una línea de vista predominante (LoS). En el dominio del tiempo, la potencia de la señal ya no cae a profundidades tan drásticas (reducción de Deep Fades) debido a la componente constante (o variante determinística). 
*   A mayor factor $K$ (dB), la señal se parece más a un canal AWGN simple sin fluctuaciones, ya que la potencia difusa se vuelve insignificante en comparación a la potencia del rayo directo. La severidad del fading disminuye enormemente respecto al modelo Rayleigh.

### Concepto de dualidad Tiempo – Frecuencia
La dualidad se observa claramente en el simulador:
1.  **Ensanchamiento Temporal vs Selectividad Frecuencial:** Una gran dispersión temporal de los rayos (retardos largos en el dominio del tiempo) matemáticamente significa una caída en el ancho de banda de coherencia ($B_c \propto 1/\tau_{rms}$). Físicamente, un impulso en el tiempo se hace ancho, pero la respuesta frecuencial se vuelve "estrecha" u oscilante (selectiva).
2.  **Variación Temporal vs Dispersión Frecuencial (Doppler):** La rapidez con la que cambia la amplitud del canal en el dominio del tiempo (desvanecimiento rápido) se modela en frecuencia mediante el espectro Doppler ($f_D$). Un canal que varía rapidísimo en el tiempo produce un ensanchamiento grande del tono portador en el dominio de la frecuencia.
