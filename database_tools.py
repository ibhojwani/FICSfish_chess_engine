'''
CS122 Project

Ginormous Anteaters

Contains 2 primary functions, initialize_db() and populate_db(), to
build a database and insert information from a pgn file, respectively.

Author(s): Ishaan Bhojwani
'''

import re

import sqlite3
import os
import time
import matplotlib.pyplot as plt
from csv import reader


# information to pull from the pgn file
INFO_TO_PULL = ["FICSGamesDBGameNo",
                "WhiteElo",
                "BlackElo",
                "WhiteRD",
                "BlackRD",
                "ECO",
                "PlyCount",
                "Result",
                "Moves"]
# Information to include in db (<column name>, <structure_type>)
INFO_TO_INCLUDE = {"WhiteElo": "INTEGER",
                   "BlackElo": "INTEGER",
                   "Result": "INTEGER",
                   "PlyCount": "INTEGER",
                   "Moves": "TEXT",
                   "FICSGamesDBGameNo": "INTEGER"}
# Indices to build on database (<index name>, <table>, [<column(s)>])
INDICES = [("IX_Move", "Moves", ["Move"])]

QUERY_FREQ = 100  # CURRENTLY UNUSED


def populate_db(games_file, db, unique=True, query_freq=QUERY_FREQ):
    '''
    Populates the database with a list of games.
    input:
        games: filename with pgn of games to be added
        db: database to populate, filename
        redundancy: when True, stops redundant files from being added
    returns int,  # of games added
    '''
    print('Connecting to database...')
    initialize_db(db)
    conn = sqlite3.connect(db)

    # if param is true, checks to make sure file isn't already in db.
    if check_file(games_file, conn, unique):
        print("File is already in database!\n")
        return None
    conn.execute("INSERT INTO FilesAdded Values (?);", [games_file])

    # Drops old indices. May be faster to omit this, needs testing.
    print("Dropping Indices...")
    drop_indices(conn)

    # Opens game file and adds games, printing % completion every 10%
    print("Adding games...0%")
    with open(games_file, "r") as file:
        games = file.read()
    game_list = re.split(r"\n\n\[", games)
    add_games(game_list, conn)

    # Concludes insert, builds index and stat table, and closes connection
    i = conn.total_changes
    print("Building new indices and cleaning up...")
    build_indices(conn)

    print("Modified {} rows".format(i - 1))
    conn.execute("ANALYZE;")
    conn.commit()
    conn.close()

    return None


def initialize_db(path):
    '''
    Builds the database and database tables.
    Inputs:
        path: string containing database path
    returns None
    '''
    conn = sqlite3.connect(path)
    games_query = "CREATE TABLE IF NOT EXISTS Games (\n"

    for field, field_type in INFO_TO_INCLUDE.items():
        games_query += " {} {},\n".format(field, field_type)

    games_query = games_query + " GameID INTEGER PRIMARY KEY);"
    conn.execute(games_query)

    files_added_query = "CREATE TABLE IF NOT EXISTS FilesAdded (FileName)"
    conn.execute(files_added_query)

    moves_query = "Create Table IF NOT EXISTS Moves (\n" \
        "Move, GameID, FOREIGN KEY(GameID) REFERENCES Games(GameID));"
    conn.execute(moves_query)

    conn.commit()

    return None


def check_file(games_file, db, unique):
    '''
    Checks if a given file has already been added to the db from the filename.
    Inputs:
        game_file: string, name of file (NOT path)
        db: database cursor or connection
    returns True if item in db, False if not
    '''
    if not unique:
        return False

    added_files = db.execute("SELECT FileName FROM FilesAdded WHERE FileName\
        = ?", [games_file]).fetchall()

    return bool(added_files)


def drop_indices(conn):
    '''
    Drops all indices in a database.
    Inputs:
        conn: database connection object
    returns None
    '''
    for index in INDICES:
        conn.execute("DROP INDEX IF EXISTS {};".format(index[0]))
    return None


