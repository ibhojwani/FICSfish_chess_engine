'''
CS 122
Ginormous Anteaters

Uses Sunfish to calculate best move in case of limited practical data.

Author: Catalina Raggi

Sunfish is an open source chess engine written by Thomas Ahle and any
references to the Sunfish program are entirely his. 
'''

import urllib.request
import re
import SunfishConvert
import sys

# Sunfish import code taken from:
#https://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path
sys.path.insert(0, "/home/student/122-project/122-project/sunfish-master")
import sunfish

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

Sunfish: appearance         index                SunfishConvert:Integer

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
index_conversion.
'''

def index_conversion(position):
    '''
    Converts from the Sunfish string-board coordinates to the coordinates
    used in the Piece current_pos attribute in SunfishConvert. Because 
    the boards are essentially reflected from the 51-58 row, the conversion
    works the same for both Sunfish to SunfishConvert and vice versa.

    Inputs:
    	position: an integer representing a space on one of the boards

    Returns:
    	An integer representing a space on the other board.
    '''
    row = position // 10
    	
    modifier = (row - 5) * 20
    converted_position = position - modifier
    return(converted_position)


def create_sunfish_board(string, next = "White"):
    '''
    Creates a sunfish board based on a string of moves.
    Sunfish will take this board as its starting board, so the player
    represented by uppercase letters will go first, hence the second Input
    for this function.

    Inputs:
        string: A string of moves from FICS
        next: A string "White" or "Black" that says which player is next

    Returns:
        A sunfish board represented by a string
    '''
    board = SunfishConvert.played_board(string) #Converts string of moves to end board position
    new_board = list(BLANK_BOARD) #Turns string (blank Sunfish board) to list for element reassignment
    for piece in board: #Places pieces on board
        place = piece.current_pos[1]
        index = index_conversion(place)
        if piece.player == next:
            representation = piece.label
        else:
            representation = piece.label.lower()
        new_board[index] = representation

    returned_board = "" 
    for square in new_board: #Turns list back into a string
        returned_board += square
    if next == "Black":
        returned_board = rotate_board(returned_board)
    print(returned_board)
    return returned_board


def rotate_board(string_board):
    rows = []
    for i in range(0,12):
        index_start = i * 10
        index_end = (i+1) * 10
        row = string_board[index_start:index_end]
        rows.append(row)
    rows.reverse()
    flipped_board = ""
    for row in rows:
        for square in row:
            flipped_board += square
    return flipped_board



def modified_sunfish(string, next = "White"):
    '''
    DISCLAIMER: Part of this code is borrowed or modified from sunfish
    '''
    '''
    This function takes part of the code from Sunfish's function Main
    Sunfish is given a chess board with a played history as its
    initial board as looks for the best move and the resulting score (score not needed)

    Inputs:
        string: a string representing a series of chess moves

    Returns:
        Sunfish's suggested best moves in coordinate notation
        EX e2e4
    '''
    sunfish_board = create_sunfish_board(string, next)
    searcher = sunfish.Searcher()
    pos = sunfish.Position(sunfish_board, 0, (True,True), (True,True), 0, 0)
    move, score = searcher.search(pos, secs=2) #move returned as a tuple of integers
    print(move)

    integer_move_from = index_conversion(move[0])
    integer_move_to = index_conversion(move[1])
    coordinate_from = SunfishConvert.int_to_alg(integer_move_from)
    coordinate_to = SunfishConvert.int_to_alg(integer_move_to)
    best_move = coordinate_from + coordinate_to

    return(best_move)