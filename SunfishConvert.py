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
	for move in con:
		sub = re.findall(r"[A-z]+\d", move)
		rv.extend(sub)
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

def convert_position(position):
	'''
	Turns algebraic notation into an integer value representing
	the same position on the board
	'''
	parts = list(position)
	horizontal = LETTERS.index(parts[0]) + 1
	vertical = 10 * int(parts[1])
	pos = horizontal + vertical
	return(pos)

class piece(object):
	def __init__(self, label, past_moves, current_pos, movements, 
		unlimited, player):

		self.label = label #Name of the piece
		self.past_moves = past_moves #Integer
		self.current_pos = current_pos #Tuple with algebraic notation and integer
		self.movements = movements #List of movements the piece can make
		self.unlimited = unlimited #Boolean
		self.player = player #String 

def create_knights():
	movements = [19, 21, 8, 12, -19, -21, -8, -12]

	knight1White = piece("N", 0, ("b1", 12), movements, False, "White")
	knight2White = piece("N", 0, ("g1", 17), movements, False, "White")
	knight1Black = piece("N", 0, ("b8", 82), movements, False, "Black")
	knight2Black = piece("N", 0, ("g8", 87), movements, False, "Black")

	return [knight1White, knight2White, knight2Black, knight1Black]

def create_rooks():
	movements = UP + DOWN + SIDE

	rook1White = piece("R", 0, ("a1", 11), movements, True, "White")
	rook2White = piece("R", 0, ("h1", 18), movements, True, "White")
	rook1Black = piece("R", 0, ("a8", 81), movements, True, "Black")
	rook2Black = piece("R", 0, ("h8", 88), movements, True, "Black")

	return [rook1White, rook1Black, rook2White, rook2Black]

def create_bishops():
	movements = DIAGONAL
	bishop1White = piece("B", 0, ("c1", 13), movements, True, "White")
	bishop2White = piece("B", 0, ("f1", 16), movements, True, "White")
	bishop1Black = piece("B", 0, ("c8", 83), movements, True, "Black")
	bishop2Black = piece("B", 0, ("f8", 86), movements, True, "Black")

	return [bishop1White, bishop2White, bishop1Black, bishop2Black]

def create_pawns():
	movements = UP

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

	kingWhite = piece("K", 0, ("e1", 15), FREE_MOVEMENT, False, "White")
	kingBlack = piece("K", 0, ("e8", 85), FREE_MOVEMENT, False, "Black")
	return [kingWhite, kingBlack]

def create_queens():
	
	queenWhite = piece("Q", 0, ("d1", 14), FREE_MOVEMENT, True, "White")
	queenBlack = piece("Q", 0, ("d8", 84), FREE_MOVEMENT, True, "Black")
	return [queenWhite, queenBlack]

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
			board.append(piece("Q", piece.past_moves, piece.current_pos, FREE_MOVEMENT, True, piece.player))
			board.remove(piece)
			return(sunfish_move)


def convert_string(take, turn, board):

	players = ["White", "Black"]
	current_player = players[turn%2]

	for position in take:
		'''
		Check to see if the piece is a pawn. 
		Assumes that the string will distinguish non-pawns.
		This section standardizes the string
		'''
		if len(position) == 2:
			check = "P"
			point = convert_position(position)
		if len(position) == 3:
			check = position[0]
			position = position[1:3]
			point = convert_position(position)

		if len(position) == 4:
			'''
			Checks to find pawn promotion.
			Assumes pawn promotion is written in the a7=Q format
			'''
			if position[-1] == "Q":
				return(pawn_to_queen(position, current_player, board))

		for piece in board:
			'''
			Iterates through pieces in a board to see which can make the given move.
			'''
			if piece.label == check and piece.player == current_player:	
				#Filters based on specified player and piece			
				coordinate = piece.current_pos[1]
				
				'''
				The next if/elif statements "reverses" the board based on player
				'''
				if piece.player == "Black":
					move = coordinate - point
				elif piece.player =="White":
					move = point - coordinate


				if piece.unlimited == False:
					'''
					If the piece has a limited number of moves, 
					look through the list of moves to see if the piece
					can make the desired move.
					'''
					if move in piece.movements:
						sunfish_move = piece.current_pos[0] + position
						piece.current_pos = (position, point)
						piece.past_moves += 1
						return(sunfish_move)
						
					elif piece.label == "P" and piece.past_moves == 0:
						#Option to move forward two spaces
						if move == 20:
							sunfish_move = piece.current_pos[0] + position
							piece.current_pos = (position, point)
							piece.past_moves += 1
							return(sunfish_move)
							

				elif piece.unlimited == True:
					'''
					This section checks moves for pieces like the queen or rooks.
					It the move is in a direction they can move in, 
					it checks for any blocking pieces
					to see if it is a possible move.
					'''
					for path in piece.movements:
						blocked = False
						if move % path == 0 and 0 < (move // path) < 10:
							if not blocked:
								for i in range(1, (move // path) + 1):
									change = i * path
									if piece.player == "White":
										test = piece.current_pos[1] + change
									elif piece.player == "Black":
										test = piece.current_pos[1] - change
									for subpiece in board:
										if subpiece != piece and subpiece.current_pos[1] == test:
											blocked = True
									sunfish_move = piece.current_pos[0] + position
									piece.current_pos = (position, test)
									return(sunfish_move)							

	return(converted_moves)

def test(old_positions):
	'''
	Will be the main function
	Prepares and separates the string
	Goes through list of moves and converts to sunfish
	'''
	take = isolate_string(old_positions)
	print(take)
	board = create_pawns()
	board.extend(create_knights())
	board.extend(create_bishops())
	board.extend(create_queens())
	board.extend(create_kings())
	board.extend(create_rooks())

	converted_moves = []
	turn = 0
	for move in take:
		converted_moves.append(convert_string([move], turn, board))
		turn += 1
	return converted_moves





