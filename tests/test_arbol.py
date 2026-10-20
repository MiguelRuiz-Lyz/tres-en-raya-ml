"""
PRUEBAS DEL ÁRBOL DE DECISIÓN (Semana 3, Día 3)
"""

import os
import tempfile
import unittest

from model.ml_agent import (accuracy, build_dataset, legal_prediction_rate,
                            save_tree_plot, split_dataset, train_tree,
                            tree_rules)


class TestArbol(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df, _, _ = build_dataset(300, seed=3)
        (cls.X_train, cls.X_test,
         cls.y_train, cls.y_test) = split_dataset(cls.df)
        cls.tree = train_tree(cls.X_train, cls.y_train)

    # ---------------- División ----------------
    def test_tamanos_de_la_division(self):
        self.assertEqual(len(self.X_train) + len(self.X_test), len(self.df))
        self.assertEqual(len(self.X_train), len(self.y_train))
        self.assertEqual(len(self.X_test), len(self.y_test))
        proporcion = len(self.X_test) / len(self.df)
        self.assertAlmostEqual(proporcion, 0.2, delta=0.02)

    def test_entrenamiento_y_prueba_no_comparten_posiciones(self):
        train = set(map(tuple, self.X_train.to_numpy()))
        test = set(map(tuple, self.X_test.to_numpy()))
        self.assertEqual(train & test, set())

    def test_la_division_es_reproducible(self):
        a = split_dataset(self.df, seed=5)
        b = split_dataset(self.df, seed=5)
        self.assertTrue(a[0].equals(b[0]))
        self.assertTrue(a[3].equals(b[3]))

    # ---------------- Entrenamiento ----------------
    def test_sin_limite_aprende_todo_el_entrenamiento(self):
        self.assertEqual(accuracy(self.tree, self.X_train, self.y_train), 1.0)

    def test_max_depth_limita_la_profundidad(self):
        corto = train_tree(self.X_train, self.y_train, max_depth=2)
        self.assertLessEqual(corto.get_depth(), 2)

    def test_misma_semilla_mismo_arbol(self):
        otro = train_tree(self.X_train, self.y_train)
        self.assertEqual(tree_rules(self.tree), tree_rules(otro))

    def test_la_precision_de_prueba_esta_entre_0_y_1(self):
        p = accuracy(self.tree, self.X_test, self.y_test)
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)

    def test_en_entrenamiento_todas_las_jugadas_son_legales(self):
        self.assertEqual(legal_prediction_rate(self.tree, self.X_train), 1.0)

    # ---------------- Reglas y gráfico ----------------
    def test_las_reglas_se_exportan_como_texto(self):
        texto = tree_rules(self.tree, max_depth=3)
        self.assertIn("|---", texto)
        self.assertIn("class:", texto)

    def test_el_grafico_se_guarda(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = save_tree_plot(self.tree,
                                  os.path.join(carpeta, "sub", "arbol.png"),
                                  max_depth=2)
            self.assertTrue(os.path.exists(ruta))
            self.assertGreater(os.path.getsize(ruta), 0)


if __name__ == "__main__":
    unittest.main()