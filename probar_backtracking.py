"""
Demostración del Backtracking (Semana 2, Día 1).
No es parte del juego: solo recorre el árbol para verlo y contarlo.
"""

import time

from model.game_model import Board


def foto(board):
    return [fila[:] for fila in board.grid]


def otro(jugador):
    return 'O' if jugador == 'X' else 'X'


# ----------------------------------------------------------------------
# PARTE 1: traza visible (solo unas pocas ramas, para poder leerla)
# ----------------------------------------------------------------------
def traza(board, jugador, nivel, limite, max_ramas):
    if nivel == limite:
        return
    sangria = "    " * nivel
    # La lista de jugadas se calcula UNA vez antes de probar ninguna.
    for mov in board.get_available_moves()[:max_ramas]:
        board.make_move(mov, jugador)                      # 1) HACER
        print(f"{sangria}{jugador} juega {mov}")
        traza(board, otro(jugador), nivel + 1, limite, max_ramas)   # 2) EXPLORAR
        board.undo_move(mov)                               # 3) DESHACER
        print(f"{sangria}<- deshace {mov}")


# ----------------------------------------------------------------------
# PARTE 2: recorrido COMPLETO del árbol, contando todo
# ----------------------------------------------------------------------
def contar(board, jugador, nivel, stats):
    stats["nodos"] += 1
    stats["por_nivel"][nivel] += 1

    ganador = board.get_winner()
    if ganador is not None or board.is_full():      # estado terminal (hoja)
        stats["partidas"] += 1
        stats[ganador if ganador else "empate"] += 1
        return

    for mov in board.get_available_moves():
        board.make_move(mov, jugador)               # HACER
        contar(board, otro(jugador), nivel + 1, stats)   # EXPLORAR
        board.undo_move(mov)                        # DESHACER


if __name__ == "__main__":
    # ---------- PARTE 1 ----------
    print("=== PARTE 1: traza del backtracking ===")
    tablero = Board()
    tablero.make_move((1, 1), 'X')
    tablero.make_move((0, 0), 'O')
    antes = foto(tablero)

    traza(tablero, 'X', 0, limite=3, max_ramas=2)

    print("\n¿El tablero quedó igual que al inicio?", foto(tablero) == antes,
          "(esperado: True)")

    # ---------- PARTE 2 ----------
    print("\n=== PARTE 2: árbol completo de Tres en Raya ===")
    print("(puede tardar entre 10 y 40 segundos, espera...)")
    tablero = Board()
    stats = {"nodos": 0, "partidas": 0, "X": 0, "O": 0, "empate": 0,
             "por_nivel": [0] * 10}

    inicio = time.perf_counter()
    contar(tablero, 'X', 0, stats)
    segundos = time.perf_counter() - inicio

    print(f"Nodos del árbol:       {stats['nodos']:>8,}   (esperado: 549,946)")
    print(f"Partidas completas:    {stats['partidas']:>8,}   (esperado: 255,168)")
    print(f"  Ganó X:              {stats['X']:>8,}   (esperado: 131,184)")
    print(f"  Ganó O:              {stats['O']:>8,}   (esperado: 77,904)")
    print(f"  Empates:             {stats['empate']:>8,}   (esperado: 46,080)")
    print("Nodos por profundidad:", stats["por_nivel"])
    print("  esperado:           [1, 9, 72, 504, 3024, 15120, 54720, 148176, 200448, 127872]")
    print(f"Tiempo: {segundos:.1f} s")
    print("¿El tablero volvió a quedar vacío?", foto(tablero) == foto(Board()),
          "(esperado: True)")