
import flet as ft
from src.view.data_display import open_data_window  

def build_ui(page, closest_note_text, tuning_status_text):

    open_data_button = ft.ElevatedButton("Ver Afinaciones Guardadas", on_click=lambda e: open_data_window(page))

    page.add(
        ft.Column(
            [
                ft.Text("Afinador de Guitarra", size=32),
                closest_note_text,
                tuning_status_text,
                open_data_button, 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
