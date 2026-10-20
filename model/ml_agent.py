"""
MODELO - Generación de dataset y agente de Machine Learning.

Semana 3, Día 1: simulación de partidas Minimax vs jugador aleatorio.
Semana 3, Día 2: limpieza y guardado en CSV.
Semana 3, Días 3 y 4: Árbol de Decisión y agente ML.

IMPORTANTE: este archivo NO debe importar nada de view/ ni controller/.
"""

import random

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