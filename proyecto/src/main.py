import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import flet as ft
from src.controller.instrument_controller import run_controller

ft.app(target=run_controller)