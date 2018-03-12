'''
Tranlsates algebraic notation to integer notation and vice versa.
See docstring at end for methodology and format of integer notation.
'''

import sqlite3
import re


def translate_moves_to_int(moves, ls=False):
    '''
    Parses moves. Has to be fast. Indexing is avoided as much as possible, as
    is regex, for speed. Turns all moves into a signed 2 byte integer
    representation. See doc string at end of file for details on method.
    Inputs:
        moves: string containing moves list
        ls: True if input is a list of moves
    returns list of 2 byte signed ints
    '''
    # consider switching kings and pawns?
    maps = {"K": 9000, "Q": 1000, "R": 3000, "B": 5000, "N": 7000, "P": 0,
            "a": 10, "b": 20, "c": 30, "d": 40, "e": 50, "f": 60, "g": 70,
            "h": 80, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
            "8": 8}

    if ls:
        # split move string into individual moves
        rounds = re.split(r" \w*\. ", moves[3:])
        turns = []
        for r in rounds:
            turns += r.split(" ")
    else:
        turns = [moves]
    int_turns = []

    # USE MORE DICTS for mapping?
    for turn in turns:
        orig_turn = turn

        # Castling. Nested IF to only do 1 check on all non castle moves
        if "O" in turn:
            if "O-O-O" in turn:  # castling short
                move_int = 990
            else:
                move_int = 90  # castling long

            # Checks and checkmates
            if "+" in turn:
                move_int += 1
            if "#" in turn:
                move_int += 2
            int_turns.append(move_int)
            continue

        # initializes translation int
        move_int = 0

        # Deal with pawns. In its own function due to special pawn rules re
        # pawn promotion and notation.
        try:
            if turn[0].islower():
                int_turns.append(translate_pawns_helper(move_int, turn, maps))
                continue
        except:
            print(orig_turn)
            raise
        # Deal with non-pawn pieces
        else:
            move_int += maps[turn[0]]

        # checks/checkmates
        if ("+" in turn) or ("#" in turn):
            move_int += checkmate_helper(turn)
            turn = turn[:-1]

        # destination coords
        move_int += maps[turn[-1]] + maps[turn[-2]]

        # capture and piece ident info
        if "x" in turn:  # In case of captures
            potential_ident = turn[-4]

            if potential_ident.islower():  # signals file identifier
                move_int += maps[potential_ident] * 10
            elif not potential_ident.isupper():  # signals rank identifier
                move_int += 1000 + maps[potential_ident] * 100

            move_int *= -1  # Signifies capture

        else:
            potential_ident = turn[-3]

            if potential_ident.islower():  # signals file identifier
                move_int += maps[potential_ident] * 10
            elif not potential_ident.isupper():  # signals rank identifier
                move_int += 1000 + maps[potential_ident] * 100

        int_turns.append(move_int)

    if len(int_turns) > 50:
        return int_turns[:50]

    return int_turns


def checkmate_helper(turn):
    '''
    Helper function for translate_moves_to_int() which deals with checks
    and checkmates.
    '''
    if "+" in turn:
        return 10000
    return 20000


def translate_pawns_helper(move_int, turn, maps):
    '''
    Helper function for translate_moves_to_int() which deals with pawn
    translation.
    '''
    # pawn promotion special rules. Ok if this is slower as its rare.
    # The order of if statements matters for code simplicity.
    if "=" in turn:
        move_int += 30000  # turns 10000's place to 3 for pawn promo

        # checks/checkmates
        if ("+" in turn) or ("#" in turn):
            move_int += checkmate_helper(turn) / 10
            turn = turn[:-1]

        # file identification
        move_int += maps[turn[0]] * 10 - 100

        # movement info (see doc at end of file for info)
        if turn[-3] == "1":
            move_int += 30

        # piece promoted to
        move_int += maps[turn[-1]] / 1000

        # captures and direction of capture (left or right diagonally)
        if "x" in turn:
            if turn[-4] < turn[0]:
                move_int += 10
            else:
                move_int += 20
            move_int *= -1

        return int(move_int)
        # end of pawn promotion

    # back to regular pawns
    # Check/checkmates.
    if ("+" in turn) or ("#" in turn):
        move_int += checkmate_helper(turn)
        turn = turn[:-1]

    # file identification
    move_int += maps[turn[0]] * 10

    # final coords
    move_int += maps[turn[-2]] + maps[turn[-1]]

    # captures
    if "x" in turn:
        return move_int * -1
    return move_int


