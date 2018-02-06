# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#
# Ishaan Bhojwani

import re
import sqlite3
from fractions import Fraction

# information to pull from the pgn file.
INFO_TO_PULL = {"WhiteElo",
                "BlackElo",
                "WhiteRD",
                "BlackRD",
                "ECO",
                "PlyCount",
                "Result",
                "Moves"}
# Information to include in db, with datatypes
INFO_TO_INCLUDE = {"WhiteElo": "INTEGER",
                   "BlackElo": "INTEGER",
                   "Result": "INTEGER",
                   "Moves": "TEXT"}


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

    games_query = games_query[:-2] + ");"
    conn.execute(games_query)

    files_added_query = "CREATE TABLE IF NOT EXISTS FilesAdded (FileName)"
    conn.execute(files_added_query)

    return None


def populate_db_games(games_file, db):
    '''
    Populates the database with a list of games.
    input:
        games: filename with pgn of games to be added
        db: database to populate, filename
    returns int,  # of games added
    '''
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    already_added_query = "SELECT * FROM FilesAdded"
    already_added = (cur.execute(already_added_query)).fetchall()
    if games_file in already_added:
        return None

    with open(games_file, "r") as file:
        games = file.read()
    game_list = re.split(r"\n\n\[", games)

    i = 0
    for game in game_list:
        i += 1
        # print(i)
        # this prob isnt the best way to ensure all elements start with '['
        if game[0] != '[':
            game = '[' + game
        add_game(pull_info(game), conn)

    i = conn.total_changes
    print("Modified {} rows".format(i))

    conn.execute("INSERT INTO FilesAdded Values (?);", [games_file])

    conn.commit()
    conn.close()

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
        if split[0][1:] in INFO_TO_INCLUDE:
            game_info[split[0][1:]] = split[1][:-2]
    game_info["moves"] = '"' + re.sub(r"{.*", "", line_list[-1]) + '"'

    return tweak_info(game_info)


def tweak_info(game_info):
    '''
    Tweaks dict of game information to conform to database reqs.
    Input:
        game_info: dict
    returns: modified dict
    '''
    # Tweaks 'Result' from string to int, w/ white win=1, black=-1, and draw=0
    # This is done save space (3-7 bytes to just 1) and simplify querying.
    result_l = game_info['Result'].split('-')
    game_info['Result'] = int(Fraction(result_l[0]) - Fraction(result_l[1]))

    # Turns WhiteElo, BlackElo, WhiteRD BlackRD, and PlyCount into ints
    if "WhiteELO" in INFO_TO_INCLUDE:
        game_info['WhiteElo'] = int(game_info['WhiteElo'])
    if "BlackELO" in INFO_TO_INCLUDE:
        game_info['BlackElo'] = int(game_info['BlackElo'])
    if "WhiteRD" in INFO_TO_INCLUDE:
        game_info['WhiteRD'] = int(float(game_info['WhiteRD']))
    if "BlackRD" in INFO_TO_INCLUDE:
        game_info['BlackRD'] = int(float(game_info['BlackRD']))
    if "PlyCount" in INFO_TO_INCLUDE:
        game_info['PlyCount'] = int(game_info['PlyCount'])

    # Ensures ECO is a string
    if 'ECO' in INFO_TO_INCLUDE:
        game_info['ECO'] = '"' + game_info["ECO"] + '"'
    # Checks if game is good to be added

    return game_info


def add_game(game, db):
    '''
    Adds a game to a database.
    Inputs:
        game: dictionary containing game info (game_info)
        db: database cursor or connection
    returns None
    '''
    query = "INSERT INTO games ("

    for field in game.keys():
        query += "\n{},".format(field)
    query = query[:-1] + ")\nVALUES ("
    for value in game.values():
        query += "\n{},".format(value)

    query = query[:-1] + ");"
    db.execute(query)

    return None
