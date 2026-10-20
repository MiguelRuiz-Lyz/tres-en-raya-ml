"""
MODELO - Comparación Minimax vs Árbol de Decisión (Semana 3, Día 5).

Mide precisión (sobre TODAS las posiciones alcanzables), latencia por etapa
de la partida y resultados de partidas completas.

IMPORTANTE: este archivo NO debe importar nada de view/ ni controller/.
"""

import random
import time

import pandas as pd

from model.game_model import Board
from model.minimax_agent import MinimaxAgent
from model.ml_agent import FEATURE_COLUMNS, MLAgent, encode_board, load_dataset


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def other(player):
    return 'O' if player == 'X' else 'X'


def grid_key(board):
    """Copia inmutable del tablero (sirve como clave de diccionario)."""
    return tuple(tuple(fila) for fila in board.grid)


def board_from_key(key):
    """Reconstruye un tablero a partir de su clave."""
    board = Board()
    for r in range(3):
        for c in range(3):
            if key[r][c] != Board.EMPTY:
                board.make_move((r, c), key[r][c])
    return board


def count_pieces(key):
    return sum(1 for fila in key for celda in fila if celda != Board.EMPTY)


def dataset_cells(df):
    """Conjunto de posiciones (codificadas) que están en el dataset."""
    return {tuple(int(v) for v in fila)
            for fila in df[FEATURE_COLUMNS].to_numpy()}


def outcome(value):
    """Resultado teórico de un valor de Minimax: 1 gana, 0 empata, -1 pierde."""
    return (value > 0) - (value < 0)


# ----------------------------------------------------------------------
# Todas las posiciones alcanzables
# ----------------------------------------------------------------------
def enumerate_positions():
    """
    Recorre el árbol (con backtracking) y devuelve un diccionario
    {posición: quién mueve} con todas las posiciones alcanzables NO terminales.
    """
    posiciones = {}
    board = Board()

    def explorar(turno):
        clave = grid_key(board)
        if clave in posiciones or board.is_game_over():
            return
        posiciones[clave] = turno
        for jugada in board.get_available_moves():
            board.make_move(jugada, turno)
            explorar(other(turno))
            board.undo_move(jugada)

    explorar('X')
    return posiciones


# ----------------------------------------------------------------------
# Precisión y latencia, posición por posición
# ----------------------------------------------------------------------
def compare_agents(tree, positions=None, seen_cells=None,
                   min_pieces=0, reps=3, progress=None):
    """
    Para cada posición, Minimax y el árbol eligen jugada y se miden.
    Devuelve una tabla con una fila por posición:
      pieces, mover, seen, mm_ms, mm_nodes, ml_ms,
      match (misma casilla), optimal (mismo resultado teórico),
      fallback (el árbol usó el orden de respaldo).
    'min_pieces' permite probar solo posiciones avanzadas (más rápido).
    """
    if positions is None:
        positions = enumerate_positions()
    if seen_cells is None:
        seen_cells = dataset_cells(load_dataset())

    ml = {'X': MLAgent(tree, 'X', 'O'), 'O': MLAgent(tree, 'O', 'X')}
    mm = {'X': MinimaxAgent('X', 'O'), 'O': MinimaxAgent('O', 'X')}
    ml['X'].get_move(Board())          # calentamiento: la 1.ª consulta es lenta

    items = [(k, m) for k, m in positions.items() if count_pieces(k) >= min_pieces]
    filas = []
    for i, (clave, mover) in enumerate(items):
        board = board_from_key(clave)

        # --- Minimax: puntúa todas las jugadas (así sabemos cuán buena es cada una)
        t0 = time.perf_counter()
        resultados = mm[mover].score_moves(board)
        mm_ms = (time.perf_counter() - t0) * 1000
        valores = dict(resultados)
        mejor_valor = max(valores.values())
        mejor = max(resultados, key=lambda par: par[1])[0]   # igual que get_move

        # --- Árbol: se repite 'reps' veces y se promedia
        agente = ml[mover]
        t0 = time.perf_counter()
        jugada = agente.get_move(board)
        tiempos = [(time.perf_counter() - t0) * 1000]
        fallback = agente.last_was_fallback
        for _ in range(reps - 1):
            t0 = time.perf_counter()
            agente.get_move(board)
            tiempos.append((time.perf_counter() - t0) * 1000)

        filas.append({
            "pieces": count_pieces(clave),
            "mover": mover,
            "seen": encode_board(board, mover) in seen_cells,
            "mm_ms": mm_ms,
            "mm_nodes": mm[mover].nodes_evaluated,
            "ml_ms": sum(tiempos) / len(tiempos),
            "match": jugada == mejor,
            "optimal": outcome(valores[jugada]) == outcome(mejor_valor),
            "fallback": fallback,
        })
        if progress:
            progress(i + 1, len(items))

    return pd.DataFrame(filas)