def translate_int_to_move(int_turn):
    '''
    Translates moves from the integer notation back into algebraic notation.
    See doc string at end of file for referene on methodology.
    Inputs:
        int_turn: int representation of move
    returns string, algebraic repr. of move
    '''
    piece_maps = {"9": "K", "1": "Q", "2": "Q", "3": "R", "4": "R", "5": "B",
                  "6": "B", "7": "N", "8": "N", "0": ""}
    file_maps = {"1": "a", "2": "b", "3": "c", "4": "d", "5": "e", "6": "f",
                 "7": "g", "8": "h"}
    check_maps = {"0": "", "1": "+", "2": "#"}
    promo_maps = {"1": "Q", "3": "R", "5": "B", "7": "N"}
    direction_maps = {"0": 0, "1": -1, "2": 1, "3": 0, "4": -1, "5": 1}
    castling_maps = {"0": "", "1": "+", "2": "#"}
    check = ""

    # See if piece was captured in turn
    if int_turn < 0:
        capture = "x"
        turn = str(int_turn)[1:]  # Omit first character, which will be (-)
        int_turn = abs(int_turn)
    else:
        capture = ""
        turn = str(int_turn)

    # Castling
    if (turn[0] == "9" and int_turn < 100) or (turn[:2] == "99"):
        if re.findall(r"\d\d\d", turn):
            castling = "O-O-O"
        else:
            castling = "O-O"
        castling += castling_maps[turn[-1]]
        return castling

    # Pawn promotion
    if int_turn >= 30000:
        check = check_maps[turn[1]]
        int_file = int(turn[2]) + 1  # File compensation (see doc str)
        file = file_maps[str(int_file)]  # Original file of pawn

        # Calc direction of move (straight, left diagonal, right diagonal),
        # and apply that direction to orig file to get destination file
        direction = direction_maps[turn[3]]
        if direction == 0:
            dest_file = ""
        else:
            int_dest_file = int_file + direction
            dest_file = file_maps[str(int_dest_file)]

        # Calculate rank
        if int(turn[3]) < 3:  # White promotes
            rank = "8"
        else:
            rank = "1"

        # Piece promoted to
        promo = "=" + promo_maps[turn[-1]]
        return file + capture + dest_file + rank + promo + check

    # Back to regular moves
    # Check, checkmate, no promotion
    if (int_turn >= 10000) and (int_turn < 30000):
        check = check_maps[turn[0]]
        turn = str(int(turn[1:]))  # removes first char and any preceding 0's

    # Piece being moved
    piece = piece_maps[turn[0]]
    # Pawns
    if int(turn) < 1000:
        piece = ""

    # Rank/file identifiers.
    # Pawns first as they use special rules
    if not piece:
        if not capture:  # Pawns dont use ident unless they capture
            ident = ""
        else:
            ident = file_maps[turn[0]]
    elif int(turn[1]) == 0:  # Regular piece, no identifier
        ident = ""
    elif int(turn[0]) % 2 == 0:  # Rank identifier
        ident = turn[1]
    else:  # File identifier
        ident = file_maps[turn[1]]

    # Destination coords
    coords = file_maps[turn[-2]] + turn[-1]

    return piece + ident + capture + coords + check


