import flet as ft
import sounddevice as sd
import asyncio
from src.model.audio_processing import detect_frequency
from src.model.tuning import find_closest_tuning, evaluate_tuning
from src.model.firebase_service import get_tuning_data, update_tuning_data, delete_tuning_data

# Pila para almacenar las vistas
view_stack = []

def open_data_window(page, user_id="user123"):
    """Abre una ventana con las afinaciones guardadas y permite actualizar/eliminar."""

    view_stack.append(page.controls.copy())
    page.controls.clear()
    tuning_list_column = ft.Column()

    # Función para refrescar la lista de afinaciones
    def refresh_data():
 
        tuning_list_column.controls.clear()
        # Obtener los datos actualizados de Firestore
        tuning_data = get_tuning_data(user_id)

        if not tuning_data:
            tuning_list_column.controls.append(ft.Text("No hay afinaciones guardadas."))
        else:
            for tuning in tuning_data:
                doc_id = tuning["id"] 
                # Campos de texto para mostrar la nota y el estado de afinación
                note_text = ft.Text(f"Nota: {tuning['note']}")
                status_text = ft.Text(f"Estado: {tuning['tuning_status']}")

                # Botón para actualizar
                update_button = ft.ElevatedButton(
                        "Actualizar",
                    on_click=lambda e, id=doc_id: page.run_task(update_note, page, id)  # Pasar 'page' primero
                    )

                # Botón para eliminar
                delete_button = ft.ElevatedButton(
                    "Eliminar",
                    on_click=lambda e, id=doc_id: (
                        delete_tuning_data(id),
                        refresh_data()  # Refrescar la lista después de eliminar
                    )
                )

                # Agregar elementos a la lista
                tuning_list_column.controls.append(
                    ft.Row([note_text, status_text, update_button, delete_button])
                )

        # Actualizar la página para reflejar los cambios
        page.update()

    # Botón para volver a la vista anterior
    back_button = ft.ElevatedButton(
        "Volver",
        on_click=lambda e: go_back(page)  
    )

    # Agregar el botón "Volver" y la lista de afinaciones a la página
    page.add(ft.Column([back_button, tuning_list_column]))

    # Llamar a refresh_data para cargar los datos iniciales
    refresh_data()

def go_back(page):

    if view_stack:  # Si hay vistas en la pila
        previous_view = view_stack.pop()  # Obtener la vista anterior
        page.controls.clear()  # Limpiar la página actual
        page.controls.extend(previous_view)  # Restaurar la vista anterior
        page.update()  # Actualizar la página

async def update_note(page, doc_id):

    # Iniciamos la captura de audio
    detected_freq = None
    listening_active = True

    def callback(indata, frames, time, status):
        nonlocal detected_freq
        detected_freq = detect_frequency(indata)

    # Configuración audio stream
    audio_stream = sd.InputStream(
        channels=1, callback=callback, blocksize=1024, samplerate=22050
    )
    audio_stream.start()

    # Indicador de que se está mostrando audioo
    page.snack_bar = ft.SnackBar(ft.Text("Capturando audio..."))
    page.snack_bar.open = True
    page.update()

    frequency_samples = []
    while listening_active:
     if detected_freq is not None:
    
        closest_note, _ = find_closest_tuning(detected_freq)
        tuning_status = evaluate_tuning(detected_freq, closest_note)

        # Actualizar en Firestore
        update_tuning_data(doc_id, {"note": closest_note, "tuning_status": tuning_status})

        # Detener captura
        audio_stream.stop()
        listening_active = False

        # Mostrar mensaje de éxito
        page.snack_bar = ft.SnackBar(ft.Text("Nota actualizada correctamente."))
        page.snack_bar.open = True
        page.update()

    await asyncio.sleep(0.1)  # Breve pausa antes de la siguiente iteración
