from django.urls import path

from .views import index_view, dashboard_view, register_view, login_view, logout_view, users_view, books_view, \
    book_view, user_view, author_view, tag_view, authors_view, tags_view, account_view, out_view, create_book_view, \
    create_admin_view

urlpatterns = [
    path('', index_view, name="home"),
    path('dashboard/', dashboard_view, name="dashboard"),
    path('login/', login_view, name="login_url"),
    path('register/', register_view, name="register_url"),
    path('logout/', logout_view, name="logout"),
    path('users/', users_view, name="users"),
    path('user/', user_view, name="user"),
    path('books/', books_view, name="books"),
    path('book/', book_view, name="book"),
    path('author/', author_view, name="author"),
    path('authors/', authors_view, name="authors"),
    path('tag/', tag_view, name="tag"),
    path('tags/', tags_view, name="tags"),
    path('my_account/', account_view, name="account"),
    path('quit/', out_view, name="out"),
    path('create_book/', create_book_view, name="create_book"),
    path('create_admin/', create_admin_view, name="create_admin")
]
