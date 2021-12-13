from decouple import config
from neo4j import GraphDatabase

from .queries import _delete_user, _create_and_return_user, _delete_following, _create_and_return_following, \
    _find_and_return_following, _delete_book, _add_and_return_book, _add_and_return_rating, \
    _delete_rating, _mass_upload, _find_and_return_users, _find_and_return_books, \
    _find_and_return_book, _find_and_return_user_by_id, _find_and_return_author_by_id, _find_and_return_tag_by_id, \
    _find_and_return_authors, _find_and_return_tags, _find_and_return_login_info, _is_book_rated, \
    _create_and_return_tag, _is_user_followed, _find_and_return_user, _find_and_return_books_similar_users, \
    _find_and_return_foaf_users, _find_and_return_recommendations_friends_also_read, \
    _find_and_return_recommendations_users_also_read, _find_and_return_recommendations_tags, \
    _find_and_return_recommendations_tags_author_weighted, _find_and_return_similar_users_by_ratings, \
    _add_and_return_book_with_authors, _edit_and_return_book_with_authors, _edit_and_return_user, _search, \
    _find_and_return_user_data_by_id


class App:

    def __init__(self):
        uri = "neo4j+s://{NEO4J_URI}".format(NEO4J_URI=config('NEO4J_URI'))
        user = config('NEO4J_USERNAME')
        password = config('NEO4J_PASSWORD')
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def delete_user(self, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(_delete_user, user_id)
            return result

    def create_user(self, user_name, user_email, user_password, admin=False):
        with self.driver.session() as session:
            result = session.write_transaction(_create_and_return_user, user_name, user_email, user_password, admin)
            return result

    def edit_user(self, user_id, user_name, user_email):
        with self.driver.session() as session:
            result = session.write_transaction(_edit_and_return_user, user_id, user_name, user_email)
            return result

    def find_search_results(self, text):
        with self.driver.session() as session:
            result = session.write_transaction(_search, text)
            return result

    def delete_following(self, user_email):
        with self.driver.session() as session:
            result = session.write_transaction(_delete_following, user_email)
            return result

    def create_following(self, user1_id, user2_id):
        with self.driver.session() as session:
            result = session.write_transaction(_create_and_return_following, user1_id, user2_id)
            return result

    def find_user(self, user_email):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_user, user_email)
            return result

    def find_users(self):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_users)
            return result

    def find_login_info(self, user_email):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_login_info, user_email)
            return result

    def find_following(self, user_email):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_following, user_email)
            return result

    def delete_book(self, isbn):
        with self.driver.session() as session:
            result = session.write_transaction(_delete_book, isbn)
            return result

    def mass_uploading_data(self, filename):
        with self.driver.session() as session:
            session.write_transaction(_mass_upload, filename)

    def create_book(self, isbn, year, title, image):
        with self.driver.session() as session:
            result = session.write_transaction(_add_and_return_book, isbn, year, title, image)
            return result

    def create_book_with_authors(self, isbn, year, title, image, authors):
        with self.driver.session() as session:
            result = session.write_transaction(_add_and_return_book_with_authors, isbn, year, title, image, authors)
            print(result)
            return result

    def edit_book_with_authors(self, isbn, year, title, image, authors):
        with self.driver.session() as session:
            result = session.write_transaction(_edit_and_return_book_with_authors, isbn, year, title, image, authors)
            return result

    def find_books(self):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_books)
            return result

    def find_tags(self):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_tags)
            return result

    def find_authors(self):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_authors)
            return result

    def find_book(self, isbn):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_book, isbn)
            return result

    def find_user_by_id(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_user_by_id, user_id)
            return result

    def find_user_data_by_id(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_user_data_by_id, user_id)
            return result

    def find_tag_by_id(self, tag_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_tag_by_id, tag_id)
            return result

    def find_author_by_id(self, author_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_author_by_id, author_id)
            return result

    def is_book_rated(self, user_id, isbn):
        with self.driver.session() as session:
            result = session.read_transaction(_is_book_rated, user_id, isbn)
            return result

    def is_user_followed(self, user1_id, user2_id):
        with self.driver.session() as session:
            result = session.read_transaction(_is_user_followed, user1_id, user2_id)
            for _ in result:
                return True
            return False

    def delete_rating(self, user_email, isbn):
        with self.driver.session() as session:
            result = session.write_transaction(_delete_rating, user_email, isbn)
            return result

    def create_rating(self, user_id, isbn, rating):
        with self.driver.session() as session:
            result = session.read_transaction(_add_and_return_rating, user_id, isbn, rating)
            return result

    def create_tag(self, book_isbn, tag_name):
        with self.driver.session() as session:
            result = session.read_transaction(_create_and_return_tag, book_isbn, tag_name)
            return result

    def find_books_recommendations(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_books_similar_users, user_id)
            return result

    def find_users_recommendations_foaf(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_foaf_users, user_id)
            return result

    def find_users_recommendations_similar_rating(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_similar_users_by_ratings, user_id)
            return result

    def find_books_recommendations_following(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_recommendations_friends_also_read, user_id)
            return result

    def find_books_recommendations_user_also_read(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_recommendations_users_also_read, user_id)
            return result

    def find_books_recommendations_similar_tags(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_recommendations_tags, user_id)
            return result

    def find_books_recommendations_similar_tags_author_weighted(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(_find_and_return_recommendations_tags_author_weighted, user_id)
            return result

# app = App()
# app.mass_uploading_data("..\\init_data\\books_queries.txt")
# app.mass_uploading_data("..\\init_data\\authors_queries.txt")
# app.mass_uploading_data("..\\init_data\\authors_books_queries.txt")
# app.mass_uploading_data("..\\init_data\\tags_queries.txt")
# app.mass_uploading_data("..\\init_data\\users_queries.txt")
# app.mass_uploading_data("..\\init_data\\users_ratings_queries.txt")
# app.mass_uploading_data("..\\init_data\\books_tags_queries1.txt")
# app.mass_uploading_data("..\\init_data\\books_tags_queries2.txt")
# app.mass_uploading_data("..\\init_data\\users_following_queries.txt")
# app.close()
