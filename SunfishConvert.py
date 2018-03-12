'''
CS 122
Ginormous Anteaters

This code is meant to convert the algebraic notation used in FICS
into coordinate notation, as well as create a modified chess board
given a series of moves

The chess board is represented by a list of objects from the
Piece class and will be used to call a best move from Sunfish 
in case of limited practical data. 

Sunfish is an open source chess engine written by Thomas Ahle and any
references to the Sunfish program are entirely his. 

Author: Catalina Raggi
'''
import re

''' 
This code uses integer representations for squares on a chess board to calculate movements
as well as the common a-h, 1-8 notation.

8   81 82 83 84 85 86 87 88
7   71 72 73 74 75 76 77 78
6   61 62 63 64 65 66 67 68
5   51 52 53 54 55 56 57 58
4   41 42 43 44 45 46 47 48
3   31 32 33 34 35 36 37 38
2   21 22 23 24 25 26 27 28
1   11 12 13 14 15 16 17 18

    a  b  c  d  e  f  g  h
'''

LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h"]
KNIGHT_MOVEMENT = [19, 21, 8, 12, -19, -21, -8, -12]
DIAGONAL = [9, 11, -9, -11] 
UP = [10]
DOWN = [-10]
SIDE = [-1, 1]
FREE_MOVEMENT = DIAGONAL + UP + DOWN + SIDE

def isolate_string(string):
    '''
    Turns inputted string of moves and number of turns 
    into a list of just the moves

    Explanation of re string:

    [A-z]: look for the starting letters (either starting column
    or piece label)

    \d: find the column number being moved into

    The second call for [A-z] is to find en passant moves, which
    come in the form column+capture+new_location+e.p.
    EX:hxg6e.p.

    The = is considered to check for pawn promotions, which come
    in the form column+row+=+label_of_piece_promoted_to
    EX: e8=Q

    Castling is notated as "O-O" or "O-O-O"

    Inputs: 
        string: a string of moves

    Returns:
        A list of strings
    '''
    return re.findall(r"[A-z]+\d+[A-z]*=*[A-z]*|O-O|O-O-O", string)


def alg_to_int(position):
    '''
    Turns algebraic notation into an integer value representing
    the same position on the board
    EX. An input of a1 would return the integer 11

    Inputs:
        position: a string representing a square on the chess board

    Returns:
        An integer representation of a square on the chess board
    '''
    parts = list(position)
    horizontal = LETTERS.index(parts[0]) + 1
    vertical = 10 * int(parts[1])
    pos = horizontal + vertical
    return(pos)


