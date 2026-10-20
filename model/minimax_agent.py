"""
MODELO - Agente Minimax con Backtracking.

Semana 2, Día 2: función de evaluación (este archivo).
Semana 2, Día 3: algoritmo Minimax recursivo y contador de nodos.

IMPORTANTE: este archivo NO debe importar nada de view/ ni controller/.
"""


class MinimaxAgent:
    """Agente que puntúa y (desde el Día 3) elige jugadas con Minimax."""

    # Puntajes de los estados terminales, vistos desde la IA
    WIN_SCORE = 10      # ganó la IA
    LOSS_SCORE = -10    # ganó el humano
    DRAW_SCORE = 0      # empate (o nadie ha ganado todavía)

    def __init__(self, ai_player='O', human_player='X'):
        if ai_player == human_player:
            raise ValueError("La IA y el humano deben usar fichas distintas.")
        self.ai_player = ai_player
        self.human_player = human_player
        self.nodes_evaluated = 0   # se usará en el Día 3

    def evaluate(self, board):
        """
        Puntúa un tablero desde el punto de vista de la IA.
          +10 si ganó la IA, -10 si ganó el humano, 0 en cualquier otro caso.
        No modifica el tablero: solo lo observa.
        """
        if board.check_winner(self.ai_player):
            return self.WIN_SCORE
        if board.check_winner(self.human_player):
            return self.LOSS_SCORE
        return self.DRAW_SCORE