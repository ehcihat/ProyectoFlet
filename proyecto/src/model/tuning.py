from config import GUITAR_TUNING
from src.model.audio_processing import SAMPLE_FREQ, butter_lowpass, filtfilt
def find_closest_tuning(detected_freq):
    closest_cord = None
    min_diff = float("inf")

    for cord, target_freq in GUITAR_TUNING.items():
        diff = abs(detected_freq - target_freq)
        if diff < min_diff:
            min_diff = diff
            closest_cord = cord

    return closest_cord, min_diff

def evaluate_tuning(detected_freq, closest_cord):
    tuning_threshold = 5  # Aumentar la tolerancia a 5 Hz
    target_freq = GUITAR_TUNING[closest_cord]
    
    if abs(detected_freq - target_freq) <= tuning_threshold:
        return "Afinada"
    elif detected_freq < target_freq:
        return "Demasiado bajo"
    else:
        return "Demasiado alto"

def apply_lowpass_filter(data, cutoff=500, fs=SAMPLE_FREQ):  # Aumento del corte a 500 Hz
    b, a = butter_lowpass(cutoff, fs)
    return filtfilt(b, a, data)