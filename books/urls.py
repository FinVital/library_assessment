# books/urls.py

from django.urls import path
from .views import (
    BookListCreateView, BookDetailView, AuthorListCreateView, 
    AuthorDetailView, FavoriteListCreateView, RegisterView
)

urlpatterns = [
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('authors/', AuthorListCreateView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('register/', RegisterView.as_view(), name='register'),
]
