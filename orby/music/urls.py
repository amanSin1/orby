from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.music_home, name='music_home'),
    # path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    # path('search/', views.search_music, name='search'),
    # path('playlists/', views.get_playlists, name='playlists'),
]