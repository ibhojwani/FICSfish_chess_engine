from django.shortcuts import render
from django.http import JsonResponse
from database_tools import return_best, translate_moves_to_int, translate_int_to_move, drop_views
import sqlite3
import os




DATA_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_FILENAME = os.path.join(DATA_DIR, 'database.db')
views = []

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

def move_generator(request):
    conn = sqlite3.connect(DATABASE_FILENAME)
    try:
        moves = request.GET.get('moves', None)
        split_list = moves.split()
        last_move = split_list[-1]
        best_move = return_best(conn, views, last_move)



        data = {'m': best_move}
        return JsonResponse(data)

    except:
        drop_views(views, conn)
