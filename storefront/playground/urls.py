from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('game_feed', views.game_feed, name='game_feed'),
    path('description', views.description, name='description')
]