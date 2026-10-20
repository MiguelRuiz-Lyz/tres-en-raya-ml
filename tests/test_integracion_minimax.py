"""
PRUEBAS DE INTEGRACIÓN CON MINIMAX REAL (Semana 2, Día 4)
Controlador + Modelo + agente Minimax funcionando juntos.
"""

import tkinter as tk
import unittest

from model.game_model import Board
from model.minimax_agent import MinimaxAgent
from view.gui_view import GameView
from controller.game_controller import GameController
from tests.test_integracion_hvh import VistaFalsa


def crear_juego_minimax():
    board = Board()
    view = VistaFalsa()
    controller = GameController(board, view)
    controller.register_agent("minimax", MinimaxAgent('O', 'X'))
    view.on_mode_change("minimax")
    return board, view, controller


class TestModoMinimax(unittest.TestCase):

    def test_la_ia_responde_tras_la_jugada_del_humano(self):
        board, view, _ = crear_juego_minimax()
        view.click(0, 0)                      # el humano abre en una esquina
        self.assertEqual(view.cells[(0, 0)], 'X')
        # Contra una esquina, la única respuesta que no pierde es el centro
        self.assertEqual(view.cells[(1, 1)], 'O')
        self.assertEqual(view.status, "Turno de X")

    def test_las_metricas_son_reales(self):
        _, view, _ = crear_juego_minimax()
        view.click(0, 0)
        nodos, ms = view.metrics
        self.assertGreater(nodos, 1000)       # exploró miles de nodos
        self.assertGreaterEqual(ms, 0)

    def test_se_repinta_antes_de_que_la_ia_piense(self):
        _, view, _ = crear_juego_minimax()
        view.click(0, 0)
        self.assertEqual(view.refresh_calls, 1)

    def test_el_humano_nunca_gana_contra_minimax(self):
        estrategias = {
            "siempre la primera libre": lambda libres: libres[0],
            "siempre la última libre": lambda libres: libres[-1],
            "siempre la del medio": lambda libres: libres[len(libres) // 2],
        }
        for nombre, elegir in estrategias.items():
            with self.subTest(estrategia=nombre):
                board, view, controller = crear_juego_minimax()
                while not controller.game_over:
                    view.click(*elegir(board.get_available_moves()))
                self.assertNotEqual(board.get_winner(), 'X')
                self.assertEqual(view.score[0], 0)    # X no suma victorias

    def test_el_modo_ml_sigue_sin_agente(self):
        _, view, _ = crear_juego_minimax()
        view.on_mode_change("ml")
        view.click(1, 1)
        self.assertEqual(view.cells, {})
        self.assertIn("aún no", view.status)


class TestMinimaxConVistaReal(unittest.TestCase):

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("No hay pantalla disponible para Tkinter")
        self.root.withdraw()
        self.board = Board()
        self.view = GameView(self.root)
        self.controller = GameController(self.board, self.view)
        self.controller.register_agent("minimax", MinimaxAgent('O', 'X'))

    def tearDown(self):
        self.root.destroy()

    def test_clic_real_y_respuesta_de_la_ia(self):
        self.view.mode_var.set("minimax")
        self.view._mode_changed()                        # como si eligieras el modo
        self.view.cells[0][0].invoke()                   # clic real del humano
        self.assertEqual(self.view.cells[0][0]["text"], "X")
        self.assertEqual(self.view.cells[1][1]["text"], "O")
        self.assertNotEqual(self.view.nodes_var.get(), "—")
        self.assertIn("ms", self.view.time_var.get())


if __name__ == "__main__":
    unittest.main()