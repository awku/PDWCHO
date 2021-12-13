from django.forms import forms, CharField, EmailField, FloatField, PasswordInput, RadioSelect, IntegerField


class SignUpForm(forms.Form):
    name = CharField(label='Name', max_length=100)
    email = EmailField(label='E-mail', max_length=100)
    password = CharField(label='Password', max_length=100, widget=PasswordInput())


class LoginForm(forms.Form):
    email = EmailField(label='E-mail', max_length=100)
    password = CharField(label='Password', max_length=100, widget=PasswordInput())


class RateBookForm(forms.Form):
    rating = FloatField(label='', min_value=0, max_value=5)


class TagBookForm(forms.Form):
    tag = CharField(label='', max_length=100)


class CreateAdminForm(forms.Form):
    email = EmailField(label='E-mail', max_length=100)
    password = CharField(label='Password', max_length=100, widget=PasswordInput())


class CreateBookForm(forms.Form):
    title = CharField(label='Title', max_length=100)
    isbn = CharField(label='ISBN', max_length=100)
    year = IntegerField(label='Year')
    image = CharField(label='Cover Image', max_length=400)
    authors = CharField(label='Authors', max_length=400,
                        help_text="For more than 1 author, please separate each with a comma (,)")


class EditBookForm(forms.Form):
    title = CharField(label='Title', max_length=100)
    year = IntegerField(label='Year')
    image = CharField(label='Cover Image', max_length=400)
    authors = CharField(label='Authors', max_length=400,
                        help_text="For more than 1 author, please separate each with a comma (,)")


class EditUserForm(forms.Form):
    name = CharField(label='Name', max_length=100)
    email = EmailField(label='E-mail', max_length=100)


user_choices = [
    (1, 'users followed by users I follow'),
    (2, 'users who similarly rated the same books I did'),
]

book_choices = [
    (1, 'books rated by users I follow'),
    (2, 'books read by users who rated the same books I did'),
    (3, 'books with common tags to the previously rated books'),
    (4, 'books with common tags to the previously rated books or written by the same authors (weighted)'),
]


class RecommendUsersForm(forms.Form):
    users_options = CharField(label='', widget=RadioSelect(choices=user_choices), empty_value=1)


class RecommendBooksForm(forms.Form):
    books_options = CharField(label='', widget=RadioSelect(choices=book_choices), empty_value=1)
