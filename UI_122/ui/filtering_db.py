#Constructing Query and Results

import sqlite3
import os
import ui.database_tools as dbt
import pandas as pd
from pathlib import Path

DATA_DIR = str(Path(__file__).parents[2])
DATABASE_FILENAME = os.path.join(DATA_DIR, 'database.db')

#where should I cur.close()? need to add them
#need to fix queries for results and first plays (need count and intersect and 
    #also include the rest of query stuff in dict) --> commented out right after av_plays

'''
This code is written assuming that the dictionary output from the HTML is in
the following form of:

data = {
    min_B_ELO: type(int) >= 600 & less than max_B_ELO,
    max_B_ELO: type(int) <= 3000 & greater than min_B_ELO,
    min_W_ELO: type(int) >= 600 & less than max_W_ELO,
    max_W_ELO: type(int) <= 3000 & greater than min_W_ELO,
    num_plays_cutoff: 0 < type(int) < 100,
    result: 1 or -1
    first_play_white: validmove,
    first_play_black: validmove,
    gameID_box: boolean
}

If nothing is inputted for one or all of these options in the data dictionary,
they will default to certain values and return data regarding those except
for filter plays.
'''
def dict_to_list(data):
    '''
    This is a helper function that returns the list of the data dictionary.

    Input: dict
    Output: list 
    '''
    data_list = [data['min_B_ELO'],data['max_B_ELO'],data['min_W_ELO'],data['max_W_ELO'],\
        data['num_plays_cutoff'],data['result']]
    return data_list

def get_statistics(data):
    '''
    This is the function that returns statistics given the input form, except
    the filtering for opening moves. 
    '''
    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()

    cur.execute('SELECT count (*) FROM Games')
    total_number = cur.fetchone()[0]
    print (total_number)

    data_list = dict_to_list(data)
    
    query = 'SELECT count (*) FROM Games WHERE BlackElo >= ? AND BlackElo <= ? \
    AND WhiteElo >= ? AND WhiteElo <= ? AND Plycount <= ? AND Result == ?'
    #need to add default values for this query to work 

    cur.execute(query,data_list)
    fraction_number = cur.fetchone()[0]

    percentage = fraction_number/total_number

    cur.execute('SELECT AVG(Plycount) FROM Games')
    av_plays = cur.fetchone()[0]

    '''    
    if data['first_play_white'] is not '' and data['first_play_black']\
    is not '':
        white_integer = dbt.convert_to_int(data['first_play_white'])
        black_integer = dbt.convert_to_int(data['first_play_black'])

        integer_list = [white_integer,black_integer]

        query = 'SELECT count (*) FROM Moves WHERE turn = 1 AND move = ? \
        INTERSECT SELECT count (*) FROM Moves WHERE turn = 2 AND Move = ?'
        #get count from this query

        cur.execute(query,integer_list)
        revised_fraction_number = cur.fetchone()[0]

    elif data['first_play_white'] is not '':
        white_integer = [dbt.convert_to_int(data['first_play_white'])]
        query = 'SELECT count (*) FROM Moves WHERE turn = 1 and move = ?'
        cur.execute(query,white_integer)

        revised_fraction_number = cur.fetchone()[0]


    else:
        if data['first_play_black'] is not '':
            black_integer = [dbt.convert_to_int(data['first_play_black'])]
            query = 'SELECT count (*) FROM Moves WHERE turn = 2 and move = ?'
            cur.execute(query,black_integer)

            revised_fraction_number = cur.fetchone()[0]

    if data['result'] is not None:
    '''

#    if gameID_box:
#        gameID_list = [item[0] for item in cur.execute('SELECT FICSGamesDBGameNo').fetchall()]    
    
    return ('The average percentage of games in our database given your filtering\
        options is', percentage,' . The average number of plays for the games in\
        this filtered database is ', av_plays,'.')