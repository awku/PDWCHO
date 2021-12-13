from functools import wraps

from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from .db import App
from .forms import SignUpForm, LoginForm, RateBookForm, TagBookForm, RecommendUsersForm, RecommendBooksForm, \
    CreateAdminForm, CreateBookForm, EditBookForm, EditUserForm

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
                version = 'users followed by users I follow'
            elif selected == "2":
                books_data = None
                users_data = app.find_users_recommendations_similar_rating(user_id)
                version = 'users who similarly rated the same books I did'
        if book_form.is_valid():
            selected = book_form.cleaned_data.get("books_options")
            if selected == "1":
                users_data = None
                books_data = app.find_books_recommendations_following(user_id)
                version = 'books rated by users I follow'
            if selected == "2":
                users_data = None
                books_data = app.find_books_recommendations_user_also_read(user_id)
                version = 'books read by users who rated the same books I did'
            if selected == "3":
                users_data = None
                books_data = app.find_books_recommendations_similar_tags(user_id)
                version = 'books with common tags to the previously rated books'
            if selected == "4":
                users_data = None
                books_data = app.find_books_recommendations_similar_tags_author_weighted(user_id)
                version = 'books with common tags to the previously rated books or written by the same authors (weighted)'
    else:
        user_form = RecommendUsersForm()
        book_form = RecommendBooksForm()
    return render(request, 'dashboard.html',
                  {'user_form': user_form, 'book_form': book_form, 'users_data': users_data, 'books_data': books_data,
                   'version': version})


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
    return render(request, 'basic_form.html', {'form': form, 'page_title': 'Sign up', 'button_text': 'Sign up'})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get("password")
            user_password = app.find_login_info(email)
            if user_password:
                user_password = user_password[0]['password']
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
    return render(request, 'basic_form.html', {'form': form, 'page_title': 'Login', 'button_text': 'Login'})


def logout_view(request):
    if request.session.exists(request.session.session_key):
        if 'user_id' in request.session:
            request.session.pop("user_id")
        if 'admin' in request.session:
            request.session.pop("admin")
    return redirect('/books')


def books_view(request):
    if request.method == "GET":
        books_data = app.find_books()
        page = request.GET.get('page', 1)
        paginator = Paginator(books_data, 5)
        books = paginator.page(page)
        return render(request, 'books.html', {'books': books})


def search_view(request):
    if request.method == 'GET':
        is_logged_in = 'user_id' in request.session
        search_query = request.GET.get('search_box', None)
        search_results = app.find_search_results(search_query)
        results_data = []
        for row in search_results:
            if 'Book' in row['labels(nodes)']:
                results_data.append({'name': row['nodes']['title'], 'url': f"/book?isbn={row['nodes']['isbn']}"})
            elif 'Author' in row['labels(nodes)']:
                results_data.append({'name': row['nodes']['name'], 'url': f"/author?id={row['ID(nodes)']}"})
            elif 'Tag' in row['labels(nodes)']:
                results_data.append({'name': row['nodes']['name'], 'url': f"/tag?id={row['ID(nodes)']}"})
            elif 'User' in row['labels(nodes)'] and is_logged_in:
                results_data.append({'name': row['nodes']['name'], 'url': f"/user?id={row['ID(nodes)']}"})
        page = request.GET.get('page', 1)
        paginator = Paginator(results_data, 10)
        results = paginator.page(page)
        return render(request, 'search.html', {'results': results, 'query': search_query})


