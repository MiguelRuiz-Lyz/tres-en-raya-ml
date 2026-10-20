"""
CONTROLADOR - Acumulador de métricas de la IA.

Guarda cuántas jugadas hizo la IA y cuántos nodos y milisegundos
gastó, para mostrar promedios y la jugada más lenta.
No dibuja nada ni conoce las reglas del juego: solo suma y promedia.
"""


class MetricsTracker:

    def __init__(self):
        self.reset()

    def reset(self):
        """Borra todo lo acumulado."""
        self.moves = 0
        self.total_nodes = 0
        self.total_ms = 0.0
        self.max_ms = 0.0

    def record(self, nodes, ms):
        """Registra la jugada de una IA: nodos explorados y milisegundos."""
        self.moves += 1
        self.total_nodes += nodes
        self.total_ms += ms
        self.max_ms = max(self.max_ms, ms)

    @property
    def avg_nodes(self):
        return self.total_nodes / self.moves if self.moves else 0.0

    @property
    def avg_ms(self):
        return self.total_ms / self.moves if self.moves else 0.0