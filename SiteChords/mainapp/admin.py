from django.contrib import admin
from .models import Singer, Album, Song, ContentWithChords, Chord, ChordVariation

admin.site.register(Singer)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(ContentWithChords)
admin.site.register(Chord)
admin.site.register(ChordVariation)


