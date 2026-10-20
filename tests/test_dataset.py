"""
PRUEBAS DE LA GENERACIÓN DE DATASET (Semana 3, Día 1)
"""

import unittest

from model.game_model import Board
from model.ml_agent import (DatasetGenerator, encode_board,
                            index_to_move, move_to_index)


class TestCodificacion(unittest.TestCase):

    def test_codificacion_relativa(self):
        t = Board()
        t.make_move((0, 0), 'X')
        t.make_move((1, 1), 'O')
        # Desde X: mi ficha en la casilla 0 (=1), la del rival en la 4 (=-1)
        self.assertEqual(encode_board(t, 'X'), (1, 0, 0, 0, -1, 0, 0, 0, 0))

    def test_codificacion_cambia_con_el_jugador(self):
        t = Board()
        t.make_move((0, 0), 'X')
        t.make_move((1, 1), 'O')
        self.assertEqual(encode_board(t, 'O'), (-1, 0, 0, 0, 1, 0, 0, 0, 0))

    def test_indice_y_jugada_son_inversos(self):
        for i in range(9):
            self.assertEqual(move_to_index(index_to_move(i)), i)
        self.assertEqual(move_to_index((1, 2)), 5)


class TestSimulacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Se simula UNA vez y todas las pruebas reutilizan el resultado.
        cls.generador = DatasetGenerator(seed=7)
        cls.registros, cls.resumen = cls.generador.generate(300)

    def test_las_partidas_suman_el_total(self):
        r = self.resumen
        self.assertEqual(r["win"] + r["draw"] + r["loss"], 300)
        self.assertEqual(len({reg["game"] for reg in self.registros}), 300)

    def test_minimax_nunca_pierde(self):
        self.assertEqual(self.resumen["loss"], 0)

    def test_la_etiqueta_es_una_casilla_libre(self):
        for reg in self.registros:
            self.assertEqual(reg["cells"][reg["move"]], 0)

    def test_mismo_estado_misma_etiqueta(self):
        vistos = {}
        for reg in self.registros:
            esperado = vistos.setdefault(reg["cells"], reg["move"])
            self.assertEqual(reg["move"], esperado)

    def test_se_usan_los_dos_roles(self):
        roles = {reg["player"] for reg in self.registros}
        self.assertEqual(roles, {'X', 'O'})

    def test_la_semilla_hace_reproducible_el_resultado(self):
        a, _ = DatasetGenerator(seed=3).generate(20)
        b, _ = DatasetGenerator(seed=3).generate(20)
        self.assertEqual(a, b)

    def test_se_puede_fijar_el_rol(self):
        registros, _ = DatasetGenerator(seed=1).generate(20, roles=('O',))
        self.assertEqual({reg["player"] for reg in registros}, {'O'})


if __name__ == "__main__":
    unittest.main()