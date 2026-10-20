"""
PRUEBAS DE MINIMAX (Semana 2, Día 3)
Incluye la prueba central de la rúbrica: el agente es imbatible.
"""

import unittest

from model.game_model import Board
from model.minimax_agent import MinimaxAgent


def tablero_desde(texto):
    """Crea un tablero a partir de 9 caracteres (un espacio = casilla vacía)."""
    t = Board()
    for i, ficha in enumerate(texto):
        if ficha != ' ':
            t.make_move((i // 3, i % 3), ficha)
    return t


class TestMinimaxBasico(unittest.TestCase):

    def setUp(self):
        self.ia = MinimaxAgent('O', 'X')

    def test_toma_la_victoria_inmediata(self):
        #  O O .      O gana jugando en (0, 2)
        #  X X .
        #  X . .
        tablero = tablero_desde("OO XX X  ")
        self.assertEqual(self.ia.get_move(tablero), (0, 2))

    def test_ganar_pronto_vale_9(self):
        tablero = tablero_desde("OO XX X  ")
        valores = dict(self.ia.score_moves(tablero))
        self.assertEqual(valores[(0, 2)], 9)       # 10 - profundidad 1

    def test_bloquea_la_victoria_del_rival(self):
        #  X X .      X amenaza con (0, 2): la IA debe bloquear
        #  . O .
        #  . . .
        tablero = tablero_desde("XX  O    ")
        self.assertEqual(self.ia.get_move(tablero), (0, 2))

    def test_juega_como_x_si_se_le_pide(self):
        ia_x = MinimaxAgent('X', 'O')
        tablero = tablero_desde("XX  OO   ")
        self.assertEqual(ia_x.get_move(tablero), (0, 2))

    def test_get_move_no_modifica_el_tablero(self):
        tablero = tablero_desde("XX  O    ")
        antes = [fila[:] for fila in tablero.grid]
        self.ia.get_move(tablero)
        self.assertEqual(tablero.grid, antes)      # el backtracking restauró todo

    def test_el_contador_de_nodos_se_reinicia_en_cada_jugada(self):
        tablero = tablero_desde("XX  O    ")
        self.ia.get_move(tablero)
        primera = self.ia.nodes_evaluated
        self.assertGreater(primera, 0)
        self.ia.get_move(tablero)
        self.assertEqual(self.ia.nodes_evaluated, primera)

    def test_partida_terminada_devuelve_none(self):
        self.assertIsNone(self.ia.get_move(tablero_desde("XOXXOOOXX")))  # lleno
        self.assertIsNone(self.ia.get_move(tablero_desde("XXXOO    ")))  # ganó X
        self.assertEqual(self.ia.score_moves(tablero_desde("XXXOO    ")), [])


class TestMinimaxCompleto(unittest.TestCase):
    """Pruebas que recorren el árbol entero (tardan unos segundos)."""

    def test_desde_el_tablero_vacio(self):
        ia_x = MinimaxAgent('X', 'O')
        valores = ia_x.score_moves(Board())
        # Con juego perfecto, abrir en cualquier casilla lleva al empate.
        self.assertEqual({v for _, v in valores}, {0})
        # Todo el árbol, sin contar la raíz: 549,946 - 1
        self.assertEqual(ia_x.nodes_evaluated, 549945)
        self.assertEqual(ia_x.get_move(Board()), (0, 0))   # primera de las empatadas

    def revisar(self, board, turno, agente):
        """Recorre TODAS las respuestas posibles del humano. La IA nunca debe perder."""
        ganador = board.get_winner()
        if ganador is not None:
            self.assertNotEqual(ganador, agente.human_player,
                                f"¡La IA perdió!\n{board}")
            return
        if board.is_full():
            return

        if turno == agente.ai_player:
            jugada = agente.get_move(board)
            self.assertTrue(board.make_move(jugada, turno))
            self.revisar(board, agente.human_player, agente)
            board.undo_move(jugada)
        else:
            for jugada in board.get_available_moves():
                board.make_move(jugada, turno)
                self.revisar(board, agente.ai_player, agente)
                board.undo_move(jugada)

    def test_imbatible_jugando_como_O(self):
        self.revisar(Board(), 'X', MinimaxAgent('O', 'X'))

    def test_imbatible_jugando_como_X(self):
        self.revisar(Board(), 'X', MinimaxAgent('X', 'O'))


if __name__ == "__main__":
    unittest.main()