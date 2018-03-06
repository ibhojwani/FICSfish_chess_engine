from django.contrib import admin

from chessboard.models import Invitation, Move

admin.site.register(Move)
admin.site.register(Invitation)
