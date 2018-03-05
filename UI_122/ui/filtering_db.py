#Constructing Query and Results 
#Priya Lingutla

import sqlite3
import os

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'database.db')

'''
Assuming that the dictionary output from the HTML is in the following form of:
output_dictionary = {
    min_B_ELO: type(int) >= 600 & less than max_B_ELO,
    max_B_ELO: type(int) <= 3000 & greater than min_B_ELO,
    min_W_ELO: type(int) >= 600 & less than max_W_ELO,
    max_W_ELO: type(int) <= 3000 & greater than min_W_ELO
}

'''

def filter_db(db,output_dictionary):
    '''
    This is a helper function that creates a query based on the output dictionary and
    returns the database.

    Input: db (sqlite3 database), output_dictionary (dict) which is the user input
    Output: db - filtered database given user input
    '''

    conn = sqlite3.connect(DATABASE_FILENAME) 
    cur = conn.cursor()
    
    output_list = [ output_dictionary[min_B_ELO], output_dictionary[max_B_ELO],
        output_dictionary[min_W_ELO], output_dictionary[max_W_ELO] ] 
    
    cur.execute('SELECT count (*) FROM games WHERE BlackElo >= ? AND \
     BlackElo < ? AND WhiteElo >= ? AND WhiteElo < ?',output_list) 

    return db

def get_statistics(db):
    '''
    This is a helper function that outputs statistics for a database in the
    following form: 
    (num_games, num_plays, gameID_list)

    Input: db
    Output: tupl
    '''
    #count number of rows in database

def return_statistics(db, output_dictionary):
    '''
    This is the main function that implements filtering the database
    based on user input. 
    '''
    filtered_db = filter_db(database.db,output_dictionary)

    #average plays in database only in filtered db
    #rows in gameID column in database to list only in filtered db
    return (percentage, av_plays, gameID_list)



