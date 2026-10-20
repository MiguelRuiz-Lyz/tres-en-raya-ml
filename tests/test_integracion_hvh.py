"""
PRUEBAS DE INTEGRACIÓN -  Humano vs Humano.

Comprueban que Modelo + Controlador (+ Vista) funcionan juntos.
Primero con una VISTA FALSA (sin ventana) y luego con la vista real.
"""

import tkinter as tk
import unittest

from model.game_model import Board
from view.gui_view import GameView
from controller.game_controller import GameController


class VistaFalsa:
    """Imita a GameView, pero en vez de dibujar, solo anota lo que le piden."""

    def __init__(self):
        self.on_cell_click = None
        self.on_mode_change = None
        self.on_reset = None
        self.cells = {}               # (fila, col) -> 'X' / 'O'
        self.status = ""
        self.score = (0, 0, 0)
        self.metrics = None
        self.board_enabled = True
        self.refresh_calls = 0
        self.summary = None

    # --- Los mismos métodos públicos que tiene la vista real ---
    def get_mode(self):
        return "hvh"

    def set_cell(self, row, col, symbol):
        self.cells[(row, col)] = symbol

    def clear_board(self):
        self.cells = {}
        self.board_enabled = True

    def set_board_enabled(self, enabled):
        self.board_enabled = enabled

    def set_status(self, text):
        self.status = text

    def set_score(self, x_wins, o_wins, draws):
        self.score = (x_wins, o_wins, draws)

    def set_metrics(self, nodes, time_ms):
        self.metrics = (nodes, time_ms)

    def clear_metrics(self):
        self.metrics = None

    def set_metrics_summary(self, moves, avg_nodes, avg_ms, max_ms):
        self.summary = (moves, avg_nodes, avg_ms, max_ms)

    def clear_metrics_summary(self):
        self.summary = None

    def refresh(self):
        self.refresh_calls += 1

    # --- Simula el clic de un usuario ---
    def click(self, row, col):
        self.on_cell_click(row, col)


class TestHumanoVsHumano(unittest.TestCase):

    def setUp(self):
        # setUp se ejecuta antes de CADA prueba: todo empieza desde cero.
        self.board = Board()
        self.view = VistaFalsa()
        self.controller = GameController(self.board, self.view)

    def jugar(self, *casillas):
        """Hace clic en varias casillas seguidas: jugar((0,0), (1,1), ...)"""
        for fila, col in casillas:
            self.view.click(fila, col)

    # ---------------- Arranque y turnos ----------------
    def test_arranque(self):
        self.assertEqual(self.view.status, "Turno de X")
        self.assertEqual(self.view.cells, {})
        self.assertEqual(self.view.score, (0, 0, 0))
        self.assertEqual(len(self.board.get_available_moves()), 9)

    def test_turnos_alternan(self):
        self.jugar((0, 0), (1, 1))
        self.assertEqual(self.view.cells[(0, 0)], 'X')
        self.assertEqual(self.view.cells[(1, 1)], 'O')
        self.assertEqual(self.view.status, "Turno de X")

    def test_casilla_ocupada_no_cambia_el_turno(self):
        self.jugar((0, 0))
        self.assertEqual(self.view.status, "Turno de O")
        self.jugar((0, 0))                                  # casilla ocupada
        self.assertEqual(self.view.cells[(0, 0)], 'X')      # no se sobrescribió
        self.assertIn("ocupada", self.view.status)
        self.jugar((1, 1))                                  # sigue siendo turno de O
        self.assertEqual(self.view.cells[(1, 1)], 'O')

    def test_clic_fuera_de_rango_no_dibuja_nada(self):
        self.jugar((5, 5))
        self.assertEqual(self.view.cells, {})

    # ---------------- Victorias y empate ----------------
    def test_victoria_por_fila(self):
        self.jugar((0, 0), (1, 0), (0, 1), (1, 1), (0, 2))
        self.assertEqual(self.view.status, "¡Ganó X!")
        self.assertEqual(self.view.score, (1, 0, 0))
        self.assertFalse(self.view.board_enabled)
        self.assertEqual(self.board.get_winner(), 'X')

    def test_victoria_por_columna(self):
        self.jugar((0, 0), (0, 2), (0, 1), (1, 2), (1, 0), (2, 2))
        self.assertEqual(self.view.status, "¡Ganó O!")
        self.assertEqual(self.view.score, (0, 1, 0))

    def test_victoria_por_diagonal(self):
        self.jugar((0, 0), (0, 1), (1, 1), (0, 2), (2, 2))
        self.assertEqual(self.view.status, "¡Ganó X!")

    def test_empate(self):
        #  X O X
        #  X O O
        #  O X X
        self.jugar((0, 0), (0, 1), (0, 2), (1, 1), (1, 0),
                   (1, 2), (2, 1), (2, 0), (2, 2))
        self.assertEqual(self.view.status, "¡Empate!")
        self.assertEqual(self.view.score, (0, 0, 1))
        self.assertTrue(self.board.is_draw())

    def test_no_se_juega_despues_de_terminar(self):
        self.jugar((0, 0), (1, 0), (0, 1), (1, 1), (0, 2))   # gana X
        self.jugar((2, 2))                                   # intento extra
        self.assertNotIn((2, 2), self.view.cells)
        self.assertEqual(self.view.score, (1, 0, 0))

    # ---------------- Reinicio y modos ----------------
    def test_nueva_partida_conserva_marcador(self):
        self.jugar((0, 0), (1, 0), (0, 1), (1, 1), (0, 2))   # gana X
        self.view.on_reset()
        self.assertEqual(self.view.cells, {})
        self.assertTrue(self.view.board_enabled)
        self.assertEqual(self.view.score, (1, 0, 0))
        self.assertEqual(self.view.status, "Turno de X")
        self.assertEqual(len(self.board.get_available_moves()), 9)

    def test_elegir_el_mismo_modo_no_reinicia_marcador(self):
        self.jugar((0, 0), (1, 0), (0, 1), (1, 1), (0, 2))   # gana X
        self.view.on_mode_change("hvh")                      # mismo modo
        self.assertEqual(self.view.score, (1, 0, 0))

    def test_cambiar_de_modo_reinicia_marcador(self):
        self.jugar((0, 0), (1, 0), (0, 1), (1, 1), (0, 2))   # gana X
        self.view.on_mode_change("minimax")
        self.assertEqual(self.view.score, (0, 0, 0))
        self.assertIn("aún no disponible", self.view.status)

    def test_modo_ia_sin_agente_no_deja_jugar(self):
        self.view.on_mode_change("minimax")
        self.jugar((1, 1))
        self.assertEqual(self.view.cells, {})
        self.assertIn("aún no", self.view.status)

    # ---------------- Sincronía modelo <-> vista ----------------
    def test_modelo_y_vista_siempre_sincronizados(self):
        self.jugar((0, 0), (1, 1), (2, 2), (0, 2), (0, 0), (1, 0))
        for fila in range(3):
            for col in range(3):
                en_modelo = self.board.get_cell(fila, col)
                en_vista = self.view.cells.get((fila, col), Board.EMPTY)
                self.assertEqual(en_modelo, en_vista, f"Desincronizado en ({fila}, {col})")


