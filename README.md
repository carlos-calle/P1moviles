# Simulador de Canal Inalámbrico

Este proyecto es un simulador computacional de canales de comunicaciones inalámbricas desarrollado en Python. Proporciona una interfaz gráfica de usuario (GUI) interactiva que permite a los usuarios modelar y visualizar los efectos del desvanecimiento (fading) a gran y pequeña escala en señales de radiofrecuencia, implementando los modelos de canal **Rayleigh** y **Rician**, y soportando perfiles de retardo estandarizados por la recomendación **ITU-R M.1225**.

## Características Principales

*   **Modelos de Fading de Pequeña Escala:**
    *   **Canal Rayleigh:** Simula escenarios sin línea de vista directa (NLoS), utilizando el clásico modelo de Jakes para generar el espectro Doppler.
    *   **Canal Rician:** Simula escenarios con línea de vista directa (LoS) combinada con componentes difusos, ajustable mediante el factor $K$ (en dB).
*   **Modelos de Fading de Gran Escala:**
    *   Implementa el modelo de propagación Log-Distancia combinado con *Shadowing* (sombreado) Log-Normal.
*   **Perfiles Estándar ITU-R:** Incorpora los modelos de canal definidos en la recomendación ITU-R M.1225 (Pedestrian A/B y Vehicular A/B).
*   **Visualización en Múltiples Dominios:**
    *   **Dominio del Tiempo:** Muestra la envolvente de la señal afectada por el desvanecimiento (fading).
    *   **Dominio de la Frecuencia:** Visualiza el Perfil de Retardo de Potencia (PDP) y la respuesta en frecuencia del canal en banda de paso.
    *   **Dominio Espacial:** Gráfica de la pérdida de potencia a gran escala en función de la distancia.
    *   **Componentes y Coherencia:** Presenta las trayectorias individuales, la suma coherente, la autocorrelación temporal y la correlación frecuencial.

## Estructura del Proyecto

El código está modularizado para separar la lógica de interfaz de usuario de los modelos matemáticos y físicos:

*   `main.py`: Punto de entrada de la aplicación. Inicializa la interfaz gráfica de Tkinter.
*   `gui.py`: Contiene la clase `ChannelSimulatorApp`, la cual define toda la interfaz gráfica, maneja la entrada del usuario, y orquesta el dibujado de las gráficas utilizando `matplotlib`.
*   `simulator.py`: Actúa como puente entre la GUI y los modelos matemáticos. Recibe los parámetros, instancia el modelo de canal correspondiente y ejecuta los cálculos para retornar los arreglos de datos listos para ser graficados.
*   `rayleighchannel.py`: Define la clase `RayleighChannel`. Implementa la generación de coeficientes Rayleigh por trayectoria usando suma de sinusoides de Jakes, normalización del PDP, pérdida log-distancia y respuesta en frecuencia.
*   `ricianchannel.py`: Define la clase `RicianChannel`. Mantiene la misma estructura del canal Rayleigh, pero incorpora una componente especular LoS en la primera trayectoria mediante el factor $K$.
*   `itu_profiles.py`: Contiene perfiles predefinidos de retardos en microsegundos y ganancias en dB correspondientes a la recomendación ITU-R M.1225.
*   `requirements.txt`: Lista de dependencias de librerías de Python.

## Modelos Matemáticos Implementados

### 1. Fading de Pequeña Escala (Modelo de Jakes)
El simulador genera el desvanecimiento utilizando el **Modelo Clásico de Jakes**, el cual aproxima un espectro Doppler asumiendo que los rayos llegan al receptor uniformemente distribuidos desde todos los ángulos. 
La frecuencia Doppler máxima se calcula como:
$$f_D = \frac{v}{c} \cdot f_c$$
donde $v$ es la velocidad del móvil, $c$ la velocidad de la luz y $f_c$ la frecuencia portadora.

La simulación temporal usa una aproximación de banda angosta: cada trayectoria se modela como un coeficiente complejo variable en el tiempo, y la señal total se obtiene como suma coherente de esas mismas trayectorias. La selectividad frecuencial se calcula de forma analítica mediante:
$$H(f)=\sum_i h_i e^{-j2\pi f\tau_i}$$

Para el **Canal Rician**, la componente LoS se combina con la componente dispersiva según el Factor $K$:
$$K = \frac{\text{Potencia Componente LoS}}{\text{Potencia Componente Difusa}}$$

### 2. Fading de Gran Escala
La potencia recibida en función de la distancia $d$ se calcula usando el modelo Log-Distance más Shadowing:
$$PL(d)[dB] = PL(d_0) + 10 \cdot n \cdot \log_{10}\left(\frac{d}{d_0}\right) + X_\sigma$$
Donde $n$ es el exponente de pérdidas (ej. 3.5 para entornos urbanos), $PL(d_0)$ es la pérdida de referencia, y $X_\sigma$ es una variable aleatoria normal con media cero y desviación estándar $\sigma$ (representando el sombreado).

## Requisitos e Instalación

Para ejecutar este simulador, asegúrate de tener instalado Python 3.x.

1. Clona o descarga el repositorio del proyecto.
2. Es recomendable crear un entorno virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
   Las dependencias principales son `numpy`, `scipy` y `matplotlib`.

## Uso

Para ejecutar el simulador, simplemente lanza el archivo principal desde la terminal:

```bash
python3 main.py
```

En la ventana de la aplicación podrás:
1. **Seleccionar el Perfil:** Puedes elegir un perfil estándar de la ITU o configurar retardos y ganancias manualmente.
2. **Elegir el Modelo:** Alternar entre Rayleigh (para entornos sin vista directa) o Rician (y especificar su factor $K$).
3. **Modificar Parámetros Físicos:** Ajustar la frecuencia portadora ($f_c$), la velocidad del receptor móvil ($v$), los retardos en microsegundos, las ganancias en dB, el exponente de pérdidas ($n$) y la desviación estándar de sombreado ($\sigma$).
4. **Simular:** Al presionar "Simular Canal", la herramienta calculará las variables y actualizará las seis pestañas de gráficos para mostrar el comportamiento temporal, frecuencial, espacial y de coherencia.
