from model.game_model import Board

tablero = Board()

print("1) Tablero vacío:")
print(tablero)
print("Jugadas disponibles:", len(tablero.get_available_moves()), "(esperado: 9)")

print("\n2) Jugada válida y jugada en casilla ocupada:")
print("X en (1,1):", tablero.make_move((1, 1), 'X'), "(esperado: True)")
print("O en (1,1):", tablero.make_move((1, 1), 'O'), "(esperado: False)")
print("O en (5,5):", tablero.make_move((5, 5), 'O'), "(esperado: False)")

print("\n3) Victoria por fila:")
t = Board()
t.make_move((0, 0), 'X')
t.make_move((0, 1), 'X')
t.make_move((0, 2), 'X')
print(t)
print("¿Ganó X?", t.check_winner('X'), "(esperado: True)")
print("¿Ganó O?", t.check_winner('O'), "(esperado: False)")

print("\n4) Victoria por columna:")
t = Board()
for f in range(3):
    t.make_move((f, 2), 'O')
print("¿Ganó O?", t.check_winner('O'), "(esperado: True)")

print("\n5) Victoria por diagonal:")
t = Board()
t.make_move((0, 0), 'X')
t.make_move((1, 1), 'X')
t.make_move((2, 2), 'X')
print("¿Ganó X?", t.check_winner('X'), "(esperado: True)")

print("\n6) Empate:")
t = Board()
#  X O X
#  X O O
#  O X X
jugadas = [
    ((0, 0), 'X'), ((0, 1), 'O'), ((0, 2), 'X'),
    ((1, 0), 'X'), ((1, 1), 'O'), ((1, 2), 'O'),
    ((2, 0), 'O'), ((2, 1), 'X'), ((2, 2), 'X'),
]
for mov, jug in jugadas:
    t.make_move(mov, jug)
print(t)
print("¿Empate?", t.is_draw(), "(esperado: True)")
print("¿Terminó?", t.is_game_over(), "(esperado: True)")
print("Ganador:", t.get_winner(), "(esperado: None)")