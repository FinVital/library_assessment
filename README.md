Django API Documentation
Overview
This documentation outlines the setup and functionality of a Django RESTful API designed for managing books and authors. The API includes user authentication, search functionality, and a recommendation system. This guide also explains the design of the models, the similarity algorithm used for recommendations, and testing response times of the endpoints.

1. Models Design and Logic
Models
Author Model
python
Copy code
class Author(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
name: Represents the author's name.
about: An optional text field for additional information about the author.
The __str__ method returns the author's name, which is useful for displaying instances in the Django admin interface and in string representations.

Book Model
python
Copy code
class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    num_pages = models.IntegerField()
    genre = models.CharField(max_length=255, blank=True, null=True)  # Added genre field

    def __str__(self):
        return self.title
title: The title of the book.
description: A text field describing the book.
author: A foreign key linking to the Author model.
publication_date: The date when the book was published.
isbn: The ISBN of the book (unique).
num_pages: Number of pages in the book.
genre: A text field for the genre of the book (optional).
The __str__ method returns the book title, which is useful for display purposes.

Favorite Model
python
Copy code
class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorited_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')
user: A foreign key linking to the Django User model.
book: A foreign key linking to the Book model.
The unique_together constraint ensures that each user can only have one favorite entry per book.

2. Similarity Algorithm for Recommendations
Similarity Algorithm
The recommendation logic is implemented in the get_recommendations method:

python
Copy code
def get_recommendations(self, user):
    favorite_books = Favorite.objects.filter(user=user).values_list('book_id', flat=True)
    
    if not favorite_books:
        return []

    # Example: Recommend books by the same genre as user's favorites
    favorite_genres = Book.objects.filter(id__in=favorite_books).values_list('genre', flat=True).distinct()
    recommended_books = Book.objects.filter(genre__in=favorite_genres).exclude(id__in=favorite_books).distinct()[:5]
    
    return BookSerializer(recommended_books, many=True).data
Explanation:

Retrieve Favorite Books: Get a list of book IDs that the user has favorited.
Find Favorite Genres: Get the genres of these favorite books.
Recommend Books: Find books that share these genres, excluding those already favorited by the user. Limit the recommendations to 5 books.
3. API Endpoints
Endpoints
User Authentication
Register: POST /api/register/

Request Body: { "username": "", "password": "", "email": "" }
Response: JWT tokens (access and refresh).
Login: POST /api/login/

Request Body: { "username": "", "password": "" }
Response: JWT tokens (access and refresh).
Books
List/Create Books: GET/POST /api/books/

GET: List all books, optionally filter by search query.
POST: Create a new book.
Retrieve/Update/Delete Book: GET/PUT/DELETE /api/books/<int:pk>/

GET: Retrieve a specific book by ID.
PUT: Update a book by ID.
DELETE: Delete a book by ID.
Authors
List/Create Authors: GET/POST /api/authors/

GET: List all authors.
POST: Create a new author.
Retrieve/Update/Delete Author: GET/PUT/DELETE /api/authors/<int:pk>/

GET: Retrieve a specific author by ID.
PUT: Update an author by ID.
DELETE: Delete an author by ID.
Favorites
List/Create Favorites: GET/POST /api/favorites/

GET: List all favorite books for the authenticated user.
POST: Add a book to favorites (up to 20 books).
Delete Favorite: DELETE /api/favorites/

Request Body: { "book_id": <int> }
Response: Confirmation of removal or error if not found.
Testing Endpoints with Postman
1. Register a User:

URL: POST http://127.0.0.1:8000/api/register/
Body: JSON { "username": "testuser", "password": "testpassword", "email": "test@example.com" }
2. Login:

URL: POST http://127.0.0.1:8000/api/login/
Body: JSON { "username": "testuser", "password": "testpassword" }
3. Search Books:

URL: GET http://127.0.0.1:8000/api/books/?search=Harry
Headers: Authorization: Bearer <access_token>
4. Add a Favorite Book:

URL: POST http://127.0.0.1:8000/api/favorites/
Body: JSON { "book_id": 1 }
Headers: Authorization: Bearer <access_token>
5. Remove a Favorite Book:

URL: DELETE http://127.0.0.1:8000/api/favorites/
Body: JSON { "book_id": 1 }
Headers: Authorization: Bearer <access_token>
Summary
This documentation covers the design of the Django models, the recommendation algorithm used for suggesting books, and the API endpoints for managing books, authors, and user favorites. Testing should be performed using tools like Postman to ensure that all endpoints function as expected and to check for any issues with response times or data handling.
