from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
import uuid
from datetime import date

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField(max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    picture = models.ImageField(upload_to='book_images/%Y/%m/%d/', null=True, blank=True, default='book_images/no_profile_picture.png')
    file = models.FileField(upload_to='book_pdf/%Y/%m/%d/', null=True, blank=True, default='book_pdf/no_pdf.pdf')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    class Meta:
        ordering = ['title']


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    STATUS_MAINTENANCE = 'm'
    STATUS_ON_LOAN = 'o'
    STATUS_AVAILABLE = 'a'
    STATUS_RESERVED = 'r'

    LOAN_STATUS = (
        (STATUS_MAINTENANCE, 'Maintenance'),
        (STATUS_ON_LOAN, 'On loan'),
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_RESERVED, 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default=STATUS_MAINTENANCE,
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"), ("can_create_book", "Create new book"), ("can_update_book", "Update book details"), ("can_delete_book", "Delete book"),)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    author_profile_picture = models.ImageField(upload_to='author_images/%Y/%m/%d/', null=True, blank=True, default='author_images/no_image.png')

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = (("can_create_author", "Create new author"), ("can_update_author", "Update author details"), ("can_delete_author", "Delete author"),)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    profile_picture = models.ImageField(upload_to='customer_profile_images/%Y/%m/%d/', null=True, blank=True,
                                        verbose_name="Profile Picture", default='author_images/no_image.png')
    phone_number = models.CharField(null=True, blank=True, max_length=10)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
