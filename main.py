"""
Punto de entrada del programa.
Crea el Modelo, la Vista y el Controlador, registra los agentes de IA
y arranca el juego.
"""

import tkinter as tk

from model.game_model import Board
from model.minimax_agent import MinimaxAgent
from view.gui_view import GameView
from controller.game_controller import GameController


def main():
    root = tk.Tk()

    board = Board()                              # Modelo
    view = GameView(root)                        # Vista
    controller = GameController(board, view)     # Controlador (une los dos)

    # La IA juega con O y el humano con X (igual que el controlador)
    controller.register_agent("minimax", MinimaxAgent(ai_player='O', human_player='X'))
    # Semana 3: aquí se registrará el agente "ml"

    view.run()


if __name__ == "__main__":
    main()