def int_to_alg(coordinate):
    '''
    Turns an integer coordinate into the algebraic notation
    of the same square on a board
    EX. An input of 88 would return the string h8

    Inputs:
        coordinate: an integer

    Returns:
        A string representing a square on the chess board
    '''
    row = str(coordinate // 10)
    column_index = coordinate % 10
    column = LETTERS[column_index - 1]
    return column + row


class Piece(object):
    '''
    This class represents the pieces on the board.
    Each instance of this class is one piece.
    '''
    def __init__(self, label, past_moves, current_pos, movements, 
        unlimited, player):

        self.label = label #Name of the piece
        self.past_moves = past_moves #Integer
        self.current_pos = current_pos #Tuple with algebraic notation and integer
        self.movements = movements #List of movements the piece can make
        self.unlimited = unlimited #Boolean
        self.player = player #String 


def create_piece(label, position, movements, unlimited):
    '''
    Creates the pieces needed for the starting board.

    Inputs:
        label: The label attribute of the piece
        position: A list of starting squares for the pieces,
        will alternate sides of the board starting with the white side
        movements: The possible moves for the piece type
        unlimited: A boolean saying whether the pawn has unlimited moves

    Returns:
        A list of pieces
    '''
    pieces = [] 
    i = 0 #Alternate between creating White and Black pieces
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


'''
FUNCTIONS TO CREATE BOARD
'''


def create_knights():
    '''
    Creates the four knight pieces for the starting board as a list
    '''
    movements = KNIGHT_MOVEMENT
    positions = [("b1", 12), ("b8", 82), ("g1", 17), ("g8", 87)]

    return create_piece("N", positions, movements, False)


def create_rooks():
    '''
    Creates the four rook pieces for the starting board as a list
    '''
    movements = UP + DOWN + SIDE
    positions = [("a1", 11), ("a8", 81), ("h1", 18), ("h8", 88)]

    return create_piece("R", positions, movements, True)


def create_bishops():
    '''
    Creates the four bishop pieces for the starting board as a list
    '''
    positions = [("c1", 13), ("c8", 83), ("f1", 16), ("f8", 86)]

    return create_piece("B", positions, DIAGONAL, True)


def create_pawns():
    '''
    Creates the sixteen pawn pieces for the starting board as a list
    '''
    positions = [("a2", 21), ("a7", 71), ("b2", 22), ("b7", 72), ("c2", 23), ("c7", 73), ("d2", 24), \
    ("d7", 74), ("e2", 25), ("e7", 75), ("f2", 26), ("f7", 76), ("g2", 27), ("g7", 77), ("h2", 28),("h7", 78)]

    return create_piece("P", positions, UP, False)


def create_kings():
    '''
    Creates the two king pieces for the starting board as a list
    '''
    positions = [("e1", 15), ("e8", 85)]
    return create_piece("K", positions, FREE_MOVEMENT, False)


def create_queens():
    '''
    Creates the two queen pieces for the starting board as a list

    '''
    positions = [("d1", 14), ("d8", 84)]
    return create_piece("Q", positions, FREE_MOVEMENT, True)


def create_board():
    '''
    Creates a list of Piece objects as the starting board
    '''
    board = []
    board.extend(create_pawns())
    board.extend(create_rooks())
    board.extend(create_knights())
    board.extend(create_bishops())
    board.extend(create_kings())
    board.extend(create_queens())
    return(board)


'''
FUNCTIONS TO MODIFY BOARD
'''

def pawn_to_queen(new_space, player, label, board):
    '''
    Promotes a pawn to a given Piece type

    Inputs:
        new_space: a tuple with the space on the board
        being moved too as both a string an an integer
        EX. ("a1", 11)
        player: A string representing the current player
        label: A string representing the type of piece
        the pawn will promote to
        board: a list of pieces

    Returns:
        Modified board and the move in algebraic notation
    '''
    if new_space[1] == "8": #If white promotion
    #Find the previous position
        add = "7"
    elif new_space[1] == "1": #If black promotion
    #Find previous position
        add = "2"

    prev_pos = new_space[0] + add 
    sunfish_move = prev_pos + new_space
    return(sunfish_move)

    for piece in board:
    #Look for the pawn being promoted and promote
        if piece.player == player and piece.label == "P" and piece.current_pos[0] == prev_pos:
            if label == "Q":
                board.append(Piece("Q", piece.past_moves, piece.current_pos, FREE_MOVEMENT, True, piece.player))                
            elif label == "N":
                board.append(Piece("N", piece.past_moves, piece.current_pos, KNIGHT_MOVEMENT, False, piece.player))
            elif label == "R":
                movement = UP + DOWN + SIDE
                board.append(Piece("R", piece.past_moves, piece.current_pos, movement, True, piece.player))
            elif label == "B":
                board.append(Piece("B", piece.past_moves, piece.current_pos, DIAGONAL, True, piece.player))
            board.remove(piece)
            return(sunfish_move)


def castling(castle, player, board):
    '''
    This function allows for the castling move.
    It looks for the king and rook being moved and then moves
    them to their new locations.

    Inputs:
        castle: A string representing the type of castling
        EX. O-O or O-O-O
        player: A string representing the current player
        board: a list of Piece items

    Returns:
        A modified board and the move in coordinate notation
    '''
    rook = ""
    for piece in board:
    #Look for the pieces being moved
        if piece.player == player:
            if piece.label == "K": #Create copy and remove original
                king = piece
                board.remove(piece)
            elif piece.label == "R":
                if castle == "O-O" and piece.current_pos[0][0] == "h":
                #Finds the rook being moved
                    rook = piece
                    board.remove(piece)
                elif castle =="O-O-O" and piece.current_pos[0][0] == "a":
                    rook = piece
                    board.remove(piece)
    '''
    The next part of the code moves the king and rook based on 
    the player and the castling side.
    '''
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
    '''
    This function takes the necessary data from a given move 
    based on the length and special characteristics
    of the move string inputted.

    Inputs:
        move: A string representing a movement
        EX. Nd6, Rab1
        board: a list of Piece objects

    Returns:
        the spot being moved to, 
        label of the piece, 
        and the row filter, 
    '''
    name = "P"
    row = None
    if len(move) == 2:
    #If it's just the new position, assume pawn
        return move, name, row
    elif len(move) == 3:
    #"+" not part of move, so move must have type
    #of piece and the destination
        name  = move[0]
        position =  move[1:3]
        return position, name, row
    elif len(move) == 4:
        if move[1] == "x": #Piece is caputred
            if move[0].isupper(): #If move specifies piece type
                name = move[0]
                position = move[2:4]
                capture(position, board)
                return position, name, row
            else: #else first element must be row filter
                row = move[0]
                position = move[2:4]
                capture(position, board)
                return position, name, row
        else: #If not capture, 2nd element row filter
            name = move[0]
            position = move[2:4]
            row = move[1]
            return position, name, row
    elif len(move) == 5: 
    #Must be capture with name and row filters
    #EX, Naxd6
        name = move[0]
        row = move[1]
        position = move[3:5]
        capture(position, board)
        return position, name, row


def capture(position, board):
    '''
    Removes a Piece object at a given position
    from the board

    Inputs:
        position: a string representing a square on the board
        board: A list of Piece objects
    '''
    for piece in board: 
        if piece.current_pos[0] == position:
            board.remove(piece)


def convert_string(move, turn, board):
    '''
    Given a move in algebraic notation, this function tests to 
    see which piece can make the given move and modifies a board 
    representing the chess game.

    Inputs:
        move: a string representing the movement
        turn: an integer representing the amount of turns that have past
        this is used to calculate the current player
        board: a list of piece items

    Returns:
        Modifies a board and returns the movement in coordinate notation
    '''

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

    if move[-2] == "=": #If pawn promotion
    #Pawn promo notation is a8=Q format
        return(pawn_promo(move, current_player, move[-1], board))

    if move[-1] == "e": #If en passant
    #FICS denotes en passant with e.p.
    #Regex is only concerned with e
        row = move[0]
        last_space = ""
        new_pos = move[2:4] #move[1] must be x 
        new_coord = alg_to_int(new_pos)
        if current_player == "White":
            captured_piece = new_coord - 10
        else:
            captured_piece = new_coord + 10
        for piece in board:
            #Find pieces that meet given conditions
            if piece.current_pos[0][0] == row and piece.player == \
            current_player and piece.label == name:
            #Find attacking piece
                movement = piece.current_pos[1] - new_coord
                if movement in DIAGONAL:
                    last_space = piece.current_pos[0]
                    piece.current_pos = (new_pos, new_coord)
                    piece.past_moves += 1       
            elif piece.current_pos[1] == captured_piece:
                #Delete captured piece
                capture(captured_piece, board)

        sunfish_move = last_space + move[2:4]
        return(sunfish_move)

    position, name, row = strip_move(move, board)
    point = alg_to_int(position)

    for piece in board:
    #Go through pieces and test which can make the given move
        if piece.label == name and piece.player == current_player:
            #Check for row filter condition
            if row and piece.current_pos[0][0] != row: 
                pass
            else:
                #Filter based on specified player and piece
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
                    can make the desired move and move it if so.
                    '''
                    if movement in piece.movements:
                        sunfish_move = piece.current_pos[0] + position
                        piece.current_pos = (position, point)
                        piece.past_moves += 1
                        return(sunfish_move)
                    elif piece.label == "P": #Pawn has special moves
                        #Option to move forward two spaces 
                        #as first move of pawn
                        if movement == 20 and piece.past_moves == 0:
                            sunfish_move = piece.current_pos[0] + position
                            piece.current_pos = (position, point)
                            piece.past_moves += 1
                            return(sunfish_move)
                        elif move[1] == "x": #Special rules if pawn capture
                            if movement == 9 or movement == 11:
                                sunfish_move = piece.current_pos[0] + position
                                piece.current_pos = (position, point)
                                piece.past_moves += 1
                                return(sunfish_move)                   
                elif piece.unlimited == True:
                #Piece can move multiple squares
                    for factor in piece.movements:
                    #Check which direction it's moving in
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
                                #See if piece is blocked from moving
                                    if subpiece != piece and subpiece.current_pos[1] == test:
                                        blocked = True                        
                            if not blocked:
                            #If the movement is in the right direction
                            #and the piece is not blocked
                            #move the piece
                                sunfish_move = piece.current_pos[0] + position
                                piece.current_pos = (position, test)
                                return(sunfish_move)


def played_board(move_history):
    '''
    Creates a board represented by Piece objects from a string of moves.

    Inputs:
        move_history: a string representing a chess game

    Returns:
        A list of Piece objects representing a chess board
    '''
    take = isolate_string(move_history)
    board = create_board()
    turn = 0
    for move in take:
        convert_string(move, turn, board)
        turn += 1
    return board
