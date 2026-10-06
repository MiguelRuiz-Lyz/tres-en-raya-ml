import tkinter as tk
from view.gui_view import GameView

root = tk.Tk()
vista = GameView(root)

turno = ['X']

def al_hacer_clic(fila, col):
    # Esto es SOLO una simulación para ver la vista funcionando.
    vista.set_cell(fila, col, turno[0])
    vista.set_status(f"Clic en la casilla ({fila}, {col})")
    vista.set_metrics(549946, 123.45)
    turno[0] = 'O' if turno[0] == 'X' else 'X'

def al_cambiar_modo(modo):
    vista.set_status(f"Modo elegido: {modo}")

def al_reiniciar():
    vista.clear_board()
    vista.clear_metrics()
    vista.set_status("Tablero reiniciado")
    turno[0] = 'X'

vista.on_cell_click = al_hacer_clic
vista.on_mode_change = al_cambiar_modo
vista.on_reset = al_reiniciar

vista.run()