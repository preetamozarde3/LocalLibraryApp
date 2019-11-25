from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('customer_login/', views.CustomerLoginView.as_view(), name='customer_login'),
    path('customer_signup/', views.CustomerSignUpView.as_view(), name='customer_signup'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('email_book/', views.send_email, name='email_book'),
    path('book/<uuid:pk>/return', views.return_book, name='return_book'),
    path('book/<uuid:pk>/borrow/', views.borrow_book, name='borrow_book'),
    path('dashboard_customer/', views.LoanedBooksByUserListView.as_view(), name='dashboard_customer'),
    path('dashboard_staff/', views.LoanedBooksAllListView.as_view(), name='dashboard_staff'),
    path('search_book/', views.BookSearchListView.as_view(), name='search_book'),
    path('search_author/', views.AuthorSearchListView.as_view(), name='search_author'),
]

urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
]

