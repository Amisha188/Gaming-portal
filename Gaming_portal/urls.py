from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name="logout"),
    path('index/', views.home, name="home"),
    path('Tetris/', views.tetris_game, name="tetris_game"),
    path('Snake/', views.snake_game, name="snake_game"),
    path('Sudoku/', views.sudoku_game, name='sudoku'),
    path('Tic/', views.tic, name="tic"),
]