"""
PRUEBAS DEL AGENTE DE MACHINE LEARNING (Semana 3, Día 4)
"""

import os
import random
import tempfile
import tkinter as tk
import unittest

from model.game_model import Board
from model.ml_agent import (FEATURE_COLUMNS, TARGET_COLUMN, MLAgent,
                            build_dataset, index_to_move, train_tree)
from view.gui_view import GameView
from controller.game_controller import GameController
from tests.test_integracion_hvh import VistaFalsa

_CACHE = {}


def datos_de_prueba():
    """Dataset y árbol de prueba: se construyen una sola vez."""
    if not _CACHE:
        df, _, _ = build_dataset(300, seed=3)
        _CACHE["df"] = df
        _CACHE["tree"] = train_tree(df[FEATURE_COLUMNS], df[TARGET_COLUMN])
    return _CACHE["df"], _CACHE["tree"]


def tablero_desde_fila(fila):
    """Reconstruye el tablero de una fila del dataset y quién mueve."""
    cells = [int(fila[c]) for c in FEATURE_COLUMNS]
    if cells.count(1) == cells.count(-1):
        mover, rival = 'X', 'O'      # mueve X (X siempre abre)
    else:
        mover, rival = 'O', 'X'
    t = Board()
    for i, v in enumerate(cells):
        if v == 1:
            t.make_move((i // 3, i % 3), mover)
        elif v == -1:
            t.make_move((i // 3, i % 3), rival)
    return t, mover, rival


class ArbolFalso:
    """Árbol de mentira: siempre dice 'casilla 4 con probabilidad 1'."""
    classes_ = [4]

    def predict_proba(self, X):
        return [[1.0]]


class TestMLAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df, cls.tree = datos_de_prueba()

    def test_contrato_del_agente(self):
        agente = MLAgent(self.tree, 'O', 'X')
        self.assertEqual(agente.nodes_evaluated, 0)
        agente.get_move(Board())
        self.assertEqual(agente.nodes_evaluated, 0)

    def test_roles_iguales_lanzan_error(self):
        with self.assertRaises(ValueError):
            MLAgent(self.tree, 'X', 'X')

    def test_reproduce_las_etiquetas_del_dataset(self):
        for _, fila in self.df.iterrows():
            tablero, mover, rival = tablero_desde_fila(fila)
            agente = MLAgent(self.tree, mover, rival)
            esperado = index_to_move(int(fila[TARGET_COLUMN]))
            self.assertEqual(agente.get_move(tablero), esperado,
                             f"Falló en:\n{tablero}")

    def test_apertura_como_x(self):
        self.assertEqual(MLAgent(self.tree, 'X', 'O').get_move(Board()), (0, 0))

    def test_partida_terminada_devuelve_none(self):
        t = Board()
        for casilla in [(0, 0), (0, 1), (0, 2)]:
            t.make_move(casilla, 'X')
        self.assertIsNone(MLAgent(self.tree, 'O', 'X').get_move(t))

    def test_get_move_no_modifica_el_tablero(self):
        t = Board()
        t.make_move((0, 0), 'X')
        antes = [fila[:] for fila in t.grid]
        MLAgent(self.tree, 'O', 'X').get_move(t)
        self.assertEqual(t.grid, antes)

    def test_siempre_juega_en_casilla_libre(self):
        X, y = self.df[FEATURE_COLUMNS], self.df[TARGET_COLUMN]
        rng = random.Random(11)
        for profundidad in (1, None):
            arbol = train_tree(X, y, max_depth=profundidad)
            for partida in range(100):
                rol = 'X' if partida % 2 == 0 else 'O'
                rival = 'O' if rol == 'X' else 'X'
                agente = MLAgent(arbol, rol, rival)
                t, turno = Board(), 'X'
                while not t.is_game_over():
                    if turno == rol:
                        jugada = agente.get_move(t)
                        self.assertIn(jugada, t.get_available_moves())
                    else:
                        jugada = rng.choice(t.get_available_moves())
                    t.make_move(jugada, turno)
                    turno = 'O' if turno == 'X' else 'X'

    def test_respaldo_si_el_arbol_propone_casilla_ocupada(self):
        t = Board()
        t.make_move((1, 1), 'X')               # el centro (casilla 4) está ocupado
        agente = MLAgent(ArbolFalso(), 'O', 'X')
        self.assertEqual(agente.get_move(t), (0, 0))   # primera del orden de respaldo
        self.assertTrue(agente.last_was_fallback)
        self.assertEqual(agente.fallbacks, 1)
        self.assertEqual(agente.moves, 1)


class TestFromDataset(unittest.TestCase):

    def test_crea_el_csv_si_no_existe(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "sub", "dataset.csv")
            agente = MLAgent.from_dataset('O', path=ruta, n_games=100, seed=1)
            self.assertTrue(os.path.exists(ruta))
            self.assertIn(agente.get_move(Board()), Board().get_available_moves())

    def test_usa_el_csv_existente_sin_regenerarlo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "dataset.csv")
            MLAgent.from_dataset('O', path=ruta, n_games=100, seed=1)
            antes = os.path.getmtime(ruta)
            MLAgent.from_dataset('O', path=ruta, n_games=100, seed=1)
            self.assertEqual(os.path.getmtime(ruta), antes)


def crear_juego_ml():
    _, arbol = datos_de_prueba()
    board = Board()
    view = VistaFalsa()
    controller = GameController(board, view)
    controller.register_agent("ml", MLAgent(arbol, 'O', 'X'))
    view.on_mode_change("ml")
    return board, view, controller


class TestIntegracionML(unittest.TestCase):

    def test_la_ia_ml_responde_con_cero_nodos(self):
        board, view, _ = crear_juego_ml()
        view.click(0, 0)
        self.assertEqual(view.cells[(0, 0)], 'X')
        self.assertEqual(list(view.cells.values()).count('O'), 1)
        self.assertEqual(view.metrics[0], 0)
        self.assertEqual(view.status, "Turno de X")

    def test_partidas_completas_sin_errores(self):
        rng = random.Random(1)
        board, view, controller = crear_juego_ml()
        for _ in range(100):
            while not controller.game_over:
                view.click(*rng.choice(board.get_available_moves()))
                self.assertNotIn("inválida", view.status)
            view.on_reset()
        self.assertGreater(view.summary[0], 0)

    def test_con_la_vista_real(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No hay pantalla disponible para Tkinter")
        root.withdraw()
        try:
            _, arbol = datos_de_prueba()
            view = GameView(root)
            controller = GameController(Board(), view)
            controller.register_agent("ml", MLAgent(arbol, 'O', 'X'))
            view.mode_var.set("ml")
            view._mode_changed()
            view.cells[0][0].invoke()
            textos = [b["text"] for fila in view.cells for b in fila]
            self.assertEqual(textos.count("X"), 1)
            self.assertEqual(textos.count("O"), 1)
            self.assertEqual(view.nodes_var.get(), "0")
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()