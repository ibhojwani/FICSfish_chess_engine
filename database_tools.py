'''
CS122 Project
Ginormous Anteaters
Author(s): Ishaan Bhojwani
'''

import re
import sqlite3
import os
from time import time
from translation import translate_int_to_move, translate_moves_to_int
from cProfile import run
from pstats import Stats
from numpy import random

'''
TODO
````
How many moves should be included?
query frequency?
modes of play?
storing past moves?
Only include winning moves?
filter on join?
take re from sunfishconvert
build cursor?
'''

# information to pull from the pgn file
INFO_TO_PULL = ["WhiteElo",
                "BlackElo",
                "WhiteRD",
                "BlackRD",
                "PlyCount",
                "Result",
                "Moves",
                "FICSGamesDBGameNo"]

# Information to include in db (<column name>, <structure_type>)
INFO_TO_INCLUDE = {"WhiteElo": "INTEGER",
                   "BlackElo": "INTEGER",
                   "Result": "INTEGER",
                   "PlyCount": "INTEGER",
                   "Fics_ID": "INTEGER UNIQUE"}

# Indices to build on database (<index name>, <table>, [<column(s)>])
INDICES = []
#("IX_Move", "Moves", ["Turn", "Move", "GameID"])

# Determines how many games go into a single INSERT statement. Adjusted to be
# fast on my machine, don't know if the ideal number will be different on
# another machine -- Ishaan
QUERY_FREQ = 250


def return_best(conn, filters, move=None, explain=False):
    '''
    Takes a move, creates viewreturns the best move and creates relevent views
    Inputs:
        conn: db connection
        views: list of names of current existing views for past turns
        turn: turn previously played
    '''
    move_number = len(filters) + 1

    if move_number == 1 and not move:
        query = "SELECT move, count(move) \n\
                FROM moves\n\
                WHERE turn=1\n\
                GROUP BY move\n\
                LIMIT 10;"
        move = pick_move(conn.execute(query).fetchall())
        return translate_int_to_move(move)

    int_move = translate_moves_to_int(move)[0]
    fil = "(moves.turn = {} AND moves.move = {})".format(move_number,
                                                         int_move)
    filters.append(fil)
    where = "\n OR ".join(filters) + "\n"
    query = "SELECT moves.move, count(moves.move)\n\
             FROM moves\n\
             JOIN (\n\
                SELECT gameID, result\n\
                FROM (\n\
                    SELECT moves.gameid, count(moves.gameid) AS ct, result\n\
                    FROM moves\n\
                    JOIN games\n\
                        ON moves.gameID = games.gameID\n\
                    WHERE\n\
                        {}\n\
                    GROUP BY moves.gameid)\n\
                WHERE ct = ?) as valid\n\
             ON moves.gameID=valid.gameID\n\
             WHERE\n\
                moves.turn=?\n\
                AND valid.result = ?\n\
             GROUP BY moves.move;".format(where)
    if explain:
        query = "EXPLAIN QUERY PLAN " + query
    params = [move_number, move_number + 1, (-1)**move_number]

    results = conn.execute(query, params).fetchall()
    if explain:
        return results

    if not results:
        return None

    return translate_int_to_move(pick_move(results))


def pick_move(query_results):
    moves = []
    probs = []
    for pair in query_results:
        moves.append(pair[0])
        probs.append(pair[1])

    probs = [p/sum(probs) for p in probs]
    move = random.choice(moves, p=probs)

    return move


def populate_db(games_file, db, n=None, verbose=False, single_file=True):
    '''
    Populates the database with a list of games.
    input:
        games: filename with pgn of games to be added
        db: database to populate, filename
        redundancy: when True, stops redundant files from being added
        verbose: bool
        sinlge_file: True if only a single file is being added
    returns int,  # of games added
    '''
    init_t = time()
    if verbose:
        print('Connecting to database...')
    initialize_db(db)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Drops old indices. May be faster to omit this, needs testing.
    if verbose:
        print("Dropping Indices...")
    drop_indices(cur)

    # Opens game file and adds games, printing % completion every 10%
    with open(games_file, "r") as file:
        games = file.read()
    game_list = re.split(r"\n\n\[", games)
    add_games(game_list, cur, n, verbose)

    # Concludes insert, builds index and stat table, and closes connection
    i = conn.total_changes
    if verbose:
        print("Building new indices and cleaning up...")
    if single_file:
        build_indices(cur)

    print("Modified {} rows in {} seconds.".format(i-1, time() - init_t))
    cur.execute("ANALYZE;")
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
        "Move, Turn, GameID, FOREIGN KEY(GameID) REFERENCES Games(GameID));"
    conn.execute(moves_query)

    conn.commit()
    conn.close()

    return None


