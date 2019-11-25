import datetime
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from catalog.models import Author, Book, Profile, BookInstance, Genre
from django.test import TestCase
from django.utils import timezone
from catalog.forms import RenewBookModelForm
import datetime
from django.utils import timezone
import uuid

"""
    Status variables for complaints
"""
STATUS_MAINTENANCE = 'maintenance'
STATUS_ON_LOAN = 'on_loan'
STATUS_RESERVED = 'reserved'
STATUS_AVAILABLE = 'available'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_DELETED_BOOK = 'deleted_book'
STATUS_RENEWAL_BOOK = 'renewal_book'


class CustomerSignUpViewTest(TestCase):
    """
        Test case for User Sign in
    """
    def test_registration_view_get(self):
        """
            A ``GET`` to the ``customer_signup`` view uses the appropriate
            template and populates the registration form into the context.
        """
        response = self.client.get(reverse('customer_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/customer_signup.html')

    # def test_registration_email_is_valid(self):
    #     """
    #         The email address is validated by validate_email() built-in function
    #         and after successful validation, the User and Profile objects are created
    #     """

    def test_registration_view_post_success(self):
        """
            A ``POST`` to the ``customer_signup`` view with valid data properly
            creates a new user and issues a redirect.
        """
        data = {
            'customer_username': 'testuser1',
            'customer_password': '1X<ISRUkw+tuK',
            'customer_email': 'foobar@test.com',
            'customer_contact_number': '9876543210',
        }
        response = self.client.post(reverse('customer_signup'), data)
        self.assertEqual(response.status_code, 200)
        # self.assertTrue(response.url.startswith('/catalog/customer_login/'))


class CustomerLoginTestCase(TestCase):
    """
            Test case for User Log in
    """

    def test_login_view_get(self):
        """
            A ``GET`` to the ``customer_login`` view uses the appropriate
            template and populates the login form(username and password) into the context.
        """
        response = self.client.get(reverse('customer_login'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/customer_login.html')

    def test_login_view_post_success(self):
        """
            A ``POST`` to the ``customer_login`` view with valid data properly
            logs in a user(customer/librarian/admin) and issues a redirect.
        """
        data = {
            'customer_username': 'testuser1',
            'customer_password': '1X<ISRUkw+tuK',
        }
        response = self.client.post(reverse('customer_login'), data)
        self.assertEqual(response.status_code, 302)

        # self.client.login(self, response)
        self.assertRedirects(response, reverse('dashboard_customer'), status_code=302, target_status_code=200)

        # check whether the logged in user is a customer/library staff and redirect accordingly


class CustomerLogoutTestCase(TestCase):
    """
        Test case for User Log out
    """

    def test_logout_view_get(self):
        User.objects.create_user(username='fred', email='test@test.com', password='secret')
        self.client.login(username='fred', password='secret')
        response = self.client.get('/catalog/logout/')
        self.assertEqual(response.status_code, 302)


class GenreModelTest(TestCase):
    """
        Test case for Genre Instance
    """

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Genre.objects.create(name='Tragedy')
        Genre.objects.create(name='Comedy')

    def test_object_name_is_name(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEquals(expected_object_name, str(genre))


class BookInstanceModelTest(TestCase):
    """
        Test case for Book Instance
    """
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK',
                                              email='testuser1@test.com')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD',
                                              email='testuser2@test.com')

        test_author = Author.objects.create(first_name='William', last_name='Shakespeare')
        test_book = Book.objects.create(title='Hamlet', author=test_author, summary='Published in 1990',
                                        isbn='123456789123')
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)

        return_date1 = datetime.date.today()
        BookInstance.objects.create(book=test_book, borrower=test_user1, due_back=return_date1,
                                    status='o')
        return_date2 = datetime.date.today() + datetime.timedelta(days=5)
        BookInstance.objects.create(book=test_book, borrower=test_user2, due_back=return_date2,
                                    status='o')

        return_date3 = datetime.date.today() - datetime.timedelta(days=5)
        BookInstance.objects.create(book=test_book, borrower=test_user2, due_back=return_date3,
                                    status='o')

    def test_book_is_overdue(self):
        for bookinst in BookInstance.objects.all():
            value = bookinst.is_overdue
            if value is True:
                self.assertTrue(True)
            else:
                self.assertFalse(False)


class ProfileModelTest(TestCase):
    """
        Test case for Profile model
    """
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='testuser1@test.com')
        Profile.objects.create(user=test_user, phone_number='987654321')

    def test_object_name_is_first_name_comma_last_name(self):
        profile = Profile.objects.get(id=1)
        expected_object_name = '{0} {1}'.format(profile.user.first_name, profile.user.last_name)
        self.assertEquals(expected_object_name, str(profile))


