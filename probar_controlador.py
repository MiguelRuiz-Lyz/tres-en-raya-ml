"""
Quiero comprobar si el flujo de la ia funciona, antes de conectar la ia,
ahurita solo marcará  la primera casilla que encuentre bacía 
"""

import tkinter as tk

from model.game_model import Board
from view.gui_view import GameView
from controller.game_controller import GameController


class AgenteDePrueba:
    """Agente falso: siempre juega en la primera casilla libre."""

    def __init__(self):
        self.nodes_evaluated = 42

    def get_move(self, board):
        return board.get_available_moves()[0]


root = tk.Tk()
board = Board()
view = GameView(root)
controller = GameController(board, view)

# Registramos el agente falso en el modo Minimax
controller.register_agent("minimax", AgenteDePrueba())

view.run()