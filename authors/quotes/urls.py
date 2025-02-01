from . import views
from django.urls import path

app_name = 'quotes'
urlpatterns = [
    path('', views.main, name="root"),
    path('<int:page>', views.main, name="root_paginate"),
    path('quote/', views.quote, name='quote'),
    path('tag/', views.tag, name='tag'),
    path('author/add/', views.add_author, name='add_author'),
    path('author/<str:author_id>/', views.author_view, name='author_view'),
    path('parse-website/', views.parse_website, name='parse_website'),
    path('switch-database/', views.switch_database, name='switch_database'),
    path('tag/<str:tag_name>/', views.quotes_by_tag_view, name='quotes_by_tag_view'),
]