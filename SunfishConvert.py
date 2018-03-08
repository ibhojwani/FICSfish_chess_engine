
import re

given = "1. e4 c5 2. f4 e6 3. Nf3 Nc6 4. d3 d5 \
5. e5 Qa5+ 6. c3 Nh6 7. Be2 Be7 8. O-O O-O 9. Re1 Qb6 10. \
Nbd2 c4+ 11. d4 Nf5 12. Nf1 Bd7 13. g4 Nh4 14. Kh1 Nxf3 15. \
Bxf3 Bh4 16. Re2 Rad8 17. Rg2 a6 18. Ng3 Ne7 19. \
Nh5 Qa5 20. Bd2 Qb5 21. Be1 Bxe1 \ 22. Qxe1 h6 23. g5 hxg5 24. \
Rxg5 Ng6 25. Qg3 Qxb2 26. Rg1 Qxc3 27. Nf6+ gxf6 28. Rxg6+ \
fxg6 29. Qxg6+ Kh8 30. Qh6# {Black checkmated} 1-0"

desired = ["e2e4", "c7c5", "f2f4", "e7e6", "g1f3", "b8c6", "d2d3", "d7d5", \
"e4e5", "d8a5", "c2c3", "g8h6", "f1e2", "f8e7", "e1g1", "e8g8", "f1e1", "a5b6",\
"b1d2", "c5c4", "d3d4", "h6f5", "d2f1", "c8d7", "g2g4", "f5h4", "g1h1",\
"h4f3", "e2f3", "e7h4", "e1e2", "a8d8", "e2g2", "a7a6", "f1g3", "c6e7",\
"g3h5", "b6a5", "c1d2", "a5b5", "d2e1", "h4e1", "d1e1", "h7h6", "g4g5", "h6g5",\
"g2g5", "e7g6", "e1g3", "b5b2", "a1g1", "b2c3", "h5f6", "g7f6", "g5g6",\
"f7g6", "g3g6", "g8h8", "g6h6"]

LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h"]
DIAGONAL = [9, 11, -9, -11]
UP = [10]
DOWN = [-10]
SIDE = [-1, 1]
FREE_MOVEMENT = DIAGONAL + UP + DOWN + SIDE

'''
NOTE:
Castling still not fully functional. I removed it from the git added version to not clutter the screen.
It should be done by the end of today or tomorrow.

INTEGER BOARD 

 81 82 83 84 85 86 87 88
 71 72 73 74 75 76 77 78 
 61 62 63 64 65 66 67 68
 51 52 53 54 55 56 57 58
 41 42 43 44 45 46 47 48 
 31 32 33 34 35 36 37 38
 21 22 23 24 25 26 27 28
 11 12 13 14 15 16 17 18
'''

def isolate_string(string):
	'''
	Turns inputted string into a list of just the moves
	'''
	con = string.split(".")
	rv = []
	for section in con:
		move = re.findall(r"[A-z]+\d|O-O|O-O-O", section)
		rv.extend(move)
	return(rv)

def divide_players():
	'''
	Given a list of moves it divides it by who played each move. 
	Not used in the conversion
	'''
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

def alg_to_int(position):
	'''
	Turns algebraic notation into an integer value representing
	the same position on the board
	'''
	parts = list(position)
	horizontal = LETTERS.index(parts[0]) + 1
	vertical = 10 * int(parts[1])
	pos = horizontal + vertical
	return(pos)