def build_indices(conn):
    '''
    Builds indices for a database.
    Inputs:
        conn: database connection object
    returns None
    '''
    for ix in INDICES:
        query = "CREATE INDEX IF NOT EXISTS {} on {} (".format(ix[0], ix[1])
        for col in ix[2]:
            query += "{}, ".format(col)
        query = query[:-2] + ");"
        conn.execute(query)

    return None


def pull_info(game, file_flag=False):
    '''
    Builds a dictionary with info of a particular game.
    Inputs:
        game: string containing FICS game info
    returns: dict
    '''

    if file_flag:
        with open(game, "r") as file:
            line_list = file.readlines()
    else:
        line_list = game.splitlines()
    game_info = {}

    for line in line_list[:-2]:
        split = line.split(' "')
        if split[0][1:] in INFO_TO_PULL:
            game_info[split[0][1:]] = split[1][:-2]
    game_info["Moves"] = '"' + re.sub(r"{.*", "", line_list[-1]) + '"'

    return tweak_info(game_info)


def tweak_info(game_info):
    '''
    Tweaks dict of game information to conform to database reqs.
    Uses 'if' statements to check if key is in game_info, as INFO_TO_PULL
    and INFO_TO_INCLUDE are designed to change over course of project.
    Input:
        game_info: dict
    returns: modified dict
    '''

    def convert_to_int(key):
        '''
        if key is required in db, then converts value to int.
        Input:
            string
        returns None
        '''
        if key in INFO_TO_PULL:
            game_info[key] = int(float(game_info[key]))
        return None

    # Turns 'Result' from string to int, w/ white win=1, black=-1, and draw=0
    # This is done save space (3-7 bytes to just 1) and simplify querying.
    if 'Result' in INFO_TO_PULL:
        result = game_info['Result'][2]  # 'Result' is either 1-0, 0-1, 1/2-1/2
        if result == "0":  # White wins
            game_info['Result'] = 1
        elif result == "1":  # Black wins
            game_info['Result'] = -1
        else:  # Draw
            game_info['Result'] = 0

    # Turns relevent values into ints from strings
    for key, value in INFO_TO_INCLUDE.items():
        if value == "INTEGER":
            convert_to_int(key)

    # Ensures ECO is passed as a string
    if 'ECO' in INFO_TO_PULL:
        game_info['ECO'] = '"' + game_info["ECO"] + '"'

    if game_info["PlyCount"] >= 200 or game_info["PlyCount"] < 5:
        game_info = None

    return game_info


def add_games(game_list, db):
    '''
    Adds a game to a database.
    Inputs:
        game_list: list containing strings to pass to pull_info
        db: database cursor or connection
    returns None
    '''
    length = len(game_list)
    i = 0

    for game in game_list:
        i += 1
        if i % 10000 == 0:
            print("..............{}%".format(round(i / length * 100)))

        if game[0] != '[':  # Need to find how to split without losing the '['
            game = '[' + game
        game_info = pull_info(game)

        if game_info:
            query = "INSERT INTO games ("
            for field in INFO_TO_INCLUDE:
                query += "\n{},".format(field)
            query = query[:-1] + ")" + "\nVALUES ("
            for value in INFO_TO_INCLUDE:
                query += "\n{},".format(game_info[value])
            query = query[:-1] + ");"

            db.execute(query)

    return None


