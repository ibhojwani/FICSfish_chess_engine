#Cat Raggi
import re

given = "1. e4 c5 2. f4 e6 3. Nf3 Nc6 4. d3 d5 \
5. e5 Qa5+ 6. c3 Nh6 7. Be2 Be7 8. O-O O-O 9. Re1 Qb6 10. \
Nbd2 c4+ 11. d4 Nf5 12. Nf1 Bd7 13. g4 Nh4 14. Kh1 Nxf3 15. \
Bxf3 Bh4 16. Re2 Rad8 17. Rg2 a6 18. Ng3 Ne7 19. \
Nh5 Qa5 20. Bd2 Qb5 21. Be1 Bxe1 22. Qxe1 h6 23. g5 hxg5 24. \
Rxg5 Ng6 25. Qg3 Qxb2 26. Rg1 Qxc3 27. Nf6+ gxf6 28. Rxg6+ \
fxg6 29. Qxg6+ Kh8 30. Qh6# {Black checkmated} 1-0"

LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h"]

def isolate_string(string):
	con = string.split(".")
	rv = []
	for move in con:
		sub = re.findall(r"[A-z]+\d", move)
		rv.extend(sub)
	return(rv)

def divide_players():
	all_moves = isolate_string()
	total = len(all_moves)
	player1 = []
	player2 = []
	for i in range(0, total):
		if i % 2 == 0:
			player1.append(all_moves[i])
		else:
			player2.append(all_moves[i])
	print("player 1")
	print(player1)
	print("player2")
	print(player2)

def convert_position(position):
	parts = list(position)
	horizontal = LETTERS.index(parts[0]) + 1
	vertical = 10 * int(parts[1])
	pos = horizontal + vertical
	return(pos)

class piece(object):
	def __init__(self, label, past_moves, current_pos, movements, 
		unlimited, player):

		self.label = label
		self.past_moves = past_moves
		self.current_pos = current_pos
		self.movements = movements
		self.unlimited = unlimited
		self.player = player

def create_knights():
	movements = [19, 21, 8, 12, -19, -21, -8, -12]

	knight1White = piece("N", 0, ("b1", 12), movements, False, "White")
	knight2White = piece("N", 0, ("g1", 17), movements, False, "White")
	knight1Black = piece("N", 0, ("b8", 82), movements, False, "Black")
	knight2Black = piece("N", 0, ("g8", 87), movements, False, "Black")

	return [knight1White, knight2White, knight2Black, knight1Black]

def create_rooks():
	movements = [1, 10]

	rook1White = piece("R", 0, ("a1", 11), movements, True, "White")
	rook2White = piece("R", 0, ("h1", 18), movements, True, "White")
	rook1Black = piece("R", 0, ("a8", 81), movements, True, "Black")
	rook2Black = piece("R", 0, ("h8", 88), movements, True, "Black")

	return [rook1White, rook1Black, rook2White, rook2Black]

def create_bishops():
	movements = [11, 9]
	bishop1White = piece("B", 0, ("c1", 13), movements, True, "White")
	bishop2White = piece("B", 0, ("f1", 16), movements, True, "White")
	bishop1Black = piece("B", 0, ("c8", 83), movements, True, "Black")
	bishop2Black = piece("B", 0, ("f8", 86), movements, True, "Black")

	return [bishop1White, bishop2White, bishop1Black, bishop2Black]

def create_pawns():
	movements = [10]

	pawn1White = piece("P", 0, ("a2", 21), movements, False, "White")
	pawn2White = piece("P", 0, ("b2", 22), movements, False, "White")
	pawn3White = piece("P", 0, ("c2", 23), movements, False, "White")
	pawn4White = piece("P", 0, ("d2", 24), movements, False, "White")
	pawn5White = piece("P", 0, ("e2", 25), movements, False, "White")
	pawn6White = piece("P", 0, ("f2", 26), movements, False, "White")
	pawn7White = piece("P", 0, ("g2", 27), movements, False, "White")
	pawn8White = piece("P", 0, ("h2", 28), movements, False, "White")

	pawn1Black = piece("P", 0, ("a7", 71), movements, False, "Black")
	pawn2Black = piece("P", 0, ("b7", 72), movements, False, "Black")
	pawn3Black = piece("P", 0, ("c7", 73), movements, False, "Black")
	pawn4Black = piece("P", 0, ("d7", 74), movements, False, "Black")
	pawn5Black = piece("P", 0, ("e7", 75), movements, False, "Black")
	pawn6Black = piece("P", 0, ("f7", 76), movements, False, "Black")
	pawn7Black = piece("P", 0, ("g7", 77), movements, False, "Black")
	pawn8Black = piece("P", 0, ("h7", 78), movements, False, "Black")

	return [pawn1White, pawn2White, pawn3White, pawn4White, 
	pawn5White, pawn6White, pawn7White, pawn8White,
	pawn1Black, pawn2Black, pawn3Black, pawn4Black,
	pawn5Black, pawn6Black, pawn7Black, pawn8Black]

def create_kings():
	movements = [1, 10, 11, 9, -1, -10, -11, -9]

	kingWhite = piece("K", 0, ("e1", 15), movements, False, "White")
	kingBlack = piece("K", 0, ("e8", 85), movements, False, "Black")
	return [kingWhite, kingBlack]

def create_queens():
	movements = [1, 10, 11, 9, -1, -10, -11, -9]
	
	queenWhite = piece("Q", 0, ("d1", 14), movements, True, "White")
	queenBlack = piece("Q", 0, ("d8", 84), movements, True, "Black")
	return [queenWhite, queenBlack]

def convert_string(old_positions):
	take = isolate_string(old_positions)
	print(take)
	pieces = create_pawns()
	pieces.extend(create_knights())
	pieces.extend(create_bishops())
	pieces.extend(create_queens())
	pieces.extend(create_kings())
	pieces.extend(create_rooks())

	converted_moves = []
	players = ["White", "Black"]
	turn = 0
	check = False

	for position in take:
		if len(position) == 2:
			point = convert_position(position)
		if len(position) > 2:
			check = position[0]
			position = position[1:3]
			point = convert_position(position)
		for piece in pieces:
			if (check == False) or (check and check == piece.label):
				if piece.player == players[turn%2]:
					coordinate = piece.current_pos[1]
					if piece.player == "Black":
						move = coordinate - point
					elif piece.player =="White":
						move = point - coordinate

					if piece.unlimited == False:
						if move in piece.movements:
							sunfish_move = piece.current_pos[0] + position
							piece.current_pos = (position, point)
							converted_moves.append(sunfish_move)
							piece.past_moves += 1
							turn += 1
							check = False
							break
						elif piece.label == "P" and piece.past_moves == 0:
							if move == 20:
								sunfish_move = piece.current_pos[0] + position
								piece.current_pos = (position, point)
								converted_moves.append(sunfish_move)
								piece.past_moves += 1
								turn += 1
								check = False
								break

									

	return(converted_moves)

def num_to_string(coordinate):
	row = str(coordinate // 10)
	letter_i = coordinate % 10
	letter = LETTERS[letter_i - 1]

	return(letter+row)



