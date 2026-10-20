"""
Generación del dataset real (Semana 3, Día 2).
Simula, limpia, valida y guarda data/dataset.csv.
"""

from model.ml_agent import (DEFAULT_DATASET_PATH, FEATURE_COLUMNS, TARGET_COLUMN,
                            build_dataset, load_dataset, validate_dataset)

if __name__ == "__main__":
    print("Generando dataset (1000 partidas, semilla 42)...")
    df, informe, resumen = build_dataset(1000, seed=42, path=DEFAULT_DATASET_PATH)

    print("\n=== LIMPIEZA ===")
    print(f"Filas antes:         {informe['rows_before']:>6,}   (esperado: 3,267)")
    print(f"Nulos eliminados:    {informe['nulls_removed']:>6,}   (esperado: 0)")
    print(f"Duplicados quitados: {informe['duplicates_removed']:>6,}   (esperado: 2,846)")
    print(f"Filas después:       {informe['rows_after']:>6,}   (esperado: 421)")

    print("\n=== PRIMERAS 5 FILAS ===")
    print(df.head(5).to_string(index=False))

    print("\n=== ¿QUÉ CASILLA ELIGE MINIMAX? (filas por etiqueta) ===")
    conteo = df[TARGET_COLUMN].value_counts().sort_index()
    for casilla, n in conteo.items():
        print(f"  casilla {casilla}: {n:>4}")

    print("\n=== POSICIONES SEGÚN LAS FICHAS EN EL TABLERO ===")
    fichas = (df[FEATURE_COLUMNS] != 0).sum(axis=1)
    for n_fichas, n in fichas.value_counts().sort_index().items():
        print(f"  {n_fichas} fichas: {n:>4} posiciones")

    print(f"\nCobertura aprox.: {len(df) / 4520:.1%} de las 4,520 posiciones "
          "no terminales posibles")

    print("\n=== VERIFICACIÓN DEL ARCHIVO ===")
    cargado = load_dataset()
    print(f"Archivo: {DEFAULT_DATASET_PATH}")
    print(f"Filas leídas del CSV: {len(cargado)}   (esperado: 421)")
    print(f"Problemas de validación: {validate_dataset(cargado)}   (esperado: [])")