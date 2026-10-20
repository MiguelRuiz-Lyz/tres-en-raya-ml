"""
PRUEBAS DE MÉTRICAS (Semana 2, Día 5)
"""

import tkinter as tk
import unittest

from model.game_model import Board
from model.minimax_agent import MinimaxAgent
from view.gui_view import GameView
from controller.game_controller import GameController
from controller.metrics import MetricsTracker
from tests.test_integracion_hvh import VistaFalsa


class TestMetricsTracker(unittest.TestCase):

    def test_inicia_en_cero(self):
        m = MetricsTracker()
        self.assertEqual(m.moves, 0)
        self.assertEqual(m.avg_nodes, 0)
        self.assertEqual(m.avg_ms, 0)
        self.assertEqual(m.max_ms, 0)

    def test_record_acumula(self):
        m = MetricsTracker()
        m.record(100, 2.0)
        m.record(300, 4.0)
        self.assertEqual(m.moves, 2)
        self.assertEqual(m.total_nodes, 400)
        self.assertAlmostEqual(m.total_ms, 6.0)

    def test_promedios(self):
        m = MetricsTracker()
        m.record(100, 2.0)
        m.record(300, 4.0)
        self.assertAlmostEqual(m.avg_nodes, 200)
        self.assertAlmostEqual(m.avg_ms, 3.0)

    def test_guarda_el_maximo(self):
        m = MetricsTracker()
        m.record(10, 4.0)
        m.record(10, 1.0)
        self.assertAlmostEqual(m.max_ms, 4.0)

    def test_reset_borra_todo(self):
        m = MetricsTracker()
        m.record(100, 2.0)
        m.reset()
        self.assertEqual((m.moves, m.total_nodes, m.total_ms, m.max_ms),
                         (0, 0, 0.0, 0.0))


def crear_juego(modo):
    board = Board()
    view = VistaFalsa()
    controller = GameController(board, view)
    controller.register_agent("minimax", MinimaxAgent('O', 'X'))
    view.on_mode_change(modo)
    return board, view, controller


class TestMetricasEnControlador(unittest.TestCase):

    def test_resumen_tras_una_jugada_de_la_ia(self):
        _, view, _ = crear_juego("minimax")
        view.click(0, 0)
        moves, avg_nodes, avg_ms, max_ms = view.summary
        self.assertEqual(moves, 1)
        self.assertGreater(avg_nodes, 1000)
        self.assertGreaterEqual(max_ms, 0)

    def test_el_resumen_acumula_jugadas(self):
        board, view, _ = crear_juego("minimax")
        view.click(0, 0)                                  # la IA responde en el centro
        view.click(*board.get_available_moves()[0])       # la IA debe bloquear
        self.assertEqual(view.summary[0], 2)

    def test_nueva_partida_conserva_el_resumen(self):
        _, view, _ = crear_juego("minimax")
        view.click(0, 0)
        view.on_reset()
        self.assertEqual(view.summary[0], 1)   # el resumen sigue
        self.assertIsNone(view.metrics)        # la última jugada se limpió

    def test_cambiar_de_modo_borra_el_resumen(self):
        _, view, controller = crear_juego("minimax")
        view.click(0, 0)
        view.on_mode_change("hvh")
        self.assertIsNone(view.summary)
        self.assertEqual(controller.metrics.moves, 0)

    def test_humano_vs_humano_no_registra_metricas(self):
        board = Board()
        view = VistaFalsa()
        controller = GameController(board, view)
        view.click(0, 0)
        view.click(1, 1)
        self.assertIsNone(view.summary)
        self.assertEqual(controller.metrics.moves, 0)


class TestMetricasVistaReal(unittest.TestCase):

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

    def test_el_panel_muestra_el_resumen(self):
        self.assertEqual(self.view.summary_var.get(), "—")
        self.view.mode_var.set("minimax")
        self.view._mode_changed()
        self.view.cells[0][0].invoke()
        texto = self.view.summary_var.get()
        self.assertIn("Jugadas de la IA: 1", texto)
        self.assertIn("nodos", texto)
        self.assertIn("ms", texto)


if __name__ == "__main__":
    unittest.main()