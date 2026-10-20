""""
Nombre: Miguel Ruiz Loayza
Versión: v1.2

- Representar el tablero 3x3.
- Validar movimentos.
- Detectar victoria y empate.
- Aplicar y deshacer movimientos (Backtracking): make_move / undo_move..
"""


class Board:
    """Tablero de Tres en Raya. Guarda el estado y conoce las reglas."""

    EMPTY = ' '   # Representa una casilla vacía

    def __init__(self):
        # Matriz 3x3: lista de 3 filas, cada fila con 3 casillas vacías.
        # Se usa una comprensión de listas para que cada fila sea una lista
        # independiente (ver explicación abajo).
        self.grid = [[self.EMPTY for _ in range(3)] for _ in range(3)]

    # ------------------------------------------------------------------
    # Consultas sobre el estado
    # ------------------------------------------------------------------
    def reset(self):
        """Deja el tablero vacío para empezar una partida nueva."""
        self.grid = [[self.EMPTY for _ in range(3)] for _ in range(3)]

    def get_cell(self, row, col):
        """Devuelve lo que hay en una casilla: 'X', 'O' o ' '."""
        return self.grid[row][col]

    def is_valid_move(self, move):
        """
        Un movimiento es válido si:
        1) la casilla existe (fila y columna entre 0 y 2), y
        2) está vacía.
        """
        row, col = move
        if not (0 <= row < 3 and 0 <= col < 3):
            return False
        return self.grid[row][col] == self.EMPTY

    def get_available_moves(self):
        """Devuelve la lista de casillas libres, p. ej. [(0, 0), (0, 1), ...]."""
        moves = []
        for row in range(3):
            for col in range(3):
                if self.grid[row][col] == self.EMPTY:
                    moves.append((row, col))
        return moves

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def make_move(self, move, player):
        """
        Coloca la ficha de 'player' en 'move' si es válido.
        Devuelve True si se hizo la jugada y False si no.
        """
        if not self.is_valid_move(move):
            return False
        row, col = move
        self.grid[row][col] = player
        return True

    def undo_move(self, move):
        """
        BACKTRACKING: deshace una jugada vaciando la casilla.
        Devuelve True si deshizo algo y False si no había nada que
        deshacer (casilla fuera del tablero o ya vacía).
        """
        row, col = move
        if not (0 <= row < 3 and 0 <= col < 3):
            return False
        if self.grid[row][col] == self.EMPTY:
            return False
        self.grid[row][col] = self.EMPTY
        return True    

    # Fin de partida

    def check_winner(self, player):
        """¿Ha ganado 'player'? Revisa filas, columnas y diagonales."""
        g = self.grid

        # Las 3 filas
        for row in range(3):
            if g[row][0] == g[row][1] == g[row][2] == player:
                return True

        # Las 3 columnas
        for col in range(3):
            if g[0][col] == g[1][col] == g[2][col] == player:
                return True

        # Las 2 diagonales
        if g[0][0] == g[1][1] == g[2][2] == player:
            return True
        if g[0][2] == g[1][1] == g[2][0] == player:
            return True

        return False

    def is_full(self):
        """¿No queda ninguna casilla libre?"""
        return len(self.get_available_moves()) == 0

    def is_draw(self):
        """Empate: tablero lleno y nadie ganó."""
        return self.is_full() and not self.check_winner('X') and not self.check_winner('O')

    def get_winner(self):
        """Devuelve 'X', 'O' o None si todavía no hay ganador."""
        if self.check_winner('X'):
            return 'X'
        if self.check_winner('O'):
            return 'O'
        return None

    def is_game_over(self):
        """La partida termina si alguien ganó o el tablero se llenó."""
        return self.get_winner() is not None or self.is_full()

    # ------------------------------------------------------------------
    # Utilidad para depuración en consola
    # ------------------------------------------------------------------
    def __str__(self):
        """Permite hacer print(tablero) y ver el tablero dibujado en texto."""
        filas = []
        for row in self.grid:
            filas.append(" " + " | ".join(row))
        return "\n---+---+---\n".join(filas)