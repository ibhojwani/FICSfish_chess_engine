#Constructing Query and Results

import sqlite3
import os
import ui.database_tools as dbt
import pandas as pd
from pathlib import Path

DATA_DIR = str(Path(__file__).parents[2])
DATABASE_FILENAME = os.path.join(DATA_DIR, 'game_data.db')

'''
This code is written assuming that the dictionary output from the HTML is in
the following form of:

data = {
    min_B_ELO: type(int) >= 0 & less than max_B_ELO,
    max_B_ELO: type(int) <= 3000 & greater than min_B_ELO,
    min_W_ELO: type(int) >= 0 & less than max_W_ELO,
    max_W_ELO: type(int) <= 3000 & greater than min_W_ELO,
    num_plays_cutoff: 0 < type(int) < 1000 #high estimate,
    result: 1 or -1 (this contains no default)
    gameID_box: boolean
}
'''

def dict_to_list(data):
    '''
    This is a helper function that returns the list of the data dictionary. The
    reason it does it individually is to maintain the order of the inputs for the
    query. The '.items()' method for a dictionary can have random placement results
    that do not correspond to the query placements.

    Input: dict
    Output: list 
    '''

    data_list = []
    data_list.append(data['min_B_ELO'])
    data_list.append(data['max_B_ELO'])
    data_list.append(data['min_W_ELO'])
    data_list.append(data['max_W_ELO'])
    data_list.append(data['num_plays_cutoff'])

    if 'result' in data:
        data_list.append(data['result'])

    return data_list

def get_statistics(data):
    '''
    This is the function that returns the statistics based on user inputs (data dict).

    Input: dict
    Output: str and int
    '''

    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()

    cur.execute('SELECT count (*) FROM Games')
    total_number = cur.fetchone()[0]

    data_list = dict_to_list(data)
    
    query_p1 = 'SELECT count(*) '
    query_p2 = 'FROM Games WHERE BlackElo >= ? AND BlackElo <= ? \
    AND WhiteElo >= ? AND WhiteElo <= ? AND Plycount <= ?'
    

    if 'result' in data:
        query_p2 += ' AND Result == ?'

    query = query_p1 + query_p2
    cur.execute(query,data_list)
    fraction_number = cur.fetchone()[0]

    percentage = 100*(fraction_number/total_number)

    cur.execute('SELECT AVG(Plycount) FROM Games')
    av_plays = cur.fetchone()[0]

    av_plays_query = 'SELECT AVG(Plycount) ' + query_p2
    cur.execute(av_plays_query,data_list)
    filt_av_plays = cur.fetchone()[0]

    cur.execute('SELECT AVG(BlackElo) FROM Games')
    av_black_elo = cur.fetchone()[0]


    cur.execute('SELECT AVG(WhiteElo) FROM Games')
    av_white_elo = cur.fetchone()[0]

    filt_black_query = 'SELECT AVG(BlackElo) ' + query_p2
    cur.execute(filt_black_query,data_list)
    filt_black_elo = cur.fetchone()[0]

    filt_white_query = 'SELECT AVG(WhiteElo) ' + query_p2
    cur.execute(filt_white_query,data_list)
    filt_white_elo = cur.fetchone()[0]

    if data['gameID_box']:
        new_query = 'SELECT Fics_ID ' + query_p2 + ' LIMIT 10'
        cur.execute(new_query,data_list)
        games_list = [item[0] for item in cur.fetchall()]

        return ('The average number of plays in our original database is ',round(av_plays,2), \
        '. The average Black Elo rating in our original database is ',round(av_black_elo,4), 'and the average White Elo\
        Rating is ',round(av_white_elo,4),'. The average percentage relative to the number games in our database \
        given your filtering is ', round(percentage,2),'%. The average number of plays for your filtered database is ',round(filt_av_plays,2),\
        'The average White Elo rating in your filtered database is ',round(filt_white_elo,4),' and the average Black Elo is',round(filt_black_elo,4),\
        '. The following is the list of Fics Game IDs that you can search up on the FICS database:', games_list,'.')    
    
    return ('The average number of plays in our original database is ',round(av_plays,2), \
        '. The average Black Elo rating in our original database is ',round(av_black_elo,4), 'and the average White Elo\
        Rating is ',round(av_white_elo,4),'. The average percentage relative to the number games in our database \
        given your filtering is ', round(percentage,2),'%. The average number of plays for your filtered database is ',round(filt_av_plays,2),\
        'The average White Elo rating in your filtered database is ',round(filt_white_elo,4),' and the average Black Elo is ',round(filt_black_elo,4),'.')




    