def add_games(game_list, db, n, verbose):
    '''
    Adds a game to a database.
    Inputs:
        game_list: list containing strings to pass to pull_info
        db: database cursor or connection
        n: max number to add, if None then add all
    returns None
    '''
    def build_game_query():
        ''' Builds query outline for game insert'''
        query = "INSERT INTO Games("
        for field in INFO_TO_INCLUDE:
            query += "\n{},".format(field)
        query = query[:-1] + ")" + "\nVALUES ("
        return query  # string

    def build_move_query():
        ''' Builds query outline for move insert'''
        return "INSERT INTO Moves(\n move,\n turn,\n gameID) VALUES ("

    query_timer = 0
    # gets the highest rowID currently in table
    starting_rowid = db.execute("SELECT MAX(gameID) from games;").fetchall()[0][0]
    if not starting_rowid:
        starting_rowid = 0
    game_query = build_game_query()
    move_query = build_move_query()
    if n:
        game_list = game_list[:n]
    length = len(game_list)

    for i, game in enumerate(game_list):
        query_timer += 1
        # print % completion at intervals of 10% and every 9k moves
        if (i % 9000 == 0) and verbose:
            print("..............{}%".format(round(i / length * 100)))

        # Ensures game starts with '[', which can be lost during splitting
        if game[0] != '[':
            game = '[' + game
        game_info = pull_info(game)

        # FIND A FASTER WAY TO BUILD QUERY -- maybe less adding strings?
        if game_info:
            starting_rowid += 1
            # Builds game query
            for value in INFO_TO_INCLUDE:
                game_query += "\n{},".format(game_info[value])
            game_query = game_query[:-1] + "), ("

            # Builds move query
            for move_num, move in enumerate(game_info["Moves"]):
                # Adds move, current plycount, and gameid
                move_query += "{}, {}, {}), (".format(str(move),
                                                      move_num + 1,
                                                      starting_rowid)

        # Execute / commit in batches, as multirow inserts are faster.
        # Best freq depends: long query strings uses more RAM and can slow.
        if query_timer == QUERY_FREQ:
            # Execute and commit queries
            try:
                db.execute(game_query[:-3] + ";")
                db.execute(move_query[:-3] + ";")
            except:
                print(game_query[:-3])
                print(move_query[:-3])
                raise

            # Reset variables
            game_query = build_game_query()
            move_query = build_move_query()
            query_timer = 0

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
    game_info["Moves"] = re.sub(r" {.*", "", line_list[-1])

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
        elif result == "1":  # Black win
            game_info['Result'] = -1
        else:  # Draw
            game_info['Result'] = 0

    # Turns relevent values into ints from strings
    for key, value in INFO_TO_INCLUDE.items():
        if value == "INTEGER":
            convert_to_int(key)

    # Changes key name of Fics_ID
    if "Fics_ID" in INFO_TO_INCLUDE:
        game_info["Fics_ID"] = game_info["FICSGamesDBGameNo"]

    # Translates moves into a list of 2 byte ints
    if not game_info["Moves"]:
        game_info = None
        return game_info
    game_info["Moves"] = translate_moves_to_int(game_info["Moves"], ls=True)

    if game_info["PlyCount"] < 5:
        game_info = None

    return game_info


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
            populate_db("{}/{}".format(directory, file), db, single_file=False)
        else:
            print("Skipping non .pgn file...")

    conn = sqlite3.connect(db)
    build_indices(conn)
    conn.commit()
    conn.close()
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


def profile():
    '''
    Profiles populate_db and prints 15 slowest functions.
    '''
    run('r.populate_db("test_file.pgn", database.db", unique=False, n=10000)',
        'stats')
    stats = Stats('stats')
    stats.sort_stats("tottime")
    stats.print_stats(15)


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
TALK ABOUT HOW MANY MOVES TO INCLUDE

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