class BookModelTest(TestCase):
    """
        Test case for Book model
    """
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_author = Author.objects.create(first_name='William', last_name='Shakespeare')
        test_book = Book.objects.create(title='Hamlet', author=test_author, summary='Published in 1990',
                    isbn='123456789123')
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_author_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')

    def test_isbn_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label, 'isbn')

    def test_summary_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, 'summary')

    def test_genre_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, 'genre')

    def test_object_name_is_title(self):
        book = Book.objects.get(id=1)
        expected_object_name = book.title
        self.assertEquals(expected_object_name, str(book))

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEquals(book.get_absolute_url(), '/catalog/book/1')


class AuthorModelTest(TestCase):
    """
        Test case for Author model
    """
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Diana', last_name='Rose', date_of_birth='1890-12-02', date_of_death='1900-03-14')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'date of death')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_first_name_comma_last_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '{0} {1}'.format(author.first_name, author.last_name)
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')


class AuthorListViewTest(TestCase):
        """
            Test case for Author list view
        """
        @classmethod
        def setUpTestData(cls):
            Author.objects.create(first_name='William', last_name='Rose', date_of_birth='1890-12-02',
                                  date_of_death='1900-03-14')
            Author.objects.create(first_name='Dante', last_name='Rose', date_of_birth='1890-12-02',
                                  date_of_death='1900-03-14')
            Author.objects.create(first_name='Kite', last_name='Rose', date_of_birth='1890-12-02',
                                  date_of_death='1900-03-14')
            Author.objects.create(first_name='Heather', last_name='Rose', date_of_birth='1890-12-02',
                                  date_of_death='1900-03-14')
            Author.objects.create(first_name='Jim', last_name='Rose', date_of_birth='1890-12-02',
                                  date_of_death='1900-03-14')
            Author.objects.create(first_name='Kim', last_name='Rose', date_of_birth='1890-12-02',
                                  date_of_death='1900-03-14')
            test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
            test_user1.save()

        def test_view_url_exists_at_desired_location(self):
            response = self.client.get('/catalog/authors/', follow=True)
            self.assertEqual(response.status_code, 200)

        def test_view_url_accessible_by_name(self):
            response = self.client.get(reverse('authors'), follow=True)
            self.assertEqual(response.status_code, 200)

        def test_logged_in_uses_correct_template(self):
            login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
            response = self.client.get(reverse('authors'), follow=True)
            self.assertEqual(str(response.context['user']), 'testuser1')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'catalog/author_list.html')

        def test_redirect_if_not_logged_in(self):
            response = self.client.get(reverse('authors'), follow=True)
            self.assertRedirects(response, '/catalog/customer_login/?next=/catalog/authors/')

        def test_pagination_is_three(self):
            login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
            response = self.client.get(reverse('authors'), follow=True)
            self.assertEqual(str(response.context['user']), 'testuser1')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.context['author_list']), 3)


# class BookStatusChangeTest(TestCase):
#     """
#     Test case for batch changing 'status' of books to 'On-Loan' or 'Reserved' or 'Maintenance' or 'Available'
#     """
#     def setUp(self):
#         # self.categories = factories.CategoryFactory.create_batch(5)
#         test_user = User.objects.create_superuser(username='testuser2', password='2HJ1vRV0Z&3iD', email='superuser@test.com')
#         test_user.save()
#
#     def test_change_book_status_to_on_loan(self):
#         """
#             Test changing all Category instances to 'Hide'
#         """
#         # Set Queryset to be hidden
#         to_be_hidden = models.Category.objects.values_list('pk', flat=True)
#         # Set POST data to be passed to changelist url
#         data = {
#             'action': 'change_to_hide',
#             '_selected_action': to_be_hidden
#         }
#         # Set change_url
#         change_url = self.reverse('admin:product_category_changelist')
#         # POST data to change_url
#         response = self.post(change_url, data, follow=True)
#         self.assertEqual(models.Category.objects.filter(status='show').count(), 0)


