"""
Intermediario entre Modelo y Vista
Recibe los clics de la vista, consulta/actualiza el modelo,
pide a la IA su jugada y refresca la vista.

También gestiona los 3 modos: Humano vs Humano,
Humano vs Minimax y Humano vs ML.

""" 

import time
from controller.metrics import MetricsTracker

class GameController:
    HUMAN = 'X'   # En los modos contra IA, el humano juega con X
    AI = 'O'      # y la IA juega con O

    # Nombres amigables para los mensajes de estado
    MODE_NAMES = {
        "hvh": "Humano vs Humano",
        "minimax": "Humano vs IA Minimax",
        "ml": "Humano vs IA Machine Learning",
    }

    def __init__(self, board, view):
        self.board = board    # Modelo
        self.view = view      # Vista

        self.mode = view.get_mode()
        self.current_player = 'X'
        self.game_over = False
        self.scores = {'X': 0, 'O': 0, 'draw': 0}

        # Casillero de agentes de IA: {"minimax": agente, "ml": agente}.
        # Hoy está vacío; se llenará en las Semanas 2 y 3.
        self.agents = {}
        self.metrics = MetricsTracker()

        # Conectar las "ranuras" de la vista con los métodos de este controlador
        self.view.on_cell_click = self.handle_cell_click
        self.view.on_mode_change = self.handle_mode_change
        self.view.on_reset = self.handle_reset

        self._start_new_game()

    # ------------------------------------------------------------------
    # Registro de agentes (se usará en las Semanas 2 y 3)
    # ------------------------------------------------------------------
    def register_agent(self, mode, agent):
        """Asocia un agente de IA a un modo ('minimax' o 'ml')."""
        self.agents[mode] = agent

    # ------------------------------------------------------------------
    # Eventos que llegan desde la vista
    # ------------------------------------------------------------------
    def handle_cell_click(self, row, col):
        """El usuario hizo clic en una casilla."""
        if self.game_over:
            return

        # Modo contra IA sin agente disponible: avisar y no hacer nada
        if self.mode != "hvh" and self.mode not in self.agents:
            self.view.set_status(
                f"El modo '{self.MODE_NAMES[self.mode]}' aún no está "
                "disponible. Elige Humano vs Humano."
            )
            return

        # En modos contra IA, solo el humano hace clic
        if self.mode != "hvh" and self.current_player != self.HUMAN:
            return

        move = (row, col)

        # El MODELO decide si la jugada es válida, no la vista ni el controlador
        if not self.board.is_valid_move(move):
            self.view.set_status("Esa casilla está ocupada. Elige otra.")
            return

        self._play(move)

        # Si la partida sigue y se juega contra IA, le toca a la IA
        if not self.game_over and self.mode != "hvh":
            self._ai_turn()

    def handle_mode_change(self, mode):
        """El usuario eligió otro modo de juego."""
        if mode == self.mode:
            return   # Mismo modo: no hay nada que cambiar
        self.mode = mode
        # Cambiar de modo reinicia marcador y métricas, para comparar limpiamente
        self.scores = {'X': 0, 'O': 0, 'draw': 0}
        self.metrics.reset()
        self.view.clear_metrics_summary()
        self._start_new_game()

    def handle_reset(self):
        """El usuario pulsó 'Nueva partida'."""
        self._start_new_game()

    # ------------------------------------------------------------------
    # Lógica de coordinación (privada)
    # ------------------------------------------------------------------
    def _start_new_game(self):
        self.board.reset()
        self.current_player = 'X'
        self.game_over = False

        self.view.clear_board()
        self.view.clear_metrics()
        self.view.set_score(self.scores['X'], self.scores['O'], self.scores['draw'])

        if self.mode != "hvh" and self.mode not in self.agents:
            self.view.set_status(
                f"Modo '{self.MODE_NAMES[self.mode]}': IA aún no disponible."
            )
        else:
            self.view.set_status(f"Turno de {self.current_player}")

    def _play(self, move):
        """
        Aplica una jugada del jugador actual y actualiza modelo y vista.
        Devuelve True si el modelo la aceptó y False si la rechazó.
        """
        player = self.current_player

        # 1) Modelo: solo si ÉL acepta la jugada, la vista la dibuja
        if not self.board.make_move(move, player):
            return False

        # 2) Vista
        self.view.set_cell(move[0], move[1], player)

        # 3) ¿Terminó la partida? Pregunta al modelo.
        winner = self.board.get_winner()
        if winner is not None:
            self._finish_game(f"¡Ganó {winner}!", winner)
        elif self.board.is_full():
            self._finish_game("¡Empate!", 'draw')
        else:
            # 4) Cambiar de turno
            self.current_player = 'O' if player == 'X' else 'X'
            self.view.set_status(f"Turno de {self.current_player}")

        return True

    def _finish_game(self, message, result):
        self.game_over = True
        self.scores[result] += 1
        self.view.set_status(message)
        self.view.set_score(self.scores['X'], self.scores['O'], self.scores['draw'])
        self.view.set_board_enabled(False)

    def _ai_turn(self):
        """Pide una jugada al agente, mide el tiempo y la aplica."""
        agent = self.agents[self.mode]

        self.view.set_status("La IA está pensando...")   
        self.view.refresh()                              

        inicio = time.perf_counter()
        move = agent.get_move(self.board)
        elapsed_ms = (time.perf_counter() - inicio) * 1000

        nodes = getattr(agent, "nodes_evaluated", 0)
        self.view.set_metrics(nodes, elapsed_ms)

        if move is not None:                                  
            self.metrics.record(nodes, elapsed_ms)            
            self.view.set_metrics_summary(                    
                self.metrics.moves, self.metrics.avg_nodes,   
                self.metrics.avg_ms, self.metrics.max_ms,     
            )                                                 

        if move is None or not self._play(move):
            # La IA propuso algo ilegal: detenemos la partida sin desincronizar
            self.game_over = True
            self.view.set_board_enabled(False)
            self.view.set_status(
                "Error: la IA propuso una jugada inválida. Pulsa 'Nueva partida'."
            )