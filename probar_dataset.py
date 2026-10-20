"""
Demostración de la generación de dataset (Semana 3, Día 1).
Simula 1,000 partidas y muestra estadísticas y ejemplos.
"""

import time
from collections import Counter

from model.ml_agent import DatasetGenerator, index_to_move

N_PARTIDAS = 1000


def dibujar(cells):
    """Dibuja un registro: M = mi ficha (la IA), R = rival, vacío = libre."""
    simbolo = {1: 'M', -1: 'R', 0: ' '}
    filas = []
    for f in range(3):
        fila = [simbolo[cells[f * 3 + c]] for c in range(3)]
        filas.append(" " + " | ".join(fila))
    return "\n---+---+---\n".join(filas)


if __name__ == "__main__":
    print(f"Simulando {N_PARTIDAS} partidas (Minimax vs azar)...")
    inicio = time.perf_counter()
    generador = DatasetGenerator(seed=42)
    registros, resumen = generador.generate(N_PARTIDAS)
    segundos = time.perf_counter() - inicio

    print(f"\nTiempo: {segundos:.1f} s")
    print(f"Partidas: {resumen['games']}")
    print(f"  Minimax ganó:   {resumen['win']}")
    print(f"  Empates:        {resumen['draw']}")
    print(f"  Minimax perdió: {resumen['loss']}   (esperado: 0)")

    unicas = {reg["cells"] for reg in registros}
    print(f"\nRegistros (decisiones de Minimax): {len(registros):,}")
    print(f"Posiciones distintas:              {len(unicas):,}")

    contradicciones = {}
    for reg in registros:
        contradicciones.setdefault(reg["cells"], set()).add(reg["move"])
    malas = sum(1 for movs in contradicciones.values() if len(movs) > 1)
    print(f"Posiciones con etiquetas contradictorias: {malas}   (esperado: 0)")

    print("\nCasillas elegidas por Minimax (etiqueta 0-8):")
    conteo = Counter(reg["move"] for reg in registros)
    for i in range(9):
        print(f"  casilla {i} {index_to_move(i)}: {conteo[i]:>5}")

    print("\n--- 3 ejemplos de registros ---")
    for reg in registros[2:5]:
        print()
        print(dibujar(reg["cells"]))
        print(f"Juega con {reg['player']} -> Minimax elige la casilla "
              f"{reg['move']} {index_to_move(reg['move'])}")