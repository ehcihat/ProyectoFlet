import numpy as np
import scipy.fftpack
from scipy.signal import butter, filtfilt

# Frecuencia de muestreo
SAMPLE_FREQ = 22050
# Tamaño de la ventana FFT  
WINDOW_SIZE = 4096  

window_samples = np.zeros(WINDOW_SIZE) 
detected_freqs = [] 
stabilization_window = 10  
 # Umbral de amplitud para filtrar señales débiles
min_amplitude = 2 

# Filtro para limitar frecuencias fuera del rango de guitarra
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_lowpass_filter(data, cutoff=350, fs=SAMPLE_FREQ):
    b, a = butter_lowpass(cutoff, fs)
    return filtfilt(b, a, data)

# Detección de frecuencia
def detect_frequency(indata):
    global window_samples, detected_freqs

    window_samples = np.concatenate((window_samples, indata[:, 0]))    
    window_samples = window_samples[len(indata[:, 0]):]

    filtered_samples = apply_lowpass_filter(window_samples)

    magnitude_spec = abs(scipy.fftpack.fft(filtered_samples)[:len(filtered_samples) // 2])

    # Encontrar la frecuencia con la mayor amplitud
    max_ind = np.argmax(magnitude_spec)
    max_freq = max_ind * (SAMPLE_FREQ / WINDOW_SIZE)

    # Obtener la amplitud máxima de la señal
    max_amplitude = np.max(magnitude_spec)

    print(f"Frecuencia detectada: {max_freq} Hz, Amplitud: {max_amplitude}")

    # Filtrar frecuencias 
    if max_freq < 80 or max_freq > 1000 or max_amplitude < min_amplitude:
        return None 

    # Almacenamos la frecuencia detectada
    detected_freqs.append(max_freq)

    # Si tenemos suficientes muestras, estabilizamos la frecuencia
    if len(detected_freqs) > stabilization_window:
        detected_freqs.pop(0)

    # Obtenemos el promedio de las frecuencias detectadas
    avg_freq = np.mean(detected_freqs)

    return avg_freq
