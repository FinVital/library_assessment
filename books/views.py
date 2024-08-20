# books/views.py

from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Count
from django.contrib.auth.models import User  # Add this import
from .models import Book, Author, Favorite
from .serializers import BookSerializer, AuthorSerializer, FavoriteSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Book.objects.all()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query)
            )
        return queryset

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# books/views.py

from django.shortcuts import get_object_or_404

class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book exists
        book = get_object_or_404(Book, id=book_id)

        if Favorite.objects.filter(user=user).count() >= 20:
            return Response({"error": "You can only have up to 20 favorite books."}, status=status.HTTP_400_BAD_REQUEST)

        favorite, created = Favorite.objects.get_or_create(user=user, book=book)
        if not created:
            return Response({"error": "Book is already in favorites."}, status=status.HTTP_400_BAD_REQUEST)

        # Call recommendation logic after adding a favorite
        recommendations = self.get_recommendations(user)

        return Response({
            "message": "Book added to favorites.",
            "recommendations": recommendations
        }, status=status.HTTP_201_CREATED)


    def delete(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        favorite = Favorite.objects.filter(user=user, book_id=book_id).first()
        if favorite:
            favorite.delete()
            return Response({"message": "Book removed from favorites."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Book not found in favorites."}, status=status.HTTP_404_NOT_FOUND)

    def get_recommendations(self, user):
        favorite_books = Favorite.objects.filter(user=user).values_list('book_id', flat=True)
        
        if not favorite_books:
            return []

        # Recommend books by the same author, excluding those already in favorites
        recommended_books = Book.objects.filter(author__books__in=favorite_books).exclude(id__in=favorite_books).distinct()[:5]
        
        return BookSerializer(recommended_books, many=True).data

class RegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
