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
    return render(request, 'chess.html', {})

def undo(request):
    conn = sqlite3.connect(DATABASE_FILENAME)
    undo = request.GET.get('undo', False)
    if undo:
        del filters[-1]
    temp = {'irrelevant': 5}
    return JsonResponse(temp)

def move_generator(request):
    conn = sqlite3.connect(DATABASE_FILENAME)
    moves = request.GET.get('moves', None)
    split_list = moves.split()
    if split_list == []:
        best_move = return_best(conn, filters)
    else:
        last_move = split_list[-1]
        best_move = return_best(conn, filters, last_move)


    if best_move is None:
        print("CANT USE DATA, USING SUNFISH")
        white = request.GET.get('w', True)
        print("The next turn is white: ", white)
        if white:
            best_move = IntegrateSunfish.modified_sunfish(moves, "White")
        else:
            best_move = IntegrateSunfish.modified_sunfish(moves, "Black")

    data = {'m': best_move}
    print("RETURNING: ", data)
    return JsonResponse(data)