def translate_moves_to_int(moves):
    '''
    Parses moves. Has to be fast. Indexing is avoided, as is regex, for speed.
    Turns all moves into a signed 2 byte integer representation. See doc
    string at end of file for details on representation.

    Inputs:
        moves: string containing moves list
    returns list of 2 byte signed ints
    '''
    #consider switching kings and pawns?
    maps = {"K": 9000, "Q": 1000, "R": 3000, "B": 5000, "N": 7000, "P": 0,
            "a": 10, "b": 20, "c": 30, "d": 40, "e": 50, "f": 60, "g": 70,
            "h": 80, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
            "8": 8}

    # splits move string into individual moves
    # IS IT POSSIBLE WITH ONLY 1 RE, AND NO LOOP?
    rounds = re.split(r" \w*\. ", moves[3:])
    turns = []
    for r in rounds:
        turns += r.split(" ")  # this could be done in the loop to save time
    int_turns = []

    # MAKE A HELPER FUNCTION TO REDUCE REDUNDANCY?
    for turn in turns:
        turn_orig = turn
        # Castling. Nested IF to only do 1 check on all non long-castle moves
        if "O" in turn:
            if turn == "O-O":
                int_turns.append(9)  # castling short simply gives 9
                continue
            else:
                int_turns.append(99)  # castling long likewise gives 99
                continue

        # initializes translation int
        move_int = 0

        # Deals with pawns first due to pawn promotion complications
        if turn[0].islower():

            # pawn promotion special rules. Ok if this is slower as its rare.
            # The order of if statements matters for code simplicity.
            # GO INTO HERE FROM TRY STATEMENT, TESTING IF TURN[0] IS IN MPARS?
            if "=" in turn:
                move_int += 30000  # turns 10000's place to 3 for pawn promo

                # checks/checkmates
                if "+" in turn:
                    move_int += 1000
                    turn = turn[:-1]
                elif "#" in turn:
                    move_int += 2000
                    turn = turn[:-1]

                # file identification
                move_int += maps[turn[0]] * 10

                # movement info (see doc at end of file for info)
                if turn[-3] == "1":
                    move_int += 30

                # piece promoted to
                move_int += maps[turn[-1]] / 1000

                # captures
                if "x" in turn:
                    if turn[-2] < turn[0]:
                        move_int += 20
                    else:
                        move_int += 10
                    move_int *= -1

                int_turns.append(int(move_int))
                continue
                # end of pawn promotion

            # back to regular pawns
            # Check/checkmates.
            if "+" in turn:  # check
                move_int += 10000
                turn = turn[:-1]
            elif "#" in turn:  # checkmate
                move_int += 20000
                turn = turn[:-1]

            # file identification
            move_int += maps[turn[0]] * 10

            # final coords
            move_int += maps[turn[-2]] + maps[turn[-1]]

            # captures
            if "x" in turn:
                int_turns.append(move_int * -1)
            else:
                int_turns.append(move_int)
            continue
            # end of pawns

        # Piece if not pawn
        else:
            move_int += maps[turn[0]]

        # checks/checkmates
        if "+" in turn:  # check
            move_int += 10000
            turn = turn[:-1]
        elif "#" in turn:  # checkmate
            move_int += 20000
            turn = turn[:-1]

        # destination coords and piece being moved
        move_int += maps[turn[-1]] + maps[turn[-2]]

        # capture and piece ident info--must go last as capture -> move_int*-1
        if "x" in turn:
            potential_ident = turn[-4]
            if potential_ident.islower():  # signals file identifier
                move_int += maps[potential_ident] * 10   
            elif not potential_ident.isupper():  # signals rank identifier
                move_int += 1000 + maps[potential_ident] * 100
            move_int *= -1
        else:
            potential_ident = turn[-3]
            if potential_ident.islower():  # signals file identifier
                move_int += maps[potential_ident] * 10
            elif not potential_ident.isupper():  # signals rank identifier
                move_int += 1000 + maps[potential_ident] * 100
        int_turns.append(move_int)

    return int_turns


def add_all_in_dir(directory, db):
    '''
    simple for loop to add all game files in a directory.
    Inputs:
        directory: string, path of directory
        db: string, path of directory
    returns None
    '''
    initialize_db(db)
    for i, file in enumerate(os.listdir(directory)):
        print("{}/{}".format(i + 1, len(os.listdir(directory))))
        if file.endswith(".pgn"):
            populate_db("{}/{}".format(directory, file), db)
        else:
            print("Skipping non .pgn file...")
    return None


