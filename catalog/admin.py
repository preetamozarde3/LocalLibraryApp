from django.contrib import admin
from catalog.models import Author, Genre, Book, BookInstance, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
STATUS_MAINTENANCE = 'm'
STATUS_ON_LOAN = 'o'
STATUS_AVAILABLE = 'a'
STATUS_RESERVED = 'r'

STATUS_CHOICES = (
    (STATUS_MAINTENANCE, 'm'),
    (STATUS_ON_LOAN, 'o'),
    (STATUS_AVAILABLE, 'a'),
    (STATUS_RESERVED, 'r')
)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death'), 'author_profile_picture']


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    filter_horizontal = ('genre',)
    list_filter = ('author',)
    inlines = [BooksInstanceInline]


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
    actions = ['book_onloan', 'book_available', 'book_maintenance', 'book_reserved']

    def book_onloan(self, request, queryset):
        queryset.update(status=STATUS_ON_LOAN)
    book_onloan.short_description = "Mark book status - On Loan"

    def book_available(self, request, queryset):
        queryset.update(status=STATUS_AVAILABLE)

    book_available.short_description = "Mark book status - Available"

    def book_maintenance(self, request, queryset):
        queryset.update(status=STATUS_MAINTENANCE)

    book_maintenance.short_description = "Mark book status - Maintenance"

    def book_reserved(self, request, queryset):
        queryset.update(status=STATUS_RESERVED)

    book_reserved.short_description = "Mark book status - Reserved"


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

