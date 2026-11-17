# Tres en Raya: Minimax con Backtracking y Árbol de Decisión

Proyecto educativo que compara una IA basada en búsqueda (Minimax)
con un modelo de Machine Learning (DecisionTreeClassifier).

## Arquitectura
Patrón MVC:
- `model/`: lógica del juego y agentes de IA
- `view/`: interfaz gráfica (Tkinter)
- `controller/`: conexión entre modelo y vista

## Cómo ejecutar
    python main.py

## Plan
- Semana 1: Lógica, MVC e interfaz
- Semana 2: Backtracking y Minimax
- Semana 3: Dataset y Machine Learning

## Cómo ejecutar
    python main.py                                  # el juego (3 modos)
    python -m unittest discover -s tests -t . -v    # 130 pruebas
    python probar_limpieza.py                       # genera data/dataset.csv
    python comparar_agentes.py                      # comparación final (docs/)