"""
MODELO - Agente Minimax con Backtracking.

Semana 2, Día 2: función de evaluación.
Semana 2, Día 3: algoritmo Minimax recursivo, contador de nodos y get_move.

IMPORTANTE: este archivo NO debe importar nada de view/ ni controller/.
"""


class MinimaxAgent:
    """Agente que elige jugadas explorando todo el árbol de juego."""

    # Puntajes de los estados terminales, vistos desde la IA
    WIN_SCORE = 10      # ganó la IA
    LOSS_SCORE = -10    # ganó el humano
    DRAW_SCORE = 0      # empate (o nadie ha ganado todavía)

    def __init__(self, ai_player='O', human_player='X'):
        if ai_player == human_player:
            raise ValueError("La IA y el humano deben usar fichas distintas.")
        self.ai_player = ai_player
        self.human_player = human_player
        self.nodes_evaluated = 0   # nodos visitados en la última búsqueda
        self.trace = False         # True = imprime la traza recursiva (para depurar)

    # ------------------------------------------------------------------
    # Día 2: función de evaluación
    # ------------------------------------------------------------------
    def evaluate(self, board):
        """+10 si ganó la IA, -10 si ganó el humano, 0 en cualquier otro caso."""
        if board.check_winner(self.ai_player):
            return self.WIN_SCORE
        if board.check_winner(self.human_player):
            return self.LOSS_SCORE
        return self.DRAW_SCORE

    # ------------------------------------------------------------------
    # Día 3: Minimax recursivo con Backtracking
    # ------------------------------------------------------------------
    def minimax(self, board, depth, is_maximizing):
        """
        Devuelve el valor del tablero actual suponiendo que ambos juegan lo
        mejor posible.
          depth          = cuántas jugadas se han hecho desde la raíz de la búsqueda
          is_maximizing  = True si ahora mueve la IA, False si mueve el humano
        """
        self.nodes_evaluated += 1
        score = self.evaluate(board)

        # --- Casos base (hojas del árbol) ---
        if score == self.WIN_SCORE:
            result = score - depth          # ganar pronto vale más
            self._log(depth, f"hoja: ganó {self.ai_player} -> {result}")
            return result
        if score == self.LOSS_SCORE:
            result = score + depth          # perder tarde duele menos
            self._log(depth, f"hoja: ganó {self.human_player} -> {result}")
            return result

        moves = board.get_available_moves()  # se calcula UNA vez, antes de probar
        if not moves:
            self._log(depth, "hoja: empate -> 0")
            return self.DRAW_SCORE

        # --- Caso recursivo ---
        if is_maximizing:
            player = self.ai_player
            best_score = -float('inf')
        else:
            player = self.human_player
            best_score = float('inf')

        for move in moves:
            board.make_move(move, player)                         # 1) HACER
            self._log(depth, f"{player} prueba {move}")
            value = self.minimax(board, depth + 1, not is_maximizing)  # 2) EXPLORAR
            board.undo_move(move)                                 # 3) DESHACER (backtracking)
            self._log(depth, f"<- deshace {move} (valor {value})")

            if is_maximizing:
                best_score = max(best_score, value)   # la IA quiere lo más alto
            else:
                best_score = min(best_score, value)   # el humano quiere lo más bajo

        return best_score

    # ------------------------------------------------------------------
    # Interfaz que usan el controlador y (en la Semana 3) el dataset
    # ------------------------------------------------------------------
    def score_moves(self, board):
        """
        Puntúa cada jugada posible de la IA en el tablero actual.
        Devuelve una lista de (jugada, valor). Reinicia el contador de nodos.
        Devuelve [] si la partida ya terminó.
        """
        self.nodes_evaluated = 0
        if board.get_winner() is not None or board.is_full():
            return []

        results = []
        for move in board.get_available_moves():
            board.make_move(move, self.ai_player)                 # HACER
            self._log(0, f"{self.ai_player} prueba {move}")
            value = self.minimax(board, 1, False)                 # EXPLORAR (ahora mueve el humano)
            board.undo_move(move)                                 # DESHACER
            self._log(0, f"<- deshace {move} (valor {value})")
            results.append((move, value))
        return results

    def get_move(self, board):
        """
        Devuelve la mejor jugada (fila, columna) para la IA, o None si no hay.
        Si varias jugadas empatan, elige la primera en el orden de
        get_available_moves(): así el agente es determinista.
        """
        results = self.score_moves(board)
        if not results:
            return None
        return max(results, key=lambda par: par[1])[0]

    # ------------------------------------------------------------------
    # Utilidad de depuración
    # ------------------------------------------------------------------
    def _log(self, depth, text):
        if self.trace:
            print("    " * depth + text)