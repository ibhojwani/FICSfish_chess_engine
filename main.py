'''
CS 12200 Project
Ginormous Anteaters
'''

import database_tools as dbt
import SunfishConvert as fish
import sqlite3


def play_game(db):
    moves = []
    views = []
    being_played = True
    conn = sqlite3.connect(db)

    #need to initialize board and shit

    while being_played:
        move = "RECEIEVD FROM JS BOARD"
        moves.append(move)
        best_move = dbt.return_best(conn, views)

    dbt.end_game(conn, views)

    return None


if __name__ == "__main__":
    play_game()
