"""
PRUEBAS DE LIMPIEZA Y VALIDACIÓN DEL DATASET (Semana 3, Día 2)
"""

import os
import tempfile
import unittest

import pandas as pd

from model.ml_agent import (DatasetGenerator, FEATURE_COLUMNS, TARGET_COLUMN,
                            build_dataset, clean_dataset, load_dataset,
                            records_to_dataframe, save_dataset,
                            validate_dataset)

COLUMNAS = FEATURE_COLUMNS + [TARGET_COLUMN]

# Dos filas válidas de ejemplo: (casillas, etiqueta)
A = ((1, 0, 0, 0, -1, 0, 0, 0, 0), 8)    # mueve X (fichas iguales)
B = ((0, 0, 0, 0, -1, 0, 0, 0, 0), 0)    # mueve O (el rival tiene una más)


def tabla(*filas):
    """Crea un DataFrame a partir de filas (casillas, etiqueta)."""
    datos = [list(cells) + [move] for cells, move in filas]
    return pd.DataFrame(datos, columns=COLUMNAS)


def hay(problemas, fragmento):
    return any(fragmento in p for p in problemas)


class TestConversion(unittest.TestCase):

    def test_columnas_y_filas(self):
        registros, _ = DatasetGenerator(seed=7).generate(30)
        df = records_to_dataframe(registros)
        self.assertEqual(list(df.columns), COLUMNAS)
        self.assertEqual(len(df), len(registros))

    def test_los_valores_se_copian_bien(self):
        registros, _ = DatasetGenerator(seed=7).generate(30)
        df = records_to_dataframe(registros)
        self.assertEqual(df.iloc[0][FEATURE_COLUMNS].tolist(),
                         list(registros[0]["cells"]))
        self.assertEqual(df.iloc[0][TARGET_COLUMN], registros[0]["move"])


class TestLimpieza(unittest.TestCase):

    def test_quita_duplicados(self):
        limpio, informe = clean_dataset(tabla(A, A, B))
        self.assertEqual(len(limpio), 2)
        self.assertEqual(informe["duplicates_removed"], 1)

    def test_quita_nulos(self):
        df = tabla(A, B)
        df.loc[0, "c3"] = None
        limpio, informe = clean_dataset(df)
        self.assertEqual(len(limpio), 1)
        self.assertEqual(informe["nulls_removed"], 1)

    def test_deja_enteros_ordenado_y_con_indice_limpio(self):
        limpio, _ = clean_dataset(tabla(A, B, A))
        self.assertTrue(all(pd.api.types.is_integer_dtype(t)
                            for t in limpio.dtypes))
        self.assertEqual(list(limpio.index), [0, 1])
        ordenado = limpio.sort_values(COLUMNAS).reset_index(drop=True)
        self.assertTrue(limpio.equals(ordenado))

    def test_no_resuelve_contradicciones_en_silencio(self):
        df = tabla((A[0], 2), (A[0], 3))     # misma posición, dos etiquetas
        limpio, _ = clean_dataset(df)
        self.assertEqual(len(limpio), 2)


class TestValidacion(unittest.TestCase):

    def test_dataset_generado_es_valido(self):
        registros, _ = DatasetGenerator(seed=5).generate(100)
        limpio, _ = clean_dataset(records_to_dataframe(registros))
        self.assertEqual(validate_dataset(limpio), [])

    def test_detecta_columnas_incorrectas(self):
        df = tabla(A, B).rename(columns={"c0": "x"})
        self.assertTrue(hay(validate_dataset(df), "columnas"))

    def test_detecta_valor_de_casilla_fuera_de_rango(self):
        df = tabla(((1, 0, 5, 0, -1, 0, 0, 0, 0), 8))
        self.assertTrue(hay(validate_dataset(df), "casillas"))

    def test_detecta_etiqueta_fuera_de_rango(self):
        df = tabla((A[0], 9))
        self.assertTrue(hay(validate_dataset(df), "etiquetas"))

    def test_detecta_etiqueta_sobre_casilla_ocupada(self):
        df = tabla((A[0], 4))                # la casilla 4 ya tiene una ficha
        self.assertTrue(hay(validate_dataset(df), "ocupada"))

    def test_detecta_cantidad_imposible_de_fichas(self):
        df = tabla(((1, 1, 1, 0, 0, 0, 0, 0, 0), 8))
        self.assertTrue(hay(validate_dataset(df), "fichas"))

    def test_detecta_posiciones_repetidas_o_contradictorias(self):
        df = tabla((A[0], 2), (A[0], 3))
        self.assertTrue(hay(validate_dataset(df), "repiten"))

    def test_detecta_dataset_vacio(self):
        self.assertTrue(hay(validate_dataset(tabla()), "vacío"))


class TestCSV(unittest.TestCase):

    def test_guardar_y_cargar_conserva_los_datos(self):
        registros, _ = DatasetGenerator(seed=2).generate(50)
        df, _ = clean_dataset(records_to_dataframe(registros))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = save_dataset(df, os.path.join(carpeta, "dataset.csv"))
            cargado = load_dataset(ruta)
        pd.testing.assert_frame_equal(df, cargado, check_dtype=False)

    def test_build_dataset_crea_un_csv_valido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "sub", "dataset.csv")   # 'sub' no existe
            df, informe, resumen = build_dataset(100, seed=1, path=ruta)
            self.assertTrue(os.path.exists(ruta))
            self.assertEqual(validate_dataset(load_dataset(ruta)), [])
        self.assertEqual(resumen["loss"], 0)
        self.assertLess(informe["rows_after"], informe["rows_before"])
        self.assertEqual(informe["rows_before"] - informe["nulls_removed"]
                         - informe["duplicates_removed"], informe["rows_after"])
        self.assertEqual(len(df), informe["rows_after"])

    def test_build_dataset_es_reproducible(self):
        a, _, _ = build_dataset(60, seed=9)
        b, _, _ = build_dataset(60, seed=9)
        pd.testing.assert_frame_equal(a, b)


if __name__ == "__main__":
    unittest.main()