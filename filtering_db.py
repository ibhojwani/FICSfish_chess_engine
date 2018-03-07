#Constructing Query and Results

import sqlite3
import os
import database_tools as dbt

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'database.db')

'''
This code is written assuming that the dictionary output from the HTML is in
the following form of:

output_dictionary = {
    min_B_ELO: type(int) >= 600 & less than max_B_ELO,
    max_B_ELO: type(int) <= 3000 & greater than min_B_ELO,
    min_W_ELO: type(int) >= 600 & less than max_W_ELO,
    max_W_ELO: type(int) <= 3000 & greater than min_W_ELO,
    num_plays_cutoff: 0 < type(int) < 100,
    first_play_white: validmove,
    first_play_black: validmove,
    gameID_box: boolean
}

'''

def filter_db(db,data):
    '''
    This is a helper function that creates a query based on the output dictionary and
    returns the database.

    Input: db (sqlite3 database), output_dictionary (dict) which is the user input
    Output: db - filtered database given user input
    '''
    #ADD CONDITION FOR IF THE DICTIONARY IS EMPTY

    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()
    output_list = []
    first_string = 'SELECT count * FROM games WHERE'
    condition = ''

    if len(data) == 0:
        return db

    condition = True if first_string[-5:] == 'WHERE' else False
    #does this automatically check each time condition is called?

    if min_B_ELO in data:
        add_string = 'BlackElo <= ?'
        output_list.append(data[min_B_ELO])
        if condition:
            first_string += ' ' + add_string
        else:
            first_string += ' AND ' + add_string

    if max_B_ELO in data:
        add_string = 'BlackElo >= ?'
        output_list.append(data[max_B_ELO])
        if condition:
            first_string += ' ' + add_string
        else:
            first_string += ' AND ' + add_string

    if min_W_ELO in data:
        add_string = 'WhiteElo <= ?'
        output_list.append(data[min_W_ELO])
        if condition:
            first_string += ' ' + add_string
        else:
            first_string += ' AND ' + add_string

    if max_W_ELO in data:
        add_string = 'WhiteElo >= ?'
        output_list.append(data[max_W_ELO])
        if condition:
            first_string += ' ' + add_string
        else:
            first_string += ' AND ' + add_string

    if num_plays_cutoff in data:
        add_string = 'Plycount <= ?'
        output_list.append(data[num_plays_cutoff])
        if condition:
            first_string += ' ' + add_string
        else:
            first_string += ' AND ' + add_string

    db = cur.execute(first_string,ouput_list)

    return db

def filtering_MoveSeq(db,data):
    '''
    This is the helper function that filters the database further based
    on whether the user chose to filter out first play. This function also
    assumes that either the white or black opening moves are inputted in
    the user form.

    Input:
    Output:
    '''
    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()

    if first_play_white in data:
        first_move = data[first_play_white]
        first_move_int = dbt.convert_to_int(first_move)

    if first_play_black in data:
        second_move = data[first_play_black]
        second_move_int = data[first_play_black]

    if first_play_black in data and first_play_white in data:
        output_list = [first_move_int,second_move_int]
        db = cur.execute('SELECT gameID FROM Moves WHERE turn = 1 \
            AND move = ? INTERSECT SELECT gameID FROM Moves WHERE \
            turn = 2 AND Move = ?',output_list)
        return db

    elif first_play_black in data:
        db = cur.execute('SELECT gameID FROM Moves WHERE turn = 2 AND \
            move = ?',second_move_int)

    else:
        db = cur.execute('SELECT gameID FROM Moves WHERE turn = 2 AND \
            move = ?',first_move_int)

def return_statistics(db,data):
    '''
    This is the main function that implements filtering the database
    based on user input.
    '''

    if len(data) == 0:
        return 'Please input data in at least one field.'

    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()
    gameID_list = []

    total_games = cur.execute('SELECT count (*) FROM Games')
    filtered_db = filter_db(db,data)
    if first_play_white in data:
        final_db = filtering_MoveSeq(filtered_db,data)

    conn = sqlite3.connect(final_db)

    fraction_games = cur.execute('SELECT count (*) FROM Games')
    percentage = 100 * (fraction_games/total_games)

    av_plays = cur.execute('SELECT AVG(Plycount) FROM Games')

    if gameID_box:
        gameID_list = cur.execute('SELECT FICSGamesDBGameNo FROM Games').fetchall()

    return percentage, av_plays, gameID_list
