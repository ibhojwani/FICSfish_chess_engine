import urllib.request
import re
import SunfishConvert
import sys

# Sunfish import code taken from:
#https://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path
sys.path.insert(0, "/home/student/Downloads/sunfish-master")
import sunfish

'''
Much of this code is borrowed or modified from sunfish
'''

BLANK_BOARD = (
    '         \n'  #   0 -  9
    '         \n'  #  10 - 19
    ' ........\n'  #  20 - 29
    ' ........\n'  #  30 - 39
    ' ........\n'  #  40 - 49
    ' ........\n'  #  50 - 59
    ' ........\n'  #  60 - 69
    ' ........\n'  #  70 - 79
    ' ........\n'  #  80 - 89
    ' ........\n'  #  90 - 99
    '         \n'  # 100 -109
    '         \n'  # 110 -119
)
'''
Sunfish string-board coordinates to
SunfishConvert list-board coordinates

Sunfish: appearance and index                     Integer
		rnbqkbnr    21 22 23 24 25 26 27 28    	81 82 83 84 85 86 87 88
		pppppppp    31 32 33 34 35 36 37 38		71 72 73 74 75 76 77 78
		........    41 42 43 44 45 46 47 48		61 62 63 64 65 66 67 68
		........    51 52 53 54 55 56 57 58		51 52 53 54 55 56 57 58
		........    61 62 63 64 65 66 67 68 	41 42 43 44 45 46 47 48
		........    71 72 73 74 75 76 77 78 	31 32 33 34 35 36 37 38
		PPPPPPPP    81 82 83 84 85 86 87 88		21 22 23 24 25 26 27 28
		RNBQKBNR    91 92 93 94 95 96 97 98		11 12 13 14 15 16 17 18

The columns are numbered the same way but the rows are not. To convert,
we used the fact that the index values are the same on the fifth row
and reflected vertically to calculate the conversion formula 
index_conversion, which due to 
'''

def index_conversion(position):
	row = position // 10
		
	modifier = (row - 5) * 20
	converted_position = position - modifier
	return(converted_position)


def board_sunfish(string, next = "White"):
	board = SunfishConvert.played_board(string)
	new_board = list(BLANK_BOARD)
	for piece in board:
		place = piece.current_pos[1]
		index = index_conversion(place)
		if piece.player == next:
			representation = piece.label
		else:
			representation = piece.label.lower()
		new_board[index] = representation

	returned_board = ""
	for square in new_board:
		returned_board += square
	print(returned_board)
	return returned_board


def modified_sunfish(string):
	sunfish_board = board_sunfish(string)
	searcher = sunfish.Searcher()
	pos = sunfish.Position(sunfish_board, 0, (True,True), (True,True), 0, 0)
	move, score = searcher.search(pos, secs=2)
	integer_move_from = index_conversion(move[0])
	integer_move_to = index_conversion(move[1])
	coordinate_from = SunfishConvert.int_to_alg(integer_move_from)
	coordinate_to = SunfishConvert.int_to_alg(integer_move_to)
	best_move = coordinate_from + coordinate_to

	return(best_move)