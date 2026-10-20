"""
PRUEBAS DE ARQUITECTURA - Validación del patrón MVC.

Revisan qué importa cada capa y si la vista contiene lógica de juego.
"""

import ast
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Métodos de reglas del juego: NO deben aparecer en la vista
METODOS_DE_REGLAS = [
    "check_winner", "get_winner", "is_valid_move", "get_available_moves",
    "make_move", "undo_move", "is_draw", "is_full", "is_game_over",
]


def archivos_py(carpeta):
    """Lista los archivos .py de una carpeta del proyecto."""
    ruta = os.path.join(RAIZ, carpeta)
    return [os.path.join(carpeta, nombre)
            for nombre in sorted(os.listdir(ruta)) if nombre.endswith(".py")]


def leer(ruta_relativa):
    with open(os.path.join(RAIZ, ruta_relativa), encoding="utf-8") as f:
        return f.read()


def modulos_importados(ruta_relativa):
    """Devuelve los módulos que importa un archivo (solo el nombre base)."""
    arbol = ast.parse(leer(ruta_relativa))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                modulos.add(alias.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module.split(".")[0])
    return modulos


class TestArquitecturaMVC(unittest.TestCase):

    def test_el_modelo_no_conoce_vista_ni_controlador(self):
        prohibidos = {"view", "controller", "tkinter"}
        for archivo in archivos_py("model"):
            with self.subTest(archivo=archivo):
                self.assertEqual(modulos_importados(archivo) & prohibidos, set())

    def test_la_vista_no_conoce_modelo_ni_controlador(self):
        prohibidos = {"model", "controller"}
        for archivo in archivos_py("view"):
            with self.subTest(archivo=archivo):
                self.assertEqual(modulos_importados(archivo) & prohibidos, set())

    def test_el_controlador_no_usa_tkinter_ni_importa_la_vista(self):
        prohibidos = {"view", "tkinter"}
        for archivo in archivos_py("controller"):
            with self.subTest(archivo=archivo):
                self.assertEqual(modulos_importados(archivo) & prohibidos, set())

    def test_la_vista_no_contiene_logica_de_juego(self):
        for archivo in archivos_py("view"):
            codigo = leer(archivo)
            for metodo in METODOS_DE_REGLAS:
                with self.subTest(archivo=archivo, metodo=metodo):
                    self.assertNotIn(metodo, codigo)


if __name__ == "__main__":
    unittest.main()