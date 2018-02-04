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


def pull_info(game, file_flag=False):
    '''
    Builds a dictionary with info of a particular game.
    Inputs:
        game: string containing FICS game info
    returns: dict
    '''
    important_info = ["FICSGamesDBGameNo",
                      "WhiteElo",
                      "BlackElo",
                      "WhiteRD",
                      "BlackRD",
                      "TimeControl",
                      "PlyCount",
                      "Result"]
    if file_flag:
        with open(game, "r") as file:
            line_list = file.readlines()
    else:
        line_list = game.splitlines()
    game_info = {}
    game_info["moves"] = re.sub(r"{.*", "", line_list[-1])
    for line in line_list[:-1]:
        split = line.split(' "')
        if split[0][1:] in important_info:
            game_info[split[0][1:]] = split[1][:-2]

    return game_info


def add_game(game, db):
    '''
    Adds a game to a database.
    Inputs:
        game: dictionary containing game info
        db: database cursor
    returns bool, indicating if successful
    '''
    d = pull_info(game)
    return None


def populate_db(games_file, db):
    '''
    Populates the database with a list of games.
    input:
        games: filename with pgn of games to be added
        db: database to populate, can be filename or conn object
    returns int,  # of games added
    '''
    db_is_file = isinstance(db, str)

    with open(games_file, "r") as file:
        games = file.read()
    game_list = re.split(r"\n\n\[", games)

    if db_is_file:
        conn = sqlite3.connect(db)
    else:
        conn = db

    for game in game_list:
        add_game(game, conn)

    i = conn.total_changes
    print("Modified {} rows".format(i))

    if db_is_file:
        conn.commit()
        conn.close()

    return i
