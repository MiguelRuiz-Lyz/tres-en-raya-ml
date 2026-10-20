"""
Entrenamiento y exploración del Árbol de Decisión (Semana 3, Día 3).
Requiere data/dataset.csv (se genera con probar_limpieza.py).
"""

import os

import pandas as pd
from sklearn.model_selection import KFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier

from model.minimax_agent import MinimaxAgent
from model.game_model import Board
from model.ml_agent import (FEATURE_COLUMNS, PROJECT_ROOT, TARGET_COLUMN,
                            accuracy, encode_board, index_to_move,
                            legal_prediction_rate, load_dataset,
                            save_tree_plot, split_dataset, train_tree,
                            tree_rules)

DOCS = os.path.join(PROJECT_ROOT, "docs")


def tablero_desde(texto):
    t = Board()
    for i, ficha in enumerate(texto):
        if ficha != ' ':
            t.make_move((i // 3, i % 3), ficha)
    return t


if __name__ == "__main__":
    df = load_dataset()
    X_train, X_test, y_train, y_test = split_dataset(df)
    print(f"Dataset: {len(df)} posiciones  ->  entrenamiento: {len(X_train)}, "
          f"prueba: {len(X_test)}")

    # ---------- 1. Árbol sin límite ----------
    tree = train_tree(X_train, y_train)
    print("\n=== 1. ÁRBOL SIN LÍMITE DE PROFUNDIDAD ===")
    print(f"Profundidad: {tree.get_depth()}   Hojas: {tree.get_n_leaves()}")
    print(f"Precisión en entrenamiento: {accuracy(tree, X_train, y_train):.1%}"
          "   (esperado: 100%)")
    print(f"Precisión en prueba:        {accuracy(tree, X_test, y_test):.1%}"
          "   (esperado: menor que la de entrenamiento)")
    print(f"Jugadas en casilla libre (prueba): "
          f"{legal_prediction_rate(tree, X_test):.1%}")

    # ---------- 2. Sobreajuste ----------
    print("\n=== 2. PROFUNDIDAD vs PRECISIÓN (sobreajuste) ===")
    print(f"{'max_depth':>10} {'entren.':>9} {'prueba':>9}")
    for prof in [1, 2, 3, 4, 5, 6, 8, None]:
        t = train_tree(X_train, y_train, max_depth=prof)
        print(f"{str(prof):>10} {accuracy(t, X_train, y_train):>9.1%} "
              f"{accuracy(t, X_test, y_test):>9.1%}")

    # ---------- 3. Validación cruzada ----------
    X, y = df[FEATURE_COLUMNS], df[TARGET_COLUMN]
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    puntajes = cross_val_score(DecisionTreeClassifier(random_state=42), X, y, cv=kf)
    print("\n=== 3. VALIDACIÓN CRUZADA (5 divisiones distintas) ===")
    print("Precisión por división:", [f"{p:.1%}" for p in puntajes])
    print(f"Promedio: {puntajes.mean():.1%}   (más fiable que una sola división)")

    # ---------- 4. Qué casillas mira el árbol ----------
    print("\n=== 4. IMPORTANCIA DE CADA CASILLA ===")
    for nombre, imp in sorted(zip(FEATURE_COLUMNS, tree.feature_importances_),
                              key=lambda par: -par[1]):
        print(f"  {nombre}: {imp:.1%}")

    # ---------- 5. Reglas ----------
    print("\n=== 5. REGLAS DEL ÁRBOL (primeros 3 niveles) ===")
    print(tree_rules(tree, max_depth=3))

    # ---------- 6. Maestro vs alumno ----------
    print("=== 6. MINIMAX vs ÁRBOL EN POSICIONES CONCRETAS (IA = O) ===")
    maestro = MinimaxAgent('O', 'X')
    casos = [("Ganar de inmediato", "OO XX X  "),
             ("Bloquear al rival", "XX  O    "),
             ("Responder al centro", "    X    ")]
    for nombre, texto in casos:
        t = tablero_desde(texto)
        fila = pd.DataFrame([encode_board(t, 'O')], columns=FEATURE_COLUMNS)
        pred = int(tree.predict(fila)[0])
        print(f"\n{nombre}:\n{t}")
        print(f"  Minimax elige: {maestro.get_move(t)}")
        print(f"  El árbol elige: {index_to_move(pred)}")

    # ---------- 7. Guardar para el informe ----------
    os.makedirs(DOCS, exist_ok=True)
    ruta_reglas = os.path.join(DOCS, "reglas_arbol.txt")
    with open(ruta_reglas, "w", encoding="utf-8") as f:
        f.write(tree_rules(tree))
    ruta_img = save_tree_plot(tree, os.path.join(DOCS, "arbol_decision.png"))
    print(f"\nGuardado: {ruta_reglas}")
    print(f"Guardado: {ruta_img}")