def clear_db(db):
    '''
    Clears db of all indices and tables. Used in testing/debugging.
    Inputs:
        db: database path
    returns None
    '''
    tables = ["Moves", "Games", "FilesAdded", "sqlite_stat1"]
    conn = sqlite3.connect(db)

    for table in tables:
        conn.execute("DROP TABLE IF EXISTS {};".format(table))

    for index in INDICES:
        conn.execute("DROP INDEX IF EXISTS {};".format(index[0]))

    conn.execute("VACUUM;")
    conn.commit()
    print("Database cleared")

    return None


def calc_freq(test_file, db):
    '''
    Meant to return optimal db.execute() frequency, obsolete for now as we are
    executing with every single game instead of as a batch of n games.
    This function is probably buggy, as we've hardly used/tested it.
    Inputs
        test_file: string of games file path (indended to have ~1-5k games)
        db: databse file path
    returns: ideal number of games per db.execute() query, and prints graph
    '''
    times = {}
    last_run = 0
    # 1 - 79001 by inc of 1000
    freqs = [x for x in list(range(80000))[1::1000]]

    for freq in freqs:
        while last_run < 60:
            t1 = time.process_time()
            populate_db(test_file, db)
            t2 = time.process_time()

            last_run = t2 - t1
            times[freq] = last_run
            clear_db(test_file)
            print(freq, times[freq])

    plt.bar(range(len(times)), list(times.values()), align='center')
    plt.xticks(range(len(times)), list(times.keys()))
    plt.show()

    return min(times, key=times.get())


def test_translation(test_cases):
    '''
    Tests translation of all possible algebraic move formats.
    Inputs:
        test_cases: string of test file, with tuples of move and expected int.
    returns None
    '''
    
    with open(test_cases) as f:
        imported_cases = [list(line) for line in reader(f)]
        cases = []
    for case in imported_cases:
        cases.append([case[0], int(case[1])])
    print("Incorrect Matches: (input, translation, expected)")
    for pair in cases:
        result = translate_moves_to_int("1. "+ pair[0])[0]
        if result != pair[1]:
            print(pair[0], result, pair[1])

    return None


if __name__ == "__main__":
    add_all_in_dir(os.getcwd(), "database.db")



'''
Notes:

Potentially millions of games/moves
speed optimization + size constraints
decisions on what data to keep and what to omit
indices -- speed query but increase db size
multiple row insert -- computer couldnt handle 500k line string
? parameters -- not used in cases of internal queries
move -> numbers
    cannot simply translate, too many variables
    pawn promotion is a bitch
    instead using a system sorta like the dewey decimal system
    speed is of essence, as 1 billion moves is plausible
        regex takes a long time -- use it sparingly
        '<value> in <string>' is faster than comparison
    getting all this shit as a 2 byte int was a bitch. 
    order of move_int building
big files take foever to open
        
need to do:
move -> numbers
numbers -> moves
full game -> next move
not always analyze?

compile-time options:
sqlite_enable_stat3
sqlite_threadsafe=0
SQLITE_LIKE_DOESNT_MATCH_BLOBS
SQLITE_DEFAULT_MEMSTATUS=0

other optoins:
PRAGMA synchronous=1;
PRAGMA journal_mode = WAL
    need to reset to DELETE
sqlite_stat3
analyze tools
cProfile and pstats
'''

'''
HOW THE MOVE->INTEGER ALGORITHM WORKS

Each move is represented by a 2 byte signed integer. This saves quite a bit of
space, as originally a move would be up to 7 bytes in length.

The magnitude of the 2 byte integer must be less than 32767. Each char in this
int (6 positions, including the sign) are assigned a different meaning.

For the sake of the explanation, number each character 1-6:
+ 3 2 7 6 7 (integer)
1 2 3 4 5 6 (position identifier)

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
    Each piece has their own identifier in algebraic notation. Furthermore, if
        two pieces of the same type can make the same move, then there is an
        identifier of either the rank or file of the correct piece to identify
        which of the two pieces makes the move. This character identifies
        the piece moved AND whether the identifier is the rank or the file.
        It is done this way to save a char, thereby preventing a 4 byte int.
    0) (K)ing
    1) (Q)ueen (file)
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
4) File Identifier (always present for pawn movement)
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