def int_to_alg(coordinate):
	row = str(coordinate // 10)
	column_index = coordinate % 10
	column = LETTERS[column_index - 1]
	return column + row

class Piece(object):
	def __init__(self, label, past_moves, current_pos, movements, 
		unlimited, player):

		self.label = label #Name of the piece
		self.past_moves = past_moves #Integer
		self.current_pos = current_pos #Tuple with algebraic notation and integer
		self.movements = movements #List of movements the piece can make
		self.unlimited = unlimited #Boolean
		self.player = player #String 

def create_piece(label, position, movements, unlimited):
	pieces = []
	i = 0
	for slot in position:
		if i % 2 == 0:
			white = Piece(label, 0, slot, movements, unlimited, "White")
			pieces.append(white)
			i += 1
		elif i %2 == 1:
			black = Piece(label, 0, slot, movements, unlimited, "Black")
			pieces.append(black)
			i += 1
	return(pieces)

def create_knights():
	movements = [19, 21, 8, 12, -19, -21, -8, -12]
	positions = [("b1", 12), ("b8", 82), ("g1", 17), ("g8", 87)]

	return create_piece("N", positions, movements, False)

def create_rooks():
	movements = UP + DOWN + SIDE
	positions = [("a1", 11), ("a8", 81), ("h1", 18), ("h8", 88)]

	return create_piece("R", positions, movements, True)


def create_bishops():
	positions = [("c1", 13), ("c8", 83), ("f1", 16), ("f8", 86)]

	return create_piece("B", positions, DIAGONAL, True)


def create_pawns():
	positions = [("a2", 21), ("a7", 71), ("b2", 22), ("b7", 72), ("c2", 23), ("c7", 73), ("d2", 24), \
	("d7", 74), ("e2", 25), ("e7", 75), ("f2", 26), ("f7", 76), ("g2", 27), ("g7", 77), ("h2", 28),("h7", 78)]

	return create_piece("P", positions, UP, False)


def create_kings():
	positions = [("e1", 15), ("e8", 85)]
	return create_piece("K", positions, FREE_MOVEMENT, False)

def create_queens():
	positions = [("d1", 14), ("d8", 84)]
	return create_piece("Q", positions, FREE_MOVEMENT, True)

def create_board():
	board = []
	board.extend(create_pawns())
	board.extend(create_rooks())
	board.extend(create_knights())
	board.extend(create_bishops())
	board.extend(create_kings())
	board.extend(create_queens())
	return(board)


def pawn_to_queen(new_space, player, board):
	'''
	Promotes a pawn to a queen
	'''
	if new_space[1] == "8":
		add = "7"
	elif new_space[1] == "1":
		add = "2"
	prev_pos = new_space[0] + add
	sunfish_move = prev_pos + new_space
	for piece in board:
		if piece.player == player and piece.label == "P" and piece.current_pos[0] == prev_pos:
			board.append(Piece("Q", piece.past_moves, piece.current_pos, FREE_MOVEMENT, True, piece.player))
			board.remove(piece)
			return(sunfish_move)

def castling(castle, player, board):
	rooks = []
	rook = ""
	for piece in board:
		if piece.player == player:
			if piece.label == "K":
				king = piece
				board.remove(piece)
			elif piece.label == "R":
				if castle == "O-O" and piece.current_pos[0][0] == "h":
					rook = piece
					board.remove(piece)
				elif castle =="O-O-O" and piece.current_pos[0][0] == "a":
					rook = piece
					board.remove(piece)

	if player == "White":
		if castle == "O-O":
			sunfish_move = "e1g1"
			king.current_pos = ("g1", 17)
			king.past_moves += 1
			rook.current_pos = ("f1", 16)
			rook.past_moves += 1

		elif castle == "O-O-O":
			sunfish_move = "e1c1"
			king.current_pos = ("c1", 12)
			king.past_moves += 1
			rook.current_pos = ("d1", 13)
			rook.past_moves += 1
	elif player == "Black":
		if castle == "O-O":
			sunfish_move = "e8g8"
			king.current_pos = ("g8", 87)
			king.past_moves += 1
			rook.current_pos = ("f8", 86)
			rook.past_moves += 1
		elif castle == "O-O-O":
			sunfish_move = "e8c8"
			king.current_pos = ("c8", 82)
			king.past_moves += 1
			rook.current_pos = ("d8", 83)
			rook.past_moves += 1

	board.append(king)
	board.append(rook)
	return(sunfish_move)

def strip_move(move, board):
	name = "P"
	row = None
	if len(move) == 2:
		return move, name, row
	elif len(move) == 3:
		name  = move[0]
		position =  move[1:3]
		return position, name, row

	elif len(move) == 4:		
		if move[1] == "x":
			if move[0].isupper():
				name = move[0]
				position = move[2:4]
				capture(position, board)
				return position, name, row
			else:
				row = move[0]
				position = move[2:4]
				capture(position, board)
				return position, name, row
		else:
			name = move[0]
			position = move[2:4]
			row = move[1]
			return position, name, row
	elif len(move) == 5:
		name = move[0]
		row = move[1]
		position = move[3:5]
		capture(position, board)
		return position, name, row

def capture(position, board):
	for piece in board:
		if piece.current_pos[0] == position:
			board.remove(piece)


def convert_string(move, turn, board):

	players = ["White", "Black"]
	current_player = players[turn%2]
	name = "P"
	point = 0

	if move == "O-O" or move == "O-O-O":
		return(castling(move, current_player, board))
	'''
	name to see if the piece is a pawn. 
	Assumes that the string will distinguish non-pawns.
	This section standardizes the string
	'''
	position, name, row = strip_move(move, board)
	point = alg_to_int(position)

	if len(move) == 4:
		'''
		NOTE: name different string endings
		MAY NOT END WITH LETTER
		Checks to find pawn promotion.
		Assumes pawn promotion is written in the a7=Q format
		'''
		if move[-1] == "Q":
			return(pawn_to_queen(move, current_player, board))

	for piece in board:
		'''
		Iterates through pieces in a board to see which can make the given move.
		'''
		if piece.label == name and piece.player == current_player:
			if row and piece.current_pos[0][0] != row:
				pass
			else:
				#Filters based on specified player and piece			
				coordinate = piece.current_pos[1]
				
				'''
				The next if/elif statements "reverses" the board based on player
				'''
				if piece.player == "Black":
					movement = coordinate - point
				elif piece.player =="White":
					movement = point - coordinate

				if piece.unlimited == False:
					'''
					If the piece has a limited number of moves, 
					look through the list of moves to see if the piece
					can make the desired move.
					'''
					if movement in piece.movements:
						sunfish_move = piece.current_pos[0] + position
						piece.current_pos = (position, point)
						piece.past_moves += 1
						return(sunfish_move)
						
					elif piece.label == "P":
						#Option to move forward two spaces
						if movement == 20 and piece.past_moves == 0:
							sunfish_move = piece.current_pos[0] + position
							piece.current_pos = (position, point)
							piece.past_moves += 1
							return(sunfish_move)
						elif move[1] == "x":
							if movement == 9 or movement == 11:
								sunfish_move = piece.current_pos[0] + position
								piece.current_pos = (position, point)
								piece.past_moves += 1
								return(sunfish_move)
							

				elif piece.unlimited == True:
					for factor in piece.movements:
						blocked = False
						test = 0
						if movement % factor == 0 and (movement // factor) < 10:
							if (movement // factor) < 0:
								factor *= -1
							for i in range(1, (movement // factor) +1):
								change = i * factor

								if piece.player == "White":
									test = piece.current_pos[1] + change
								elif piece.player == "Black":
									test = piece.current_pos[1] - change
								for subpiece in board:
									if subpiece != piece and subpiece.current_pos[1] == test:
										blocked = True
									
							if not blocked:
								sunfish_move = piece.current_pos[0] + position
								piece.current_pos = (position, test)
								return(sunfish_move)							

def test(old_positions):
	'''
	Will be the main function
	Prepares and separates the string
	Goes through list of moves and converts to sunfish
	'''
	take = isolate_string(old_positions)
	board = create_board()

	converted_moves = []
	turn = 0
	for move in take:
		converted_moves.append(convert_string(move, turn, board))
		turn += 1

	return converted_moves
	#return board

def played_board(old_positions):
	take = isolate_string(old_positions)
	board = create_board()
	turn = 0

	for move in take:
		convert_string(move, turn, board)
		turn += 1

	return board

def test2(st, board):
	x = convert_string(st, 0, board)
	print(x)

def check(old_positions):
	base = isolate_string(old_positions)
	cm = test(old_positions)
	check = []
	for i in range(0, len(cm)):
		if cm[i] == desired[i]:
			pass
		else:
			check.append((False))

	print(check)
