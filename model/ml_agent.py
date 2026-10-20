"""
MODELO - Generación de dataset y agente de Machine Learning.

Semana 3, Día 1: simulación de partidas Minimax vs jugador aleatorio.
Semana 3, Día 2: limpieza y guardado en CSV.
Semana 3, Días 3 y 4: Árbol de Decisión y agente ML.

IMPORTANTE: este archivo NO debe importar nada de view/ ni controller/.
"""

import os
import random

import numpy as np
import pandas as pd

from model.game_model import Board
from model.minimax_agent import MinimaxAgent


# ----------------------------------------------------------------------
# Conversión del tablero a números (características del modelo)
# ----------------------------------------------------------------------
def encode_board(board, player):
    """
    Convierte el tablero en 9 números, vistos desde 'player':
      1 = ficha de 'player', -1 = ficha del rival, 0 = casilla vacía.
    El orden es por filas: casilla 0 = (0,0), casilla 1 = (0,1), ... casilla 8 = (2,2).
    """
    rival = 'O' if player == 'X' else 'X'
    codigos = []
    for fila in range(3):
        for col in range(3):
            celda = board.get_cell(fila, col)
            if celda == player:
                codigos.append(1)
            elif celda == rival:
                codigos.append(-1)
            else:
                codigos.append(0)
    return tuple(codigos)


def move_to_index(move):
    """(fila, columna) -> número de casilla 0..8."""
    return move[0] * 3 + move[1]


