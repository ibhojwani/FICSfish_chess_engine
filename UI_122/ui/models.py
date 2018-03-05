from django.db import models

# Create your models here.

class Games(models.Model):
    FICSGamesDBGameNo = models.IntegerField(null=True)
    BlackElo = models.IntegerField(null=True)
    WhiteElo = models.IntegerField(null=True)
    Result = models.IntegerField(null=True)
    PlyCount = models.IntegerField(null=True)
