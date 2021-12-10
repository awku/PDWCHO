from django.forms import forms, CharField, EmailField, FloatField, PasswordInput, BooleanField, RadioSelect


class SignUpForm(forms.Form):
    name = CharField(label='Name', max_length=100)
    email = EmailField(label='E-mail', max_length=100)
    password = CharField(label='Password', max_length=100, widget=PasswordInput())


class LoginForm(forms.Form):
    email = EmailField(label='E-mail', max_length=100)
    password = CharField(label='Password', max_length=100, widget=PasswordInput())


class RateBookForm(forms.Form):
    rating = FloatField(label='rating', min_value=0, max_value=5)


class TagBookForm(forms.Form):
    tag = CharField(label='tag', max_length=100)


class SearchForm(forms.Form):
    search_text = CharField(label='search_text', max_length=200)
    consider_following = BooleanField()


class RecommendBookForm(forms.Form):
    users_also_read = BooleanField()
    common_tags = BooleanField()
    common_tags_with_previously_read_books = BooleanField()
    common_tags_common_author = BooleanField()
    more_liked_by_users = BooleanField()
    with_more_liked_tags = BooleanField()
    top_books_from_similar_users = BooleanField()


user_choices = [
    (1, 'users followed by users I follow'),
    (2, 'users who similarly rated the same books I did'),
]

book_choices = [
    (1, 'books rated by users I follow'),
    (2, 'books read by users who rated the same books I did'),
    (3, 'books with common tags to the previously rated books'),
    (4, 'books with common tags to the previously rated books or wrote by the same authors (weighted)'),
]


class RecommendUsersForm(forms.Form):
    users_options = CharField(label='', widget=RadioSelect(choices=user_choices), empty_value=1)


class RecommendBooksForm(forms.Form):
    books_options = CharField(label='', widget=RadioSelect(choices=book_choices), empty_value=1)
