import flet as ft
import sounddevice as sd
import asyncio
import uuid
from src.model.audio_processing import detect_frequency
from src.model.tuning import find_closest_tuning, evaluate_tuning
from src.view.ui import build_ui
from src.model.firebase_service import save_tuning_data, get_tuning_data
from src.view.data_display import open_data_window 

def run_controller(page):

    closest_note_text = ft.Text("Esperando entrada...", size=24)
    tuning_status_text = ft.Text("Afinación: Desajustada", size=24)

    # Guardado de datos y botón para la acción
    def save_tuning(e):
  
        user_id = "user123" 
        tuning_data = {
            "note": closest_note_text.value,
            "tuning_status": tuning_status_text.value,
            "frequency": detected_freq, 
            "user_id": user_id,
        }   

    

        # Guardar los datos en Firebase
        save_tuning_data(user_id, tuning_data)

        closest_note_text.value = "Datos guardados."
        tuning_status_text.value = "Afinación guardada."
        page.update()

    save_button = ft.ElevatedButton("Guardar Afinación", on_click=save_tuning)


    audio_stream = None
    detected_freq = None 
    listening_active = False 

    def start_tuning(e):
        nonlocal listening_active
        closest_note_text.value = "Iniciando afinación..."
        tuning_status_text.value = "Afinación: En proceso..."
        page.update()

        # Iniciar la función para verificar el micrófono solo si no está activo
        if not listening_active:
            page.run_task(check_microphone)
            listening_active = True

    start_button = ft.ElevatedButton("Iniciar Afinación", on_click=start_tuning)

    # Función para detener la escucha
    def stop_listening(e):
        nonlocal audio_stream, listening_active
        if audio_stream:
            audio_stream.close()  
            audio_stream = None
            listening_active = False  
            closest_note_text.value = "Escucha detenida."
            tuning_status_text.value = "Afinación detenida."
            page.update()

    stop_button = ft.ElevatedButton("Detener Escucha", on_click=stop_listening)

    # Llamada a build_ui para crear la interfaz
    build_ui(page, closest_note_text, tuning_status_text)

    # Agregar los botones de iniciar, detener y guardar
    page.add(
        ft.Container(
            ft.Column(
                [
                    start_button,
                    stop_button, 
                    save_button 
                ],
                alignment=ft.MainAxisAlignment.CENTER,  
            ),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
        )
    )

    def callback(indata, frames, time, status):
        nonlocal detected_freq
        detected_freq = detect_frequency(indata)

        if detected_freq is None:
            closest_note_text.value = "Esperando entrada..."
            tuning_status_text.value = "Esperando entrada..."
        else:
            closest_cord, min_diff = find_closest_tuning(detected_freq)
            tuning_status = evaluate_tuning(detected_freq, closest_cord)

            closest_note_text.value = f"Cuerda: {closest_cord}"
            tuning_status_text.value = f"Afinación: {tuning_status}"

        page.update()

    async def check_microphone():
        """Verifica periódicamente si hay un micrófono disponible."""
        nonlocal audio_stream

        while listening_active: 
            devices = sd.query_devices()
            input_devices = [d for d in devices if d["max_input_channels"] > 0]

            if not input_devices:
                closest_note_text.value = "Error: No hay micrófono disponible."
                tuning_status_text.value = "Conéctalo y espera..."
                page.update()

                if audio_stream:
                    audio_stream.close() 
                    audio_stream = None
            else:
                if not audio_stream:
                    try:
                        audio_stream = sd.InputStream(
                            channels=1, callback=callback, blocksize=1024, samplerate=44100
                        )
                        audio_stream.start()
                        closest_note_text.value = "Micrófono detectado. Afinando..."
                        tuning_status_text.value = "Esperando entrada..."
                        page.update()
                    except sd.PortAudioError as e:
                        closest_note_text.value = "Error al acceder al micrófono."
                        tuning_status_text.value = f"Detalles: {str(e)}"
                        page.update()

            await asyncio.sleep(3)

def show_saved_data(page, user_id):
 
    tuning_data = get_tuning_data(user_id)
    
  
    if not tuning_data:
        page.add(ft.Text("No hay datos disponibles.", size=24))
    else:

        data_list = [ft.Text(f"Nota: {entry['note']} - Estado: {entry['tuning_status']} - Frecuencia: {entry['frequency']}", size=18) for entry in tuning_data]
        page.add(
            ft.Column(
                data_list,
                alignment=ft.MainAxisAlignment.START
            )
        )

    page.update()