# Reporte de Práctica: Simulación de Canal Inalámbrico (Rayleigh Fading & Path Loss)

**Materia / Asignatura:** Comunicaciones Inalámbricas
**Proyecto:** Simulador interactivo de propagación electromagnética multitrayecto y atenuación espacial.

---

## 1. Introducción y Marco Teórico

El objetivo de este proyecto es simular y comprender los fenómenos físicos que afectan irreversiblemente a una señal electromagnética cuando viaja desde una antena transmisora hacia un receptor móvil celular. El entorno físico no es perfecto; existen edificios, árboles, montañas y la misma distancia, lo que causa que la señal sufra de diferentes tipos de atenuación.

En nuestra simulación hemos abordado los dos problemas fundamentales estipulados por la teoría de comunicaciones:

### A. Desvanecimiento a Gran Escala (Large-Scale Fading)
Ocurre a lo largo de distancias extensas e involucra dos componentes:
1. **Path Loss (Pérdida de Trayectoria Log-Distancia):** A medida que nos alejamos de la antena base, la potencia cae logarítmicamente. La intensidad dependerá de un "exponente de pérdidas" ($n$). Si el espacio es totalmente libre, $n=2$, pero en la Tierra suele variar de $3$ a $5$.
2. **Shadowing (Ensombrecimiento Log-Normal):** Las caídas abruptas de señal al pasar por detrás de un edificio gigantesco. Es un fenómeno estadístico que se modela agregando una variable aleatoria Gaussiana (definida por la desviación $\sigma$) al cálculo de la pérdida logarítmica.

### B. Desvanecimiento a Pequeña Escala (Small-Scale Fading / Multitrayecto)
Ocurre por micro-variaciones debido a que la señal rebota en múltiples objetos locales antes de llegar a la antena:
1. **Rayleigh Fading (NLoS):** Las señales que rebotan llegan desfasadas. A veces se suman (interferencia constructiva) pero a veces se cancelan por completo (Deep Fades o ráfagas de silencio). Lo modelamos matemáticamente generando un "Proceso aleatorio de Rayleigh" que imite este comportamiento estadístico, el cual asume que no hay línea de vista.
2. **Rician Fading (LoS):** Cuando existe una Línea de Vista directa dominante y robusta entre el transmisor y el receptor, esta onda principal opaca al resto de rebotes. Se modela introduciendo una onda determinista emparejada a la suma estadística y parametrizada por el **Factor K**, que dicta qué tan fuerte es dicha onda directa versus la suma de los ecos refractados.
3. **Efecto Doppler:** El receptor está en movimiento (a cierta $v$ km/h). Esto ensancha el espectro de la señal percibida en el dominio de la frecuencia. A mayor velocidad, las variaciones (desvanecimientos) de la señal en el tiempo ocurren muchísimo más rápido. Para hacer esto de manera computacionalmente razonable e idéntica a la teoría, implementamos el **Modelo de Suma de Sinusoides de Jakes**, el cual aproxima la dispersión de este espectro Doppler.
4. **Selectividad en Frecuencia (Retardos):** Cada rebote viaja una distancia adicional y se retrasa algunos nanosegundos respecto a la línea de vista directa ("Taps" del canal). Esto origina que componentes de distintas frecuencias se anulen independientemente originando que nuestro canal actúe como un filtro caprichoso.

---

## 2. Arquitectura del Simulador (Decisiones de Programación)

Para evitar construir una aplicación desordenada (el típico "Código Espagueti" o un gran *God Script*), el simulador se programó aplicando principios modernos de separación de responsabilidades (Arquitectura Modular SOLID). La estructura de archivos del proyecto se divide así:

*   **`main.py` (Punto de Entrada):** El script lanzador. No tiene matemáticas, no dibuja ventanas, únicamente invoca el arranque del bucle de eventos (`mainloop`) de Tkinter.
*   **`gui.py` (Capa de Vista - Front-end):** Define de forma orientada a objetos toda la Interfaz Gráfica (`ChannelSimulatorApp`) en Tkinter. Su mayor complejidad radica en poseer capacidades para incrustar gráficos dinámicamente generados con `matplotlib` dentro del lienzo de la aplicación (usando `FigureCanvasTkAgg`), en vez de lanzarlos como pop-ups externos molestos.
*   **`simulator.py` (Controlador - Back-end):** Este es el motor del proyecto. Recolecta las variables estrictas numéricas, invoca al modelador core `rayleighchannel` y procesa matemáticamente cómo organizar las líneas de tiempo, las distancias y los espectros, para devolver todo empaquetado y crudo sin depender en absoluto de entornos visuales de escritorio.
*   **`rayleighchannel.py` (Lógica de Dominio Abstracta):** El núcleo de la simulación. Presenta la clase `RayleighChannel`. De aquí sobresale:
    *   Módulo `jakes_fading()`: Utiliza ciclos que suman sinusoides complejas para inyectar el ensanchamiento estocástico de la señal simulando los dispersores de ángulo de onda.
    *   Módulo `filter()`: Simula físicamente el "canal". Toma la señal que transmite el usuario y realiza una manipulación digital agregando "ceros de arrastre" (`np.concatenate`) imitando físicamente el tiempo físico de retraso de llegada de un eco, para luego multiplicar y atenuarlo por las restricciones de sus ganancias.