def summarize(df):
    """Cifras globales de la comparación."""
    vistas = df[df["seen"]]
    nuevas = df[~df["seen"]]
    return {
        "positions": len(df),
        "seen": len(vistas),
        "unseen": len(nuevas),
        "match_all": float(df["match"].mean()),
        "match_seen": float(vistas["match"].mean()),
        "match_unseen": float(nuevas["match"].mean()),
        "optimal_all": float(df["optimal"].mean()),
        "optimal_seen": float(vistas["optimal"].mean()),
        "optimal_unseen": float(nuevas["optimal"].mean()),
        "fallback_rate": float(df["fallback"].mean()),
        "mm_ms": float(df["mm_ms"].mean()),
        "ml_ms": float(df["ml_ms"].mean()),
        "mm_nodes": float(df["mm_nodes"].mean()),
    }


def by_pieces(df):
    """Promedios agrupados por cantidad de fichas en el tablero."""
    return (df.groupby("pieces")
              .agg(positions=("match", "size"),
                   mm_ms=("mm_ms", "mean"),
                   ml_ms=("ml_ms", "mean"),
                   mm_nodes=("mm_nodes", "mean"),
                   match=("match", "mean"),
                   optimal=("optimal", "mean"))
              .reset_index())


# ----------------------------------------------------------------------
# Partidas completas
# ----------------------------------------------------------------------
def play_game(player_x, player_o):
    """Juega una partida. Cada jugador es una función(board) -> jugada.
    Devuelve 'X', 'O' o None (empate). Lanza ValueError ante una jugada ilegal."""
    board = Board()
    jugadores = {'X': player_x, 'O': player_o}
    turno = 'X'
    while not board.is_game_over():
        jugada = jugadores[turno](board)
        if jugada is None or not board.make_move(jugada, turno):
            raise ValueError(f"Jugada ilegal de {turno}: {jugada}")
        turno = other(turno)
    return board.get_winner()


def random_player(rng):
    return lambda board: rng.choice(board.get_available_moves())


def minimax_player(role, cache):
    """Minimax con caché compartida (misma posición = misma respuesta)."""
    agente = MinimaxAgent(role, other(role))

    def jugar(board):
        clave = (grid_key(board), role)
        if clave not in cache:
            cache[clave] = agente.get_move(board)
        return cache[clave]
    return jugar


def match(factory_a, factory_b, n_games):
    """A contra B, alternando fichas. Cada 'factory' recibe la ficha y devuelve
    un jugador. Resultados vistos desde A: win / draw / loss."""
    res = {"win": 0, "draw": 0, "loss": 0}
    for i in range(n_games):
        rol_a = 'X' if i % 2 == 0 else 'O'
        a, b = factory_a(rol_a), factory_b(other(rol_a))
        ganador = play_game(a, b) if rol_a == 'X' else play_game(b, a)
        if ganador is None:
            res["draw"] += 1
        elif ganador == rol_a:
            res["win"] += 1
        else:
            res["loss"] += 1
    return res


def run_matches(tree, n_games=1000, seed=42):
    """Las tres series de partidas de la comparación."""
    ml = {'X': MLAgent(tree, 'X', 'O'), 'O': MLAgent(tree, 'O', 'X')}
    cache = {}
    ml_f = lambda role: ml[role].get_move
    mm_f = lambda role: minimax_player(role, cache)
    rng_a, rng_b = random.Random(seed), random.Random(seed)
    azar_a = lambda role: random_player(rng_a)
    azar_b = lambda role: random_player(rng_b)
    return {
        "ML vs azar": match(ml_f, azar_a, n_games),
        "Minimax vs azar": match(mm_f, azar_b, n_games),
        "ML vs Minimax": match(ml_f, mm_f, 2),
    }