def index_to_move(index):
    """número de casilla 0..8 -> (fila, columna)."""
    return (index // 3, index % 3)


# ----------------------------------------------------------------------
# Generador del dataset
# ----------------------------------------------------------------------
class DatasetGenerator:
    """Juega partidas Minimax vs azar y registra las decisiones de Minimax."""

    def __init__(self, seed=None):
        self.rng = random.Random(seed)    # 'seed' permite repetir los resultados
        self.agents = {
            'X': MinimaxAgent(ai_player='X', human_player='O'),
            'O': MinimaxAgent(ai_player='O', human_player='X'),
        }
        self._cache = {}                  # posición -> jugada de Minimax

    def _best_move(self, board, player):
        """Jugada óptima de Minimax; se calcula una sola vez por posición."""
        clave = (tuple(tuple(fila) for fila in board.grid), player)
        if clave not in self._cache:
            self._cache[clave] = self.agents[player].get_move(board)
        return self._cache[clave]

    def play_game(self, game_id, minimax_player):
        """
        Juega UNA partida. Minimax usa la ficha 'minimax_player'; el rival
        elige al azar. Devuelve (registros, resultado), con resultado
        'win', 'draw' o 'loss' visto desde Minimax.
        """
        board = Board()
        turno = 'X'                       # X siempre abre
        registros = []

        while not board.is_game_over():
            if turno == minimax_player:
                jugada = self._best_move(board, turno)
                registros.append({
                    "game": game_id,
                    "player": turno,
                    "cells": encode_board(board, turno),   # características
                    "move": move_to_index(jugada),         # etiqueta
                })
            else:
                jugada = self.rng.choice(board.get_available_moves())
            board.make_move(jugada, turno)
            turno = 'O' if turno == 'X' else 'X'

        ganador = board.get_winner()
        if ganador is None:
            resultado = 'draw'
        elif ganador == minimax_player:
            resultado = 'win'
        else:
            resultado = 'loss'
        return registros, resultado

    def generate(self, n_games, roles=('X', 'O')):
        """
        Juega 'n_games' partidas alternando el rol de Minimax según 'roles'.
        Devuelve (registros, resumen).
        """
        registros = []
        resumen = {"games": n_games, "win": 0, "draw": 0, "loss": 0}
        for game_id in range(n_games):
            rol = roles[game_id % len(roles)]
            nuevos, resultado = self.play_game(game_id, rol)
            registros.extend(nuevos)
            resumen[resultado] += 1
        return registros, resumen



# ----------------------------------------------------------------------
# Día 2: limpieza, validación y guardado del dataset
# ----------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "dataset.csv")

FEATURE_COLUMNS = [f"c{i}" for i in range(9)]   # c0..c8: las 9 casillas
TARGET_COLUMN = "move"                          # la casilla elegida (0..8)


def records_to_dataframe(registros):
    """Lista de registros -> tabla con columnas c0..c8 y move.
    (Las columnas 'game' y 'player' se descartan a propósito.)"""
    filas = []
    for reg in registros:
        fila = dict(zip(FEATURE_COLUMNS, reg["cells"]))
        fila[TARGET_COLUMN] = reg["move"]
        filas.append(fila)
    return pd.DataFrame(filas, columns=FEATURE_COLUMNS + [TARGET_COLUMN])


def clean_dataset(df):
    """
    Quita nulos y duplicados, convierte a enteros y ordena.
    NO resuelve contradicciones: de eso se encarga validate_dataset.
    Devuelve (tabla_limpia, informe).
    """
    informe = {"rows_before": len(df)}

    sin_nulos = df.dropna()
    informe["nulls_removed"] = len(df) - len(sin_nulos)

    sin_duplicados = sin_nulos.drop_duplicates()
    informe["duplicates_removed"] = len(sin_nulos) - len(sin_duplicados)

    limpio = (sin_duplicados.astype(int)
              .sort_values(FEATURE_COLUMNS + [TARGET_COLUMN])
              .reset_index(drop=True))
    informe["rows_after"] = len(limpio)
    return limpio, informe


def validate_dataset(df):
    """Devuelve la lista de problemas encontrados ([] = dataset válido)."""
    if list(df.columns) != FEATURE_COLUMNS + [TARGET_COLUMN]:
        return ["Las columnas no son c0..c8 + move."]
    if df.empty:
        return ["El dataset está vacío."]
    if df.isnull().any().any():
        return ["Hay valores nulos."]

    problemas = []
    valores = df[FEATURE_COLUMNS].to_numpy()
    etiquetas = df[TARGET_COLUMN].to_numpy().astype(int)

    if not np.isin(valores, [-1, 0, 1]).all():
        problemas.append("Hay casillas con valores distintos de -1, 0 o 1.")

    if not ((etiquetas >= 0) & (etiquetas <= 8)).all():
        problemas.append("Hay etiquetas fuera del rango 0..8.")
    else:
        ocupadas = valores[np.arange(len(df)), etiquetas] != 0
        if ocupadas.any():
            problemas.append(
                f"{int(ocupadas.sum())} filas eligen una casilla ocupada.")

    mias = (valores == 1).sum(axis=1)
    rivales = (valores == -1).sum(axis=1)
    imposibles = ~((mias == rivales) | (rivales == mias + 1))
    if imposibles.any():
        problemas.append(
            f"{int(imposibles.sum())} filas tienen una cantidad imposible de fichas.")

    repetidas = int(df.duplicated(subset=FEATURE_COLUMNS).sum())
    if repetidas:
        problemas.append(
            f"{repetidas} filas repiten una posición (duplicada o contradictoria).")

    return problemas


def save_dataset(df, path=DEFAULT_DATASET_PATH):
    """Guarda la tabla como CSV (crea la carpeta si no existe)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return path


def load_dataset(path=DEFAULT_DATASET_PATH):
    """Lee el CSV y devuelve la tabla."""
    return pd.read_csv(path)


def build_dataset(n_games=1000, seed=42, path=None):
    """
    Proceso completo: simular -> tabla -> limpiar -> validar -> (guardar).
    Devuelve (tabla, informe_de_limpieza, resumen_de_partidas).
    Lanza ValueError si la validación encuentra problemas.
    """
    registros, resumen = DatasetGenerator(seed=seed).generate(n_games)
    tabla, informe = clean_dataset(records_to_dataframe(registros))

    problemas = validate_dataset(tabla)
    if problemas:
        raise ValueError("Dataset inválido: " + "; ".join(problemas))

    if path is not None:
        save_dataset(tabla, path)
    return tabla, informe, resumen