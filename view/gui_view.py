"""
Interfaz gráfica con Tkinter.
DIBUJA el tablero y los paneles de métricas
avisa al controlador cuando el usuario hace clic.
"""

import tkinter as tk


class GameView:
    """Ventana principal del juego."""

    # (texto que ve el usuario, código interno que recibe el controlador)
    MODES = [
        ("Humano vs Humano", "hvh"),
        ("Humano vs IA Minimax", "minimax"),
        ("Humano vs IA Machine Learning", "ml"),
    ]

    # Colores de las fichas (decoración, no lógica)
    COLORS = {'X': '#1f6feb', 'O': '#d1242f'}

    def __init__(self, root):
        self.root = root
        self.root.title("Tres en Raya - Minimax vs Árbol de Decisión")
        self.root.minsize(640, 520)

        # "Ranuras" que el controlador llenará en el Día 4.
        self.on_cell_click = None    # función(fila, columna)
        self.on_mode_change = None   # función(codigo_de_modo)
        self.on_reset = None         # función()

        # Variables enlazadas a etiquetas: al cambiarlas, el texto se actualiza solo.
        self.mode_var = tk.StringVar(value="hvh")
        self.status_var = tk.StringVar(value="Bienvenido. Elige un modo y juega.")
        self.score_var = tk.StringVar(value="X: 0   O: 0   Empates: 0")
        self.nodes_var = tk.StringVar(value="—")
        self.time_var = tk.StringVar(value="—")
        self.summary_var = tk.StringVar(value="—")

        self.cells = []  # matriz 3x3 de botones
        self._build_layout()

    # ------------------------------------------------------------------
    # Construcción de la ventana
    # ------------------------------------------------------------------
    def _build_layout(self):
        # La ventana se divide en 2 columnas: tablero (ancha) y panel lateral.
        # 'weight' indica cuánto espacio extra recibe cada una al agrandar la
        # ventana: así la interfaz es responsiva.
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_board()
        self._build_side_panel()

    def _build_board(self):
        board_frame = tk.Frame(self.root, padx=10, pady=10)
        board_frame.grid(row=0, column=0, sticky="nsew")

        for i in range(3):
            board_frame.rowconfigure(i, weight=1)
            board_frame.columnconfigure(i, weight=1)

        for row in range(3):
            fila_botones = []
            for col in range(3):
                btn = tk.Button(
                    board_frame,
                    text="",
                    font=("Helvetica", 36, "bold"),
                    width=3,
                    # r=row, c=col "congela" los valores de este botón.
                    command=lambda r=row, c=col: self._cell_clicked(r, c),
                )
                btn.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
                fila_botones.append(btn)
            self.cells.append(fila_botones)

    def _build_side_panel(self):
        side = tk.Frame(self.root, padx=10, pady=10)
        side.grid(row=0, column=1, sticky="nsew")

        # Panel 1: modo de juego
        mode_box = tk.LabelFrame(side, text="Modo de juego", padx=8, pady=6)
        mode_box.pack(fill="x", pady=(0, 10))
        for texto, codigo in self.MODES:
            tk.Radiobutton(
                mode_box,
                text=texto,
                value=codigo,
                variable=self.mode_var,
                command=self._mode_changed,
                anchor="w",
            ).pack(fill="x")

        # Panel 2: estado de la partida
        status_box = tk.LabelFrame(side, text="Estado", padx=8, pady=6)
        status_box.pack(fill="x", pady=(0, 10))
        tk.Label(status_box, textvariable=self.status_var,
                 wraplength=200, justify="left",
                 font=("Helvetica", 11, "bold")).pack(fill="x")
        tk.Label(status_box, textvariable=self.score_var,
                 anchor="w").pack(fill="x", pady=(6, 0))

        # Panel 3: métricas de la IA
        metrics_box = tk.LabelFrame(side, text="Métricas de la IA", padx=8, pady=6)
        metrics_box.pack(fill="x", pady=(0, 10))
        tk.Label(metrics_box, text="Nodos explorados:", anchor="w").pack(fill="x")
        tk.Label(metrics_box, textvariable=self.nodes_var, anchor="w",
                 font=("Helvetica", 12, "bold")).pack(fill="x")
        tk.Label(metrics_box, text="Tiempo de respuesta:", anchor="w").pack(fill="x")
        tk.Label(metrics_box, textvariable=self.time_var, anchor="w",
                 font=("Helvetica", 12, "bold")).pack(fill="x")

        tk.Label(metrics_box, text="Acumulado de la IA:", anchor="w").pack(
            fill="x", pady=(6, 0))
        tk.Label(metrics_box, textvariable=self.summary_var, anchor="w",
                 justify="left").pack(fill="x")

        # Botón de nueva partida
        tk.Button(side, text="Nueva partida", command=self._reset_clicked,
                  pady=6).pack(fill="x")

    # ------------------------------------------------------------------
    # Eventos internos: solo reenvían el aviso al controlador
    # ------------------------------------------------------------------
    def _cell_clicked(self, row, col):
        if self.on_cell_click:
            self.on_cell_click(row, col)

    def _mode_changed(self):
        if self.on_mode_change:
            self.on_mode_change(self.mode_var.get())

    def _reset_clicked(self):
        if self.on_reset:
            self.on_reset()

    # ------------------------------------------------------------------
    # Métodos que el CONTROLADOR usará para ordenarle cosas a la vista
    # ------------------------------------------------------------------
    def set_cell(self, row, col, symbol):
        """Dibuja 'X' u 'O' en una casilla."""
        color = self.COLORS.get(symbol, "black")
        self.cells[row][col].config(text=symbol, fg=color, disabledforeground=color)

    def clear_board(self):
        """Vacía todas las casillas y las vuelve a habilitar."""
        for fila in self.cells:
            for btn in fila:
                btn.config(text="", state=tk.NORMAL)

    def set_board_enabled(self, enabled):
        """Habilita o bloquea los botones (p. ej. al terminar la partida)."""
        estado = tk.NORMAL if enabled else tk.DISABLED
        for fila in self.cells:
            for btn in fila:
                btn.config(state=estado)

    def set_status(self, text):
        self.status_var.set(text)

    def set_score(self, x_wins, o_wins, draws):
        self.score_var.set(f"X: {x_wins}   O: {o_wins}   Empates: {draws}")

    def set_metrics(self, nodes, time_ms):
        """Muestra nodos explorados y tiempo en milisegundos."""
        self.nodes_var.set(f"{nodes:,}")
        self.time_var.set(f"{time_ms:.2f} ms")

    def clear_metrics(self):
        self.nodes_var.set("—")
        self.time_var.set("—")

    def set_metrics_summary(self, moves, avg_nodes, avg_ms, max_ms):
        """Muestra el resumen acumulado de la IA."""
        self.summary_var.set(
            f"Jugadas de la IA: {moves}\n"
            f"Promedio: {avg_nodes:,.0f} nodos, {avg_ms:.2f} ms\n"
            f"Más lenta: {max_ms:.2f} ms"
        )

    def clear_metrics_summary(self):
        self.summary_var.set("—")

    def get_mode(self):
        return self.mode_var.get()

    def refresh(self):
        """Fuerza el repintado de la ventana (útil antes de un cálculo largo)."""
        self.root.update_idletasks()    

    def run(self):
        """Arranca la ventana y espera eventos (clics, etc.)."""
        self.root.mainloop()