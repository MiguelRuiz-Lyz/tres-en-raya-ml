"""
Punto de entrada del programa.
Aquí se crearán el Modelo, la Vista y el Controlador y se arrancará el juego.
"""

import tkinter as tk

from model.game_model import Board
from view.gui_view import GameView
from controller.game_controller import GameController


def main():
    root = tk.Tk()

    board = Board()                              # Modelo
    view = GameView(root)                        # Vista
    controller = GameController(board, view)     # Controlador (une los dos)

    view.run()


if __name__ == "__main__":
    main()