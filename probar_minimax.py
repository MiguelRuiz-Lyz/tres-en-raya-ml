"""
Demostración de Minimax (Semana 2, Día 3).
Parte 1: traza de la recursión. Parte 2: decisiones concretas.
Parte 3: el tablero vacío completo. Parte 4: Minimax contra Minimax.
"""

import time

from model.game_model import Board
from model.minimax_agent import MinimaxAgent


def tablero_desde(texto):
    t = Board()
    for i, ficha in enumerate(texto):
        if ficha != ' ':
            t.make_move((i // 3, i % 3), ficha)
    return t


if __name__ == "__main__":
    # ---------------- PARTE 1: traza ----------------
    print("=== PARTE 1: traza de la recursión (tablero con 4 casillas libres) ===")
    ia = MinimaxAgent('O', 'X')
    tablero = tablero_desde("XX OO X  ")
    print(tablero, "\n")
    ia.trace = True
    mejor = ia.get_move(tablero)
    ia.trace = False
    print(f"\nMejor jugada: {mejor} (esperado: (1, 2))")
    print(f"Nodos explorados: {ia.nodes_evaluated}")

    # ---------------- PARTE 2: decisiones ----------------
    print("\n=== PARTE 2: decisiones concretas ===")
    casos = [
        ("Ganar de inmediato", "OO XX X  ", (0, 2)),
        ("Bloquear al rival",  "XX  O    ", (0, 2)),
        ("Responder a X en el centro", "    X    ", (0, 0)),
    ]
    for nombre, texto, esperado in casos:
        t = tablero_desde(texto)
        print(f"\n{nombre}:")
        print(t)
        valores = ia.score_moves(t)
        print("Valores por jugada:", valores)
        print(f"Elige: {ia.get_move(t)}  (esperado: {esperado})   "
              f"Nodos: {ia.nodes_evaluated:,}")

    # ---------------- PARTE 3: tablero vacío ----------------
    print("\n=== PARTE 3: primera jugada desde el tablero vacío (IA = X) ===")
    print("(puede tardar unos segundos...)")
    ia_x = MinimaxAgent('X', 'O')
    inicio = time.perf_counter()
    valores = ia_x.score_moves(Board())
    segundos = time.perf_counter() - inicio
    print("Valores:", sorted({v for _, v in valores}), "(esperado: [0], todas empatan)")
    print(f"Nodos explorados: {ia_x.nodes_evaluated:,}   (esperado: 549,945)")
    print(f"Tiempo: {segundos:.2f} s")

    # ---------------- PARTE 4: Minimax vs Minimax ----------------
    print("\n=== PARTE 4: Minimax (X) contra Minimax (O) ===")
    tablero = Board()
    jugadores = {'X': MinimaxAgent('X', 'O'), 'O': MinimaxAgent('O', 'X')}
    turno = 'X'
    while not tablero.is_game_over():
        agente = jugadores[turno]
        jugada = agente.get_move(tablero)
        tablero.make_move(jugada, turno)
        print(f"{turno} juega {jugada}  (nodos: {agente.nodes_evaluated:,})")
        turno = 'O' if turno == 'X' else 'X'
    print()
    print(tablero)
    print("\nResultado:", "Empate" if tablero.is_draw() else f"Ganó {tablero.get_winner()}",
          "(esperado: Empate)")