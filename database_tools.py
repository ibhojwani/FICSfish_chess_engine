'''
CS122 Project

Ginormous Anteaters

Contains 2 primary functions, initialize_db() and populate_db(), to
build a database and insert information from a pgn file, respectively.

Author(s): Ishaan Bhojwani
'''

import re
import sqlite3
from fractions import Fraction
import os

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


def populate_db(games_file, db, unique=True):
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
    conn.close()

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
        result_l = game_info['Result'].split('-')
        game_info['Result'] = int(Fraction(result_l[0]) -
                                  Fraction(result_l[1]))

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
        if round(i / length * 100, 3) % 10 == 0:
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


def parse_moves(moves):
    '''
    parses moves.
    Inputs:
        moves: string containing moves list
    returns list
    '''
    maps = {"K": 1, "Q": 2, "R": 3, "B": 4, "N": 5,
            "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8,
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
            "x": 1, "+": 2, "#": 3}

    rounds = re.split(r" \d\. ", moves)
    turns = []
    for r in rounds:
        turns += r.split(" ")

    int_turns = []

    for i, turn in enumerate(turns):
        turn_num = (i + 2) // 2
        integer_turn = ""
        for letter in turn:
            integer_turn += maps[letter]

    return []


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
    Clears db of all indices and tables.
    Inputs:
        db: database path
    returns None
    '''
    tables = ["Moves", "Games", "FilesAdded"]
    conn = sqlite3.connect(db)

    for table in tables:
        conn.execute("DROP TABLE IF EXISTS {};".format(table))
    
    for index in INDICES:
        conn.execute("DROP INDEX IF EXISTS {};".format(index[0]))

    conn.execute("VACUUM;")
    conn.commit()
    print("Database cleared")

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
stat to decide plycount?

need to do:
move -> numbers
numbers -> moves
full game -> next move
'''