*   **`itu_profiles.py` (Repositorio de Datos):** Extrae limpiamente hacia aparte los diccionarios con la información estandarizada avalada por la recomendación **UIT-R M.1225**, conteniendo los retrasos, rebotes y atenuaciones características de entornos *Vehiculares* y *Peatonales* para uso de auto-completado. 
    * *Nota Docente sobre el Código:* Para mantener el programa visualmente agradable frente a bajas tasas de muestreo digital (Fs=10KHz, impuestas para reducir el coste de la RAM de la PC y evitar que se pasme), estos perfiles empíricos de la norma han sido intencionalmente escalados del orden de nanosegundos (reales) al de microsegundos, permitiendo notar dramáticamente sus efectos destructivos en los gráficos didácticos simulados a coste de estirar artificialmente la dimensión relativa del tiempo microscópico.

---

## 3. Análisis Técnico de los Resultados Gráficos Visuales

Al presionar "Simular Canal", notarás que el motor renderiza cuatro (4) gráficas. Cada una representa un factor teórico distinto del entorno celular y su inspección detallada resulta vital:

### 1. Desvanecimiento de Pequeña Escala (Arriba Izquierda)
*   **Eje:** Tiempo (s) contra Potencia (dB).
*   **Explicación:** Muestra el trayecto instantáneo local de la señal. Al estar en movimiento y tener múltiples rayos rebotando de diferentes edificios (interferencia de multitrayectoria constructiva o destructiva según nuestra posición exacta instantánea), observamos fluctuaciones de hasta $30\text{ dB}$ en nanosegundos formando picadas hondísimas (típicamente representadas por una distribución de Rayleigh inversa). 

### 2. Desvanecimiento de Gran Escala (Arriba Derecha)
*   **Eje:** Distancia de cobertura (m) contra Potencia (dB).
*   **Explicación:** Modela el comportamiento "Macro". Olvidamos el paso a paso sutil y vemos la atenuación a largo plazo debida únicamente a que cada vez que triplicamos la distancia desde la antena, el campo se disipa libremente hacia el vacío, restando una cantidad contundente de decibelios a la ecuación de Friss. Las variaciones sutiles tipo sierra obedecen al ensombrecimiento por grandes edificios o montañas modelado.

### 3. Respuesta Frecuencial en Banda Base (Abajo Izquierda)
*   **Eje:** Frecuencia (kHz) alrededor del centro cero contra Magnitud (dB).
*   **Explicación:** Corrobora la "selectividad en frecuencia". Demuestra que el medio físico de ecos no le hace daño equitativamente a toda la banda, sino que rechaza y atenaza enormemente "parches" del espectro, destrozando frecuencias exactas y dejando otras casi intactas. La amplitud de cada cancelación nos remite estrictamente a la cantidad y grosor (dispersión r.m.s) de cada perfil estático elegido, sirviendo para verificar el índice de Interferencia Intersimbólica (ISI) esperado.

### 4. Respuesta Frecuencial Paso Banda (Abajo Derecha)
*   **Eje:** Frecuencia general (GHz) contra Magnitud (dB).
*   **Explicación:** Un reflejo fiel del panel anterior, pero mapeando y dibujando en qué punto radial del espectro electromagnético gigante nos posicionamos. Se inyecta la franja del efecto base superpuesto rigurosamente alrededor de la frecuencia portadora generadora real $f_c$ (marcada con una útil línea delimitadora vertical roja), revelando la alteración impuesta a las subportadoras laterales de nuestra trama.

---

## 4. Requisitos e Instalación Local

Todo el proyecto fue estructurado bajo un entorno Python $3$. Para ejecutar el experimento con éxito por tu cuenta en una terminal computacional sin excepciones cruzadas, sigue estos dos breves comandos de preparativos estándares:

```bash
# Instalar los tres pilares computacionales requeridos: Numpy, Scipy y Matplotlib
pip install -r requirements.txt
```

```bash
# Lanzar el simulador y arrancar la visualización del Desktop
python main.py
```
