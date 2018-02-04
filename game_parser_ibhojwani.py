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


################## THIS IS FROM PA1 ##################


class TrieNode(object):

    def __init__(self):
        self.count = 0
        self.final = False
        self.children = {}
        return None

    def add_word(self, word):
        '''
        Adds word to Trie tree. *Assumes that word is not already in tree.*
        Therefore, is important to first check that word is not already
        added and or empty.

        Parameters:
            word: word to add, string

        returns None
        '''

        self.count += 1

        if len(word) == 0:
            self.final = True
            return None

        # below only deals with len(word) >1
        if word[0] not in self.children:
            self.children[word[0]] = TrieNode()

        self.children[word[0]].add_word(word[1:])

        return None

    def trace(self, w):
        '''
        traces a given word w through Trie tree to see if all elements
        of w are in the tree. If not, returns False.

        Parameters:
            w: string, characters to be tested

        returns tuple, with bool saying if traced word exists in tree
        and with number of counts at final node if it does exist.
        '''
        if len(w) == 0:
            if self.final == True:
                return (True, self.count)  # self.counts should == 1 here
            else:
                return (False, self.count)
        if w[0] not in self.children:
            return (False, 0)
        return self.children[w[0]].trace(w[1:])

    def gather_completions(self, prefix="", prev=""):
        '''
        Recursively searches for completions.

        Parameters:
            prefix: string, only in initial call
            prev: stem passed from previous recursive call
        returns: list of strings

        '''

        stem = prev
        completions = []
        status = self.trace(prefix)

        # checks if pref is not in dic or if there are no more continuations
        if status == (False, 0):
            return []

        if len(self.children) == 0:
            if stem == '':
                return ['']
            else:
                return [stem]

        # checks if current node is the final node in a continuation
        if status[0] == True:
            completions.append(stem)

        end_node = self
        for char in prefix:
            end_node = end_node.children[char]

        for next in end_node.children:
            completions = completions + end_node.children[next]\
                .gather_completions(prev=stem + next)

        return completions

    def __repr__(self):
        return("count: {}\n final: {} \n children {}"
               .format(self.count, self.final, self.children))
