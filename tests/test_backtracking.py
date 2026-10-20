"""
PRUEBAS DEL BACKTRACKING - undo_move debe restaurar el estado previo.
"""

import unittest

from model.game_model import Board


def foto(board):
    """Copia del contenido del tablero, para comparar 'antes' y 'después'."""
    return [fila[:] for fila in board.grid]


class TestBacktracking(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_undo_deja_la_casilla_vacia(self):
        self.board.make_move((1, 1), 'X')
        self.assertTrue(self.board.undo_move((1, 1)))
        self.assertEqual(self.board.get_cell(1, 1), Board.EMPTY)

    def test_hacer_y_deshacer_restaura_el_tablero(self):
        self.board.make_move((0, 0), 'X')
        self.board.make_move((1, 1), 'O')
        antes = foto(self.board)
        self.board.make_move((2, 2), 'X')
        self.board.undo_move((2, 2))
        self.assertEqual(foto(self.board), antes)

    def test_undo_devuelve_la_jugada_a_las_disponibles(self):
        self.board.make_move((0, 2), 'X')
        self.assertEqual(len(self.board.get_available_moves()), 8)
        self.board.undo_move((0, 2))
        self.assertEqual(len(self.board.get_available_moves()), 9)
        self.assertIn((0, 2), self.board.get_available_moves())

    def test_undo_en_casilla_vacia_devuelve_false(self):
        self.assertFalse(self.board.undo_move((0, 0)))

    def test_undo_fuera_de_rango_devuelve_false(self):
        self.assertFalse(self.board.undo_move((3, 3)))
        self.assertFalse(self.board.undo_move((-1, 0)))

    def test_undo_anula_una_victoria(self):
        for casilla in [(0, 0), (0, 1), (0, 2)]:
            self.board.make_move(casilla, 'X')
        self.assertTrue(self.board.check_winner('X'))
        self.board.undo_move((0, 2))
        self.assertFalse(self.board.check_winner('X'))
        self.assertIsNone(self.board.get_winner())

    def test_deshacer_en_orden_inverso_vuelve_al_inicio(self):
        jugadas = [((0, 0), 'X'), ((1, 1), 'O'), ((2, 2), 'X'), ((0, 2), 'O')]
        for mov, jug in jugadas:
            self.board.make_move(mov, jug)
        for mov, _ in reversed(jugadas):
            self.board.undo_move(mov)
        self.assertEqual(foto(self.board), foto(Board()))


if __name__ == "__main__":
    unittest.main()