class AgentePrimeraLibre:
    """Agente falso: juega en la primera casilla libre."""
    nodes_evaluated = 42

    def get_move(self, board):
        return board.get_available_moves()[0]


class AgenteTramposo:
    """Agente falso defectuoso: siempre propone la casilla (0, 0)."""
    nodes_evaluated = 1

    def get_move(self, board):
        return (0, 0)


class TestIntegracionConIA(unittest.TestCase):
    """Verifica que el controlador está listo para recibir agentes de IA."""

    def setUp(self):
        self.board = Board()
        self.view = VistaFalsa()
        self.controller = GameController(self.board, self.view)

    def test_ia_responde_con_agente_falso(self):
        self.controller.register_agent("minimax", AgentePrimeraLibre())
        self.view.on_mode_change("minimax")
        self.view.click(1, 1)
        self.assertEqual(self.view.cells[(1, 1)], 'X')
        self.assertEqual(self.view.cells[(0, 0)], 'O')
        self.assertEqual(self.view.metrics[0], 42)
        self.assertEqual(self.view.status, "Turno de X")

    def test_ia_con_jugada_invalida_no_desincroniza_modelo_y_vista(self):
        self.controller.register_agent("minimax", AgenteTramposo())
        self.view.on_mode_change("minimax")
        self.view.click(0, 0)   # X juega (0,0); la IA responde (0,0): ilegal
        self.assertEqual(self.view.cells[(0, 0)], 'X')   # no se sobrescribe
        self.assertIn("inválida", self.view.status)
        self.assertFalse(self.view.board_enabled)


class TestConVistaReal(unittest.TestCase):
    """Igual que arriba, pero con la ventana real de Tkinter."""

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("No hay pantalla disponible para Tkinter")
        self.root.withdraw()   # oculta la ventana durante la prueba
        self.board = Board()
        self.view = GameView(self.root)
        self.controller = GameController(self.board, self.view)

    def tearDown(self):
        self.root.destroy()

    def tocar(self, fila, col):
        """Simula un clic real sobre el botón de esa casilla."""
        self.view.cells[fila][col].invoke()

    def test_partida_completa_con_vista_real(self):
        for fila, col in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            self.tocar(fila, col)
        self.assertEqual(self.view.cells[0][0]["text"], "X")
        self.assertEqual(self.view.cells[1][0]["text"], "O")
        self.assertEqual(self.view.status_var.get(), "¡Ganó X!")
        self.assertIn("X: 1", self.view.score_var.get())
        # El tablero quedó bloqueado: un botón deshabilitado ignora el clic
        self.assertEqual(str(self.view.cells[2][2]["state"]), "disabled")
        self.tocar(2, 2)
        self.assertEqual(self.view.cells[2][2]["text"], "")

    def test_casilla_ocupada_con_vista_real(self):
        self.tocar(0, 0)
        self.tocar(0, 0)
        self.assertEqual(self.view.cells[0][0]["text"], "X")
        self.assertIn("ocupada", self.view.status_var.get())


if __name__ == "__main__":
    unittest.main()