from django.shortcuts import render
from django.http import JsonResponse
from database_tools import return_best, translate_moves_to_int, translate_int_to_move
import sqlite3
import IntegrateSunfish
import os




DATA_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_FILENAME = os.path.join(DATA_DIR, 'best.db')
filters = []

'''
import json
import time

from datetime import datetime

from django.db.models import Q, F
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User, AnonymousUser

from chessboard.models import Move, Invitation
'''

def board(request):
    '''
    This just renders the html that has the chess board and the game and what not
    '''
    return render(request, 'chess.html', {})

def reset(request):
    '''
    This function takes a request that was sent when the reset button was pushed and
    resets filters so that best move can be calculated again
    '''
    undo = request.GET.get('reset', False)
    if undo:
        filters.clear()
    temp = {'irrelevant': 5} #need to return something JSON so this was what we did
    return JsonResponse(temp)

def undo(request):
    '''
    This function takes a request sent from the pressing of the undo button
    and removes the first element of the filters list to be able to continue
    effectively computing the next best move
    '''

    undo = request.GET.get('undo', False)
    if undo:
        filters.pop(0)
    temp = {'irrelevant': 5} #same as Above
    return JsonResponse(temp)

def move_generator(request):
    '''
    This function takes the request of the game as every move is played and Returns
    the next best move.
    '''
    conn = sqlite3.connect(DATABASE_FILENAME) #creates a connection to db
    moves = request.GET.get('moves', None) #Gets the string of moves

    split_list = moves.split() #splits the moves by spaces
    if split_list == []: #returns the move if there have been None
        best_move = return_best(conn, filters)
    else:
        last_move = split_list[-1] #gets the last move specifically
        best_move = return_best(conn, filters, last_move) #returns the best move


    if best_move is None: #if there is no more data
        white = request.GET.get('w', False) #Gets whose turn it is
        if white == "true": #if the next is white, gets the best white move
            best_move = IntegrateSunfish.modified_sunfish(moves, next = "White")
        else: #else, gets the best black move
            best_move = IntegrateSunfish.modified_sunfish(moves, next = "Black")

    '''
    returns the next best move as a dictionary->JsonResponse
    '''

    data = {'m': best_move}
    return JsonResponse(data)
