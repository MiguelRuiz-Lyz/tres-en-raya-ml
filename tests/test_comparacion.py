"""
PRUEBAS DE LA COMPARACIÓN MINIMAX vs ÁRBOL (Semana 3, Día 5)
"""

import unittest

from model.game_model import Board
from model.ml_agent import (FEATURE_COLUMNS, TARGET_COLUMN, build_dataset,
                            train_tree)
from model.comparison import (board_from_key, by_pieces, compare_agents,
                              count_pieces, dataset_cells, enumerate_positions,
                              grid_key, play_game, run_matches, summarize)

_CACHE = {}


def datos():
    """Dataset, árbol y posiciones: se calculan una sola vez."""
    if not _CACHE:
        df, _, _ = build_dataset(300, seed=3)
        _CACHE["df"] = df
        _CACHE["tree"] = train_tree(df[FEATURE_COLUMNS], df[TARGET_COLUMN])
        _CACHE["pos"] = enumerate_positions()
    return _CACHE["df"], _CACHE["tree"], _CACHE["pos"]


class TestPosiciones(unittest.TestCase):

    def test_hay_4520_posiciones_no_terminales(self):
        _, _, pos = datos()
        self.assertEqual(len(pos), 4520)

    def test_el_turno_coincide_con_las_fichas(self):
        _, _, pos = datos()
        for clave, mover in pos.items():
            x = sum(f.count('X') for f in clave)
            o = sum(f.count('O') for f in clave)
            self.assertIn(x - o, (0, 1))               # X abre
            self.assertEqual(mover, 'X' if x == o else 'O')

    def test_board_from_key_reconstruye_el_tablero(self):
        _, _, pos = datos()
        for clave in list(pos)[:200]:
            self.assertEqual(grid_key(board_from_key(clave)), clave)


class TestComparacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        df, tree, pos = datos()
        cls.pos = pos
        # Solo posiciones con 5+ fichas: así la prueba es rápida
        cls.tabla = compare_agents(tree, pos, dataset_cells(df),
                                   min_pieces=5, reps=2)

    def test_una_fila_por_posicion(self):
        esperadas = sum(1 for k in self.pos if count_pieces(k) >= 5)
        self.assertEqual(len(self.tabla), esperadas)

    def test_las_posiciones_vistas_se_reproducen_exactamente(self):
        vistas = self.tabla[self.tabla["seen"]]
        self.assertGreater(len(vistas), 0)
        self.assertTrue(vistas["match"].all())

    def test_coincidir_implica_preservar_el_resultado(self):
        t = self.tabla
        self.assertTrue((t["optimal"] | ~t["match"]).all())

    def test_las_metricas_son_validas(self):
        t = self.tabla
        self.assertTrue((t["mm_ms"] > 0).all())
        self.assertTrue((t["ml_ms"] > 0).all())
        self.assertTrue((t["mm_nodes"] >= 1).all())

    def test_el_resumen(self):
        r = summarize(self.tabla)
        self.assertEqual(r["positions"], len(self.tabla))
        self.assertEqual(r["seen"] + r["unseen"], r["positions"])
        for clave in ("match_all", "optimal_all", "fallback_rate"):
            self.assertGreaterEqual(r[clave], 0.0)
            self.assertLessEqual(r[clave], 1.0)
        self.assertGreaterEqual(r["optimal_all"], r["match_all"])

    def test_tabla_por_fichas(self):
        g = by_pieces(self.tabla)
        self.assertEqual(set(g["pieces"]), {5, 6, 7, 8})
        self.assertEqual(g["positions"].sum(), len(self.tabla))


class TestPartidas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _, tree, _ = datos()
        cls.n = 20
        cls.res = run_matches(tree, n_games=cls.n, seed=1)

    def test_minimax_nunca_pierde_contra_el_azar(self):
        self.assertEqual(self.res["Minimax vs azar"]["loss"], 0)

    def test_ml_no_le_gana_a_minimax(self):
        r = self.res["ML vs Minimax"]
        self.assertEqual(r["win"], 0)
        self.assertEqual(sum(r.values()), 2)

    def test_las_partidas_suman_el_total(self):
        for nombre in ("ML vs azar", "Minimax vs azar"):
            self.assertEqual(sum(self.res[nombre].values()), self.n)

    def test_jugada_ilegal_lanza_error(self):
        with self.assertRaises(ValueError):
            play_game(lambda b: (0, 0), lambda b: (0, 0))


if __name__ == "__main__":
    unittest.main()