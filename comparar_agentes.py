"""
Comparación final Minimax vs Árbol de Decisión (Semana 3, Día 5).
Genera docs/resultados_comparacion.md, docs/comparacion_por_posicion.csv
y docs/latencia_por_fichas.png.
"""

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model.ml_agent import (FEATURE_COLUMNS, PROJECT_ROOT, TARGET_COLUMN,
                            load_dataset, train_tree)
from model.comparison import (by_pieces, compare_agents, dataset_cells,
                              enumerate_positions, run_matches, summarize)

DOCS = os.path.join(PROJECT_ROOT, "docs")


def progreso(i, total):
    if i % 500 == 0 or i == total:
        print(f"  {i:,} / {total:,} posiciones")


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)

    df = load_dataset()
    tree = train_tree(df[FEATURE_COLUMNS], df[TARGET_COLUMN])   # igual que en main.py
    vistas = dataset_cells(df)
    posiciones = enumerate_positions()
    print(f"Dataset: {len(df)} posiciones | Universo: {len(posiciones):,} "
          "posiciones no terminales (esperado: 4,520)")

    # ---------- 1. Posición por posición ----------
    print("\nComparando en TODAS las posiciones (puede tardar 1-2 minutos)...")
    inicio = time.perf_counter()
    tabla = compare_agents(tree, posiciones, vistas, reps=5, progress=progreso)
    print(f"Listo en {time.perf_counter() - inicio:.0f} s")

    r = summarize(tabla)
    print("\n=== PRECISIÓN ===")
    print(f"{'':28}{'Coincide':>10}{'Preserva resultado':>20}")
    print(f"{'Todas (' + format(r['positions'], ',') + ')':28}"
          f"{r['match_all']:>10.1%}{r['optimal_all']:>20.1%}")
    print(f"{'Vistas (' + str(r['seen']) + ')':28}"
          f"{r['match_seen']:>10.1%}{r['optimal_seen']:>20.1%}")
    print(f"{'Nuevas (' + format(r['unseen'], ',') + ')':28}"
          f"{r['match_unseen']:>10.1%}{r['optimal_unseen']:>20.1%}")
    print(f"Veces que el árbol usó el orden de respaldo: {r['fallback_rate']:.1%}")

    print("\n=== LATENCIA PROMEDIO (todas las posiciones) ===")
    print(f"Minimax: {r['mm_ms']:.3f} ms   ({r['mm_nodes']:,.0f} nodos en promedio)")
    print(f"Árbol:   {r['ml_ms']:.3f} ms   (0 nodos)")

    g = by_pieces(tabla)
    print("\n=== LATENCIA Y PRECISIÓN POR ETAPA (fichas en el tablero) ===")
    print(f"{'Fichas':>6} {'Posic.':>7} {'Minimax ms':>11} {'Árbol ms':>9} "
          f"{'Nodos MM':>10} {'Coincide':>9} {'Preserva':>9}")
    for f in g.itertuples():
        print(f"{f.pieces:>6} {f.positions:>7,} {f.mm_ms:>11.4f} {f.ml_ms:>9.4f} "
              f"{f.mm_nodes:>10,.0f} {f.match:>9.1%} {f.optimal:>9.1%}")
    rapidos = g.loc[g.ml_ms < g.mm_ms, "pieces"].tolist()
    print(f"\nEtapas (fichas en el tablero) donde el árbol fue más rápido: {rapidos}")

    # ---------- 2. Gráfico ----------
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(g["pieces"], g["mm_ms"], "o-", label="Minimax")
    ax.plot(g["pieces"], g["ml_ms"], "s-", label="Árbol de Decisión")
    ax.set_yscale("log")
    ax.set_xlabel("Fichas en el tablero (etapa de la partida)")
    ax.set_ylabel("Tiempo promedio por jugada (ms, escala log)")
    ax.set_title("Latencia: Minimax vs Árbol de Decisión")
    ax.grid(True, alpha=0.3)
    ax.legend()
    ruta_img = os.path.join(DOCS, "latencia_por_fichas.png")
    fig.savefig(ruta_img, dpi=120, bbox_inches="tight")
    plt.close(fig)

    # ---------- 3. Partidas completas ----------
    print("\n=== PARTIDAS COMPLETAS (1,000 contra el azar) ===")
    partidas = run_matches(tree, n_games=1000, seed=42)
    for nombre, res in partidas.items():
        total = sum(res.values())
        print(f"{nombre:16} ganó {res['win']:>4} | empató {res['draw']:>4} | "
              f"perdió {res['loss']:>4}   (de {total})")

    # ---------- 4. Archivos para el informe ----------
    tabla.to_csv(os.path.join(DOCS, "comparacion_por_posicion.csv"), index=False)

    L = ["# Resultados de la comparación Minimax vs Árbol de Decisión", "",
         "Generado automáticamente por `comparar_agentes.py`.", "",
         "## Precisión", "",
         "| Conjunto | Posiciones | Coincide con Minimax | Preserva el resultado |",
         "|---|---|---|---|",
         f"| Todas | {r['positions']:,} | {r['match_all']:.1%} | {r['optimal_all']:.1%} |",
         f"| Vistas (entrenamiento) | {r['seen']:,} | {r['match_seen']:.1%} | {r['optimal_seen']:.1%} |",
         f"| Nuevas (generalización) | {r['unseen']:,} | {r['match_unseen']:.1%} | {r['optimal_unseen']:.1%} |",
         "", f"El árbol usó el orden de respaldo en {r['fallback_rate']:.1%} de las posiciones.", "",
         "## Latencia por etapa", "",
         "| Fichas | Posiciones | Minimax (ms) | Árbol (ms) | Nodos Minimax | Coincide | Preserva |",
         "|---|---|---|---|---|---|---|"]
    for f in g.itertuples():
        L.append(f"| {f.pieces} | {f.positions:,} | {f.mm_ms:.4f} | {f.ml_ms:.4f} | "
                 f"{f.mm_nodes:,.0f} | {f.match:.1%} | {f.optimal:.1%} |")
    L += ["", f"Promedio general: Minimax {r['mm_ms']:.3f} ms, Árbol {r['ml_ms']:.3f} ms.",
          f"Etapas (fichas en el tablero) donde el árbol fue más rápido: {rapidos}.", "",
          "## Partidas completas (1,000 contra el azar; 2 contra Minimax)", "",
          "| Serie | Ganó | Empató | Perdió |", "|---|---|---|---|"]
    for nombre, res in partidas.items():
        L.append(f"| {nombre} | {res['win']} | {res['draw']} | {res['loss']} |")
    L += ["", "![Latencia por etapa](latencia_por_fichas.png)", ""]
    ruta_md = os.path.join(DOCS, "resultados_comparacion.md")
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print(f"\nGuardado: {ruta_md}")
    print(f"Guardado: {ruta_img}")