
from django.conf.urls import url, include
from . import views


from django.conf import settings
from django.contrib import admin

'''
from chessboard.views import ChessView, MoveView, InvitationView, InvitationListView, AcceptorRejectView
'''
admin.autodiscover()
'''
urlpatterns = [
    url(r'^$', ChessView.as_view(template_name='chess.html'), name='chess'),
    url(r'^ajax/test/$', views.test, name='test'),
]
'''
urlpatterns = [
    url(r'^$', views.board, name='board'),
    url(r'^views/move_generator/$', views.move_generator, name='move_generator'),
    url(r'^views/undo/$', views.undo, name='undo'),
]