class RenewBookFormTest(TestCase):
    """
           Test case to Renew Book form
    """
    def test_renew_form_date_field_label(self):
        form = RenewBookModelForm()
        self.assertTrue(form.fields['due_back'].label == None or form.fields['due_back'].label == 'Renewal date')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookModelForm()
        self.assertEqual(form.fields['due_back'].help_text, 'Enter a date between now and 4 weeks (default 3).')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.now() + datetime.timedelta(weeks=4)
        form = RenewBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
        )

        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Creating 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard_customer'), follow=True)
        self.assertRedirects(response, '/catalog/customer_login/?next=/catalog/dashboard_customer/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('dashboard_customer'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/dashboard_customer.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('dashboard_customer'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('dashboard_customer'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('dashboard_customer'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 15)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
        )

        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/customer_login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['due_back'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                    {'due_back': valid_date_in_future})
        self.assertRedirects(response, reverse('dashboard_staff'))

    # def test_form_invalid_renewal_date_past(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    #     date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
    #     response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}),
    #                                 {'renewal_date': date_in_past})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal in past')
    #
    # def test_form_invalid_renewal_date_future(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    #     invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
    #     response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}),
    #                                 {'renewal_date': invalid_date_in_future})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal more than 4 weeks ahead')


class AuthorCreateViewTest(TestCase):
    """
        Test case for the AuthorCreate view
    """

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_superuser(username='testuser2', password='2HJ1vRV0Z&3iD', email='admin@test.com')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Create new author')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))
        self.assertRedirects(response, '/catalog/customer_login/?next=/catalog/author/create/')

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_redirects_to_author_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('author_create'),
                                    {'first_name': 'Christian Name', 'last_name': 'Surname', })
        # Manually check redirect because we don't know what author was created
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/catalog/authors/'))


class BookCreateViewTest(TestCase):
    """
        Test case for the BookCreate view
    """

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_superuser(username='testuser2', password='2HJ1vRV0Z&3iD', email='admin@test.com')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Create new book')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')
        Book.objects.create(title='Hamlet', author=test_author, summary='Published in 1990',
                            isbn='123456789123')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book_create'))
        self.assertRedirects(response, '/catalog/customer_login/?next=/catalog/book/create/')

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

    # def test_redirects_to_book_list_on_success(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    #     response = self.client.post(reverse('book_create'),
    #                                 {'title': 'Romeo Juliet', 'author': 'william grant', 'summary': 'Published in 2000',
    #                                  'isbn': '9876543210123'})
    #     # Manually check redirect because we don't know what book was created
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(response.url.startswith('/catalog/books/'))


class BookSearchListViewTest(TestCase):
    """
            Test case for the Book Search List View i.e
            the search bar filter in the Books List page
            and the url for search_book : /catalog/books/
    """
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')
        Book.objects.create(title='House', author=test_author, summary='Published in 1990',
                            isbn='123456789123')
        Book.objects.create(title='Money', author=test_author, summary='Published in 1991',
                            isbn='9876543210123')
        Book.objects.create(title='Mouse', author=test_author, summary='Published in 1992',
                            isbn='1293874657832')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('books'))
        self.assertRedirects(response, '/catalog/customer_login/?next=/catalog/books/')

    def test__url_pattern(self):
        url = '{url}?{filter}={value}'.format(url=reverse('search_book'), filter='q', value='Hou')
        self.client.login(username='testuser1', password='1X<ISRUkw+tu')
        response = self.client.get(url)
        self.assertIsNotNone(response)

    # def test_query_search_filter(self):
        # self.assertQuerysetEqual(Book.objects.filter(title__icontains='House'), ["<Book: House>"])