@logged_in
def book_view(request):
    if 'admin' in request.session:
        return book_admin_view(request)
    isbn = request.GET.get('isbn')
    book_data = app.find_book(isbn)
    if book_data:
        book_data = app.find_book(isbn)[0]
        user_id = request.session["user_id"]
        if request.method == "POST":
            form_function = request.POST.get('_function', '').lower()
            rate_form = RateBookForm()
            tag_form = TagBookForm()
            if form_function == 'tagging':
                tag_form = TagBookForm(request.POST)
                if tag_form.is_valid():
                    tag = tag_form.cleaned_data.get('tag')
                    app.create_tag(isbn, tag)
            if form_function == 'rating':
                rate_form = RateBookForm(request.POST)
                if rate_form.is_valid():
                    rating = rate_form.cleaned_data.get('rating')
                    app.create_rating(user_id, isbn, rating)
            is_rated = app.is_book_rated(user_id, isbn)
            book_data = app.find_book(isbn)[0]
            return render(request, 'book.html',
                          {'book': book_data, 'rate_form': rate_form, 'tag_form': tag_form, 'is_rated': is_rated})
        elif request.method == "GET":
            rate_form = RateBookForm()
            tag_form = TagBookForm()
            is_rated = app.is_book_rated(user_id, isbn)
            book_data = app.find_book(isbn)[0]
            return render(request, 'book.html',
                          {'book': book_data, 'rate_form': rate_form, 'tag_form': tag_form, 'is_rated': is_rated})
    else:
        return render(request, 'error.html')


@logged_admin
def book_admin_view(request):
    isbn = request.GET.get('isbn')
    book_data = app.find_book(isbn)
    if book_data:
        book_data = app.find_book(isbn)[0]
        if request.method == "POST":
            method = request.POST.get('_method', '').lower()
            if method == 'patch':
                form = EditBookForm(request.POST)
                if form.is_valid():
                    title = form.cleaned_data.get("title")
                    year = form.cleaned_data.get("year")
                    image = form.cleaned_data.get("image")
                    authors = form.cleaned_data.get("authors")
                    app.edit_book_with_authors(isbn, year, title, image, authors)
            elif method == 'delete':
                app.delete_book(isbn)
                return redirect('books')
        init_data = {'title': book_data['title'], 'isbn': book_data['isbn'], 'year': book_data['year'],
                     'image': book_data['image'],
                     'authors': ','.join(data['name'] for data in book_data['authors'])}
        form = EditBookForm(initial=init_data)
        return render(request, 'book_admin.html', {'form': form, 'book': book_data})
    else:
        return render(request, 'error.html')


@logged_in
def user_view(request):
    user1_id = int(request.session["user_id"])
    user2_id = int(request.GET.get('id'))
    user_data = app.find_user_by_id(user2_id)
    if user_data:
        user_data = user_data[0]
        if request.method == "POST":
            app.create_following(user1_id, user2_id)
        is_followed = 'followed' if len(app.is_user_followed(user1_id, user2_id)) > 0 else 'not followed'
        return render(request, 'user.html', {'user': user_data, 'can_follow': is_followed})
    else:
        return render(request, 'error.html')


@logged_in
def account_view(request):
    user_id = request.session["user_id"]
    if request.method == "POST":
        method = request.POST.get('_method', '').lower()
        if method == 'patch':
            if 'admin' not in request.session:
                form = EditUserForm(request.POST)
                if form.is_valid():
                    user_name = form.cleaned_data.get("name")
                    user_email = form.cleaned_data.get("email")
                    app.edit_user(user_id, user_name, user_email)
        elif method == 'delete':
            app.delete_user(user_id)
            return logout_view(request)
    user_init = app.find_user_data_by_id(user_id)[0]
    init_data = {'name': user_init['name'], 'email': user_init['email']}
    form = EditUserForm(initial=init_data) if 'admin' not in request.session else None
    user_data = app.find_user_by_id(user_id)[0]
    return render(request, 'account.html', {'user': user_data, 'form': form})


def author_view(request):
    if request.method == "GET":
        author_id = request.GET.get('id')
        author_data = app.find_author_by_id(author_id)
        if author_data:
            author_data = author_data[0]
            return render(request, 'author.html', {'author': author_data})
        else:
            return render(request, 'error.html')


def tag_view(request):
    if request.method == "GET":
        tag_id = request.GET.get('id')
        tag_data = app.find_tag_by_id(tag_id)
        if tag_data:
            tag_data = tag_data[0]
            return render(request, 'tag.html', {'tag': tag_data})
        else:
            return render(request, 'error.html')


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
    return render(request, 'basic_form.html', {'form': form, 'page_title': 'Create admin', 'button_text': 'Create'})


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
        form = CreateBookForm()
    return render(request, 'basic_form.html', {'form': form, 'page_title': 'Create book', 'button_text': 'Create'})
