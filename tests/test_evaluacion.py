"""
PRUEBAS DE LA FUNCIÓN DE EVALUACIÓN (Semana 2, Día 2)
"""

import unittest

from model.game_model import Board
from model.minimax_agent import MinimaxAgent

# Las 8 líneas ganadoras, como posiciones 0-8 (fila * 3 + columna)
LINEAS = [(0, 1, 2), (3, 4, 5), (6, 7, 8),     # filas
          (0, 3, 6), (1, 4, 7), (2, 5, 8),     # columnas
          (0, 4, 8), (2, 4, 6)]                # diagonales


def tablero_desde(texto):
    """Crea un tablero a partir de 9 caracteres: 'XXXOO    ' (un espacio = vacío)."""
    t = Board()
    for i, ficha in enumerate(texto):
        if ficha != ' ':
            t.make_move((i // 3, i % 3), ficha)
    return t


class TestEvaluacion(unittest.TestCase):

    def setUp(self):
        self.agente = MinimaxAgent(ai_player='O', human_player='X')

    def test_valores_por_defecto(self):
        a = MinimaxAgent()
        self.assertEqual((a.ai_player, a.human_player), ('O', 'X'))
        self.assertEqual(a.nodes_evaluated, 0)

    def test_ia_gana_vale_mas_10(self):
        self.assertEqual(self.agente.evaluate(tablero_desde("OOOXX X  ")), 10)

    def test_humano_gana_vale_menos_10(self):
        self.assertEqual(self.agente.evaluate(tablero_desde("XXXOO    ")), -10)

    def test_empate_vale_0(self):
        self.assertEqual(self.agente.evaluate(tablero_desde("XOXXOOOXX")), 0)

    def test_tablero_vacio_vale_0(self):
        self.assertEqual(self.agente.evaluate(Board()), 0)

    def test_partida_en_curso_vale_0(self):
        self.assertEqual(self.agente.evaluate(tablero_desde("X   O    ")), 0)

    def test_victoria_de_la_ia_en_las_8_lineas(self):
        for linea in LINEAS:
            with self.subTest(linea=linea):
                t = Board()
                for i in linea:
                    t.make_move((i // 3, i % 3), 'O')
                self.assertEqual(self.agente.evaluate(t), 10)

    def test_victoria_del_humano_en_las_8_lineas(self):
        for linea in LINEAS:
            with self.subTest(linea=linea):
                t = Board()
                for i in linea:
                    t.make_move((i // 3, i % 3), 'X')
                self.assertEqual(self.agente.evaluate(t), -10)

    def test_roles_invertidos_invierten_el_signo(self):
        tablero = tablero_desde("XXXOO    ")          # ganó X
        ia_es_o = MinimaxAgent(ai_player='O', human_player='X')
        ia_es_x = MinimaxAgent(ai_player='X', human_player='O')
        self.assertEqual(ia_es_o.evaluate(tablero), -10)
        self.assertEqual(ia_es_x.evaluate(tablero), 10)

    def test_evaluar_no_modifica_el_tablero(self):
        tablero = tablero_desde("XOXXO    ")
        antes = [fila[:] for fila in tablero.grid]
        self.agente.evaluate(tablero)
        self.assertEqual(tablero.grid, antes)

    def test_roles_iguales_lanzan_error(self):
        with self.assertRaises(ValueError):
            MinimaxAgent(ai_player='X', human_player='X')


if __name__ == "__main__":
    unittest.main()