def translation_test(db, n=20, test_cases=None, v=False):
    '''
    -----------OBSOLETE AS OF MOVES TABLE BEING ADDED TO DB----------
    Tests translation of all possible algebraic move formats. test_cases
    contains the algebraic notation of the file and the expected int notation.
    Inputs:
        db: string, database path. Set to None if using test_cases.
        n: if using db, num of games to pull
        test_cases: list of moves to test, rather than using random
        v: booll, verbose
    returns list of tuples w/ translations
    '''
    # Open test_cases file as csv into list if provided
    if test_cases:
        all_moves = open(test_cases).read()
        move_list = all_moves.split()

    # Otherwise, query for n random games of moves
    elif db:
        conn = sqlite3.connect(db)
        games = conn.execute("SELECT moves from Games ORDER BY random() "
                             "LIMIT ?;", [n]).fetchall()
        conn.close()
        temp_moves = "".join([moves[0] for moves in games])  # concat games
        temp_moves = re.split(r" \w*\. ", temp_moves)  # rm move #, make list
        move_list = []
        for moves in temp_moves:
            move_list += moves.split()  # remove spaces and break up pairs

    incorrect = []
    for move in move_list[1:]:  # Indexed to avoid initial move number
        try:
            int_move = translate_moves_to_int("1. " + move)
            algebraic = translate_int_to_move(int_move[0])

            if (move != algebraic) or v:
                incorrect.append((move, algebraic, int_move))
        except:
            print(move)
            raise

    if incorrect:
        print("Incorrect:", incorrect)
    return incorrect


'''
HOW THE MOVE->INTEGER ALGORITHM WORKS

Each move is represented by a 2 byte signed integer. This saves quite a bit of
space, as originally a move would be up to 7 bytes in length.

The magnitude of the 2 byte integer must be less than 32767. Each char in this
int (6 positions, including the sign) are assigned a different meaning.

For the sake of the explanation, number each digit 1-6:
+ 3 2 7 6 7 (2 byte integer max value)
1 2 3 4 5 6 (position identifier #)

The positions have the following significance:
1) Captures
    (+) signifies no capture was made in the move
    (-) signifies a capture
2) Checks/Promotions
    0) no check
    1) enemy king put into check
    2) checkmate
    3) pawn promotion (triggers special rules for future digits)
3) Piece Moved (with identifier info)
    If two pieces of the same type can make the same move, then there is an
        identifier of either the rank or file of the correct piece to identify
        which of the two pieces makes the move. This digit identifies
        the piece moved AND the whether the identifier which follows is of the
        rank of the file. This saves a digit, keeping it a 2 byte int in the
        case of an identifier being present.
    0) (K)ing
    1) (Q)ueen (file identifier)
    2) (Q)ueen (rank or no identifier)
    3) (R)ook (file)
    4) (R)ook (rank or no identifier)
    5) (B)ishop (file)
    6) (B)ishop (rank or no identifier)
    7) k(N)ight (file)
    8) k(N)ight (rank or no identifier)
    9) (P)awn
4) Rank/File identifier (0 if none) (see position 3)
5) Destination Rank
6) Destination File

IN THE CASE OF PAWN PROMOTION:
1) As Above
2) 3, to signify pawn promotion
3) Behaves like (2) above.
    0) None
    1) Check
    2) Checkmate
4) File Identifier - 1 (to prevent size increase to 4 byte int if file = 8)
5) Promotion Details
    Pawns either progress straight, or capture diagonally. Furthermore, they
        can only promote on the back ranks (rank 8 for white, 1 for black).
        This char stores which side promoted and which direction the movement
        happened (straight, capture diagonol left, capture diagonol right).
        This information is used to infer the destination file (saving a char)
    0) White, straight
    1) White, diag left
    2) White, diag right
    3) Black, straight
    4) Black, diag left
    5) Black, diag right
6) Promoted Piece
    There is a surprising num of bishop/rook promos, despite being objectively
        worse than a queen except in very rare case of a queen forcing a draw.
    1) Queen
    2) Rook
    3) Bishop
    4) Knight
'''
