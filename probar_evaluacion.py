"""
Demostración de la función de evaluación (Semana 2, Día 2).
Parte 1: tableros concretos. Parte 2: todas las hojas del árbol.
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


def otro(jugador):
    return 'O' if jugador == 'X' else 'X'


def recorrer(board, jugador, agente, conteo):
    """Recorre todo el árbol y puntúa cada hoja con evaluate()."""
    if board.get_winner() is not None or board.is_full():   # hoja
        puntaje = agente.evaluate(board)
        conteo[puntaje] = conteo.get(puntaje, 0) + 1
        return
    for mov in board.get_available_moves():
        board.make_move(mov, jugador)                        # HACER
        recorrer(board, otro(jugador), agente, conteo)       # EXPLORAR
        board.undo_move(mov)                                 # DESHACER


if __name__ == "__main__":
    ia = MinimaxAgent('O', 'X')        # la IA juega con O
    ia_x = MinimaxAgent('X', 'O')      # la IA juega con X

    print("=== PARTE 1: tableros concretos ===")
    casos = [
        ("Gana la IA (O)",     "OOOXX X  ", +10),
        ("Gana el humano (X)", "XXXOO    ", -10),
        ("Empate",             "XOXXOOOXX",   0),
        ("Tablero vacío",      "         ",   0),
        ("Partida en curso",   "X   O    ",   0),
    ]
    for nombre, texto, esperado in casos:
        t = tablero_desde(texto)
        print(t)
        print(f"-> {nombre}: evaluate = {ia.evaluate(t):+d}   (esperado: {esperado:+d})")
        print()

    t = tablero_desde("XXXOO    ")
    print("Mismo tablero (ganó X), si la IA jugara con X:",
          f"{ia_x.evaluate(t):+d}", "(esperado: +10)")

    print("\n=== PARTE 2: evaluar TODAS las hojas del árbol ===")
    print("(puede tardar unos segundos...)")
    tablero = Board()
    conteo = {}
    inicio = time.perf_counter()
    recorrer(tablero, 'X', ia, conteo)
    segundos = time.perf_counter() - inicio

    total = sum(conteo.values())
    suma = sum(p * n for p, n in conteo.items())
    print(f"Hojas con +10 (ganó O): {conteo.get(10, 0):>8,}   (esperado: 77,904)")
    print(f"Hojas con -10 (ganó X): {conteo.get(-10, 0):>8,}   (esperado: 131,184)")
    print(f"Hojas con   0 (empate): {conteo.get(0, 0):>8,}   (esperado: 46,080)")
    print(f"Total de hojas:         {total:>8,}   (esperado: 255,168)")
    print(f"Suma de todos los puntajes: {suma:,}   (esperado: -532,800)")
    print(f"Tiempo: {segundos:.1f} s")
    print("¿El tablero volvió a quedar vacío?",
          all(c == Board.EMPTY for fila in tablero.grid for c in fila),
          "(esperado: True)")