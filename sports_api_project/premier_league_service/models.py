from django.db import models

# This file is where you would define your database models.
#
# For example, if you wanted to save the league table data over time
# for your analytics, you might create a model like this:
#
# class LeagueTableEntry(models.Model):
#     season = models.CharField(max_length=10)
#     position = models.IntegerField()
#     team = models.CharField(max_length=100)
#     played = models.IntegerField()
#     wins = models.IntegerField()
#     draws = models.IntegerField()
#     losses = models.IntegerField()
#     points = models.IntegerField()
#     date_fetched = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         # This ensures you don't save the same team for the same season twice
#         unique_together = ('season', 'team') 
#
# For now, we are just proxying the live API, so no models are needed.
# Your services.py file would be updated to write to this model
# instead of just returning the data.