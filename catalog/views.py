import operator
import smtplib
from functools import reduce
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from catalog.models import Author, Book, BookInstance, Profile
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.generic import View
from django.core.mail.message import EmailMessage
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required
from catalog.forms import RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
STATUS_MAINTENANCE = 'm'
STATUS_ON_LOAN = 'o'
STATUS_AVAILABLE = 'a'
STATUS_RESERVED = 'r'


def index(request):
        num_books = Book.objects.all().count()
        num_instances = BookInstance.objects.all().count()
        num_instances_available = BookInstance.objects.filter(status__exact='a').count()
        num_authors = Author.objects.count()
        # Number of visits to this view, as counted in the session variable.
        num_visits = request.session.get('num_visits', 0)
        request.session['num_visits'] = num_visits + 1

        context = {
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_visits': num_visits,
        }
        return render(request, 'catalog/index.html', context=context)


@method_decorator(login_required, 'dispatch')
class BookListView(generic.ListView):
    model = Book
    paginate_by = 3


@method_decorator(login_required, 'dispatch')
class BookDetailView(generic.DetailView):
    model = Book


# @method_decorator(login_required, 'dispatch')
class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 3
    template_name = 'catalog/author_list.html'


@method_decorator(login_required, 'dispatch')
class AuthorDetailView(generic.DetailView):
    model = Author


class CustomerLoginView(View):
    def post(self, request):
        username_r = request.POST['customer_username']
        password_r = request.POST['customer_password']

        user = authenticate(request, username=username_r, password=password_r)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return HttpResponseRedirect(reverse('dashboard_staff', args=[]))
            else:
                return HttpResponseRedirect(reverse('dashboard_customer', args=[]))
        else:
            return HttpResponseRedirect(reverse('customer_login'))

    def get(self, request):
        return render(request, 'catalog/customer_login.html')


class CustomerSignUpView(View):
    def post(self, request):
        name_r = request.POST.get('customer_username')
        password_r = request.POST.get('customer_password')
        email_r = request.POST.get('customer_email')

        contact_number_r = request.POST.get('customer_contact_number')
        profile_picture_r = request.POST.get('customer_profile_picture')

        if checkemail(email_r):
            c = User.objects.create_user(username=name_r, password=password_r, email=email_r)
            c.save()

            p = Profile(user=c, phone_number=contact_number_r, profile_picture=profile_picture_r)
            p.save()

            return render(request, 'catalog/customer_login.html')
        else:
            return render(request, 'catalog/customer_signup.html')

    def get(self, request):
        return render(request, 'catalog/customer_signup.html')


def checkemail(email_r):
    try:
        validate_email(email_r)
    except ValidationError:
        False
    return True


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


def send_email(request):
    if request.user.is_authenticated:
        send_to = request.user.email
        username = request.user.username

    book = Book.objects.get(pk=int(request.POST.get('book_id')))
    book_title = str(book.title)
    book_author = str(book.author)
    book_pdf = book.file.path

    email_body = "Hello "+username+"\n\n Please find attachment your requested PDF file below \n\n Book: "+book_title+"\n Book Author: "+book_author+"\n\n"

    try:
        # send_mail('Book request', email_body, settings.EMAIL_HOST_USER, ['madhok.simran8@gmail.com'], fail_silently=False)
        email = EmailMessage(
            'Library Book request',
            email_body,
            'sender smtp gmail' + '<dolphin2016water@gmail.com>',
            [send_to],
        )
        email.attach_file(book_pdf, mimetype='application/pdf')
        email.send()
    except smtplib.SMTPException:
        return HttpResponseRedirect(reverse('index'))

    return HttpResponseRedirect(reverse('dashboard_customer', args=[]))


def borrow_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
            if request.user.is_authenticated:
                book_instance.borrower = request.user
                book_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=3)
                book_instance.status = STATUS_ON_LOAN
                book_instance.save()
                return HttpResponseRedirect(reverse('dashboard_customer'))

    context = {
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_detail.html', context)


# @method_decorator(login_required, 'dispatch')
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/dashboard_customer.html'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/dashboard_staff.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk = pk)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('dashboard_staff'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

def return_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    book_instance.status = STATUS_AVAILABLE
    book_instance.save()
    return HttpResponseRedirect(reverse('dashboard_customer'))


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'can_create_author'
    model = Author
    fields = '__all__'
    success_url = reverse_lazy('authors')


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'can_update_author'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    success_url = reverse_lazy('authors')


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'can_delete_author'
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_create_book'
    success_url = reverse_lazy('books')


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_update_book'
    success_url = reverse_lazy('books')


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_delete_book'
    success_url = reverse_lazy('books')


class BookSearchListView(BookListView):
    paginate_by = 3

    def get_queryset(self):
        result = super(BookSearchListView, self).get_queryset()

        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list))
            )

        return result


class AuthorSearchListView(AuthorListView):
    paginate_by = 3

    def get_queryset(self):
        result = super(AuthorSearchListView, self).get_queryset()

        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(first_name__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(last_name__icontains=q) for q in query_list))
            )

        return result
