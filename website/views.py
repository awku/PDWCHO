from functools import wraps

from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from .db import App
from .forms import SignUpForm, LoginForm, RateBookForm, TagBookForm, RecommendUsersForm, RecommendBooksForm, \
    CreateAdminForm, CreateBookForm

app = App()


def logged_in(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.exists(request.session.session_key) and 'user_id' in request.session:
            return function(request, *args, **kwargs)
        return redirect('login_url')

    return wrap


def logged_admin(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.exists(
                request.session.session_key) and 'user_id' in request.session and 'admin' in request.session:
            return function(request, *args, **kwargs)
        return redirect('login_url')

    return wrap


def index_view(request):
    return redirect('books')


def out_view(request):
    app.close()


@logged_in
def dashboard_view(request):
    users_data = None
    books_data = None
    user_id = request.session["user_id"]
    if request.method == "POST":
        user_form = RecommendUsersForm(request.POST)
        book_form = RecommendBooksForm(request.POST)
        if user_form.is_valid():
            selected = user_form.cleaned_data.get("users_options")
            if selected == "1":
                books_data = None
                users_data = app.find_users_recommendations_foaf(user_id)
            elif selected == "2":
                books_data = None
                users_data = app.find_users_recommendations_similar_rating(user_id)
        if book_form.is_valid():
            selected = book_form.cleaned_data.get("books_options")
            if selected == "1":
                users_data = None
                books_data = app.find_books_recommendations_following(user_id)
            if selected == "2":
                users_data = None
                books_data = app.find_books_recommendations_user_also_read(user_id)
            if selected == "3":
                users_data = None
                books_data = app.find_books_recommendations_similar_tags(user_id)
            if selected == "4":
                users_data = None
                books_data = app.find_books_recommendations_similar_tags_author_weighted(user_id)
    else:
        user_form = RecommendUsersForm()
        book_form = RecommendBooksForm()
    return render(request, 'dashboard.html',
                  {'user_form': user_form, 'book_form': book_form, 'users_data': users_data, 'books_data': books_data})


def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            email = form.cleaned_data.get("email")
            if not app.find_user(email):
                password = make_password(form.cleaned_data.get("password"))
                app.create_user(name, email, password)
        return redirect('login_url')

    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get("password")
            user_password = app.find_login_info(email)[0]['password']
            if user_password and check_password(password, user_password):
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                user_id = app.find_login_info(email)[0]['id']
                request.session["user_id"] = user_id
                if app.find_login_info(email)[0]['admin']:
                    request.session["admin"] = True
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.session.exists(request.session.session_key) and request.session["user_id"]:
        request.session.pop("user_id")
        request.session.pop("admin")
    return redirect('/books')


def books_view(request):
    if request.method == "GET":
        books_data = app.find_books()
        page = request.GET.get('page', 1)
        paginator = Paginator(books_data, 5)
        books = paginator.page(page)
        return render(request, 'books.html', {'books': books})


@logged_in
def book_view(request):
    isbn = request.GET.get('isbn')
    user_id = request.session["user_id"]
    book_data = app.find_book(isbn)[0]
    is_rated = app.is_book_rated(user_id, isbn)
    if request.method == "POST":
        rate_form = RateBookForm(request.POST)
        if rate_form.is_valid():
            rating = rate_form.cleaned_data.get('rating')
            app.create_rating(user_id, isbn, rating)
        tag_form = TagBookForm(request.POST)
        if tag_form.is_valid():
            tag = tag_form.cleaned_data.get('tag')
            app.create_tag(isbn, tag)
    else:
        rate_form = RateBookForm()
        tag_form = TagBookForm()
    return render(request, 'book.html',
                  {'book': book_data, 'rate_form': rate_form, 'tag_form': tag_form, 'is_rated': is_rated})


@logged_in
def user_view(request):
    user1_id = request.session["user_id"]
    user2_id = request.GET.get('id')
    user_data = app.find_user_by_id(user2_id)[0]
    if request.method == "POST":
        app.create_following(user1_id, user2_id)
    is_followed = 'followed' if app.is_user_followed(user1_id, user2_id) else 'not followed'
    return render(request, 'user.html', {'user': user_data, 'can_follow': is_followed})


@logged_in
def account_view(request):
    if request.method == "GET":
        user_id = request.session["user_id"]
        user_data = app.find_user_by_id(user_id)[0]
        return render(request, 'user.html', {'user': user_data, 'can_follow': 'no'})


def author_view(request):
    if request.method == "GET":
        author_id = request.GET.get('id')
        author_data = app.find_author_by_id(author_id)[0]
        return render(request, 'author.html', {'author': author_data})


def tag_view(request):
    if request.method == "GET":
        tag_id = request.GET.get('id')
        tag_data = app.find_tag_by_id(tag_id)[0]
        return render(request, 'tag.html', {'tag': tag_data})


@logged_in
def users_view(request):
    if request.method == "GET":
        users_data = app.find_users()
        page = request.GET.get('page', 1)
        paginator = Paginator(users_data, 10)
        users = paginator.page(page)
        return render(request, 'users.html', {'users': users})


def tags_view(request):
    if request.method == "GET":
        tags_data = app.find_tags()
        page = request.GET.get('page', 1)
        paginator = Paginator(tags_data, 10)
        tags = paginator.page(page)
        return render(request, 'tags.html', {'tags': tags})


def authors_view(request):
    if request.method == "GET":
        authors_data = app.find_authors()
        page = request.GET.get('page', 1)
        paginator = Paginator(authors_data, 10)
        authors = paginator.page(page)
        return render(request, 'authors.html', {'authors': authors})


@logged_admin
def create_admin_view(request):
    if request.method == "POST":
        form = CreateAdminForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if not app.find_user(email):
                password = make_password(form.cleaned_data.get("password"))
                app.create_user(user_name=None, user_email=email, user_password=password, admin=True)
                return redirect('home')
    else:
        form = CreateAdminForm()
    return render(request, 'create_admin.html', {'form': form})


@logged_admin
def create_book_view(request):
    if request.method == "POST":
        form = CreateBookForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data.get("isbn")
            if not app.find_book(isbn):
                title = form.cleaned_data.get("title")
                year = form.cleaned_data.get("year")
                image = form.cleaned_data.get("image")
                authors = form.cleaned_data.get("authors")
                app.create_book_with_authors(isbn, year, title, image, authors)
                return redirect('books')
    else:
        form = CreateAdminForm()
    return render(request, 'create_book.html', {'form': form})
