import logging

from neo4j.exceptions import ServiceUnavailable


def _delete_user(tx, user_id):
    query = "MATCH (p:User) WHERE ID(p) = $user_id DETACH DELETE p"
    result = tx.run(query, user_id=user_id)
    try:
        return [{"name": row["p"]["name"], "email": row["p"]["email"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _create_and_return_user(tx, user_name, user_email, user_password, is_admin):
    query = ("CREATE (p:User { "
             "name: $user_name, email: $user_email, password: $user_password, admin: $is_admin "
             "}) RETURN p")
    result = tx.run(query, user_name=user_name, user_email=user_email, user_password=user_password, is_admin=is_admin)
    try:
        return [{"name": row["p"]["name"], "email": row["p"]["email"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _edit_and_return_user(tx, user_id, user_name, user_email, user_password, is_admin):
    query = ("MATCH (p:User) WHERE ID(p) = $user_id "
             "SET p = {name: $user_name, email: $user_email, password: $user_password, admin: $is_admin }"
             "}) RETURN p")
    result = tx.run(query, user_id=user_id, user_name=user_name, user_email=user_email, user_password=user_password,
                    is_admin=is_admin)
    try:
        return [{"name": row["p"]["name"], "email": row["p"]["email"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _delete_following(tx, user_email):
    query = (
        "MATCH (p:User {email : $user_email})-[r:FOLLOWS]->()"
        "DELETE r"
    )
    result = tx.run(query, user_email=user_email)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _create_and_return_following(tx, user1_id, user2_id):
    query = (
        f"MATCH (u1:User) WHERE ID(u1) = {user1_id} "
        f"MATCH (u2:User) WHERE ID(u2) = {user2_id} "
        "CREATE (u1)-[:FOLLOWS]->(u2) "
        "RETURN u1, u2"
    )
    result = tx.run(query)
    try:
        return [{"u1": [row["u1"]["name"], row["u1"]["email"]], "u2": [row["u2"]["name"], row["u2"]["email"]]}
                for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _find_and_return_password(tx, user_email):
    query = (
        "MATCH (p:User) "
        "WHERE p.email = $user_email "
        "RETURN p.password AS password"
    )
    result = tx.run(query, user_email=user_email)
    return [row["password"] for row in result]


def _find_and_return_login_info(tx, user_email):
    query = (
        "OPTIONAL MATCH (p:User) "
        "WHERE p.email = $user_email "
        "RETURN p.password AS password, ID(p) as id, p.admin as admin"
    )
    result = tx.run(query, user_email=user_email)
    return [{"password": row["password"], "id": row['id'], "admin": row['admin']} for row in result]


def _find_and_return_users(tx):
    query = (
        "MATCH (p:User) "
        "RETURN p.name AS name, ID(p) AS id"
    )
    result = tx.run(query)
    return [{"name": row["name"], "id": row["id"]} for row in result]


def _find_and_return_user(tx, user_email):
    query = (
        "MATCH (p:User {email: '$user_email'}) "
        "RETURN p.name AS name, ID(p) AS id"
    )
    result = tx.run(query, user_email=user_email)
    return [{"name": row["name"], "id": row["id"]} for row in result]


def _find_and_return_user_by_id(tx, user_id):
    query = (
        "MATCH (p:User) "
        f"WHERE ID(p) = {user_id} "
        "OPTIONAL MATCH (p)-[r:RATED]->(b:Book) "
        "with p, collect({ isbn: b.isbn, title: b.title, rating: r.rating }) as books "
        "OPTIONAL MATCH (p)-[:FOLLOWS]->(u:User) "
        "with p, books, collect({ id: ID(u), name: u.name }) as users "
        "RETURN p.name as name, books, users"
    )
    result = tx.run(query)
    return [{"name": row["name"], "books": row["books"], "users": row["users"]} for row in result]


def _find_and_return_author_by_id(tx, author_id):
    query = (
        "OPTIONAL MATCH (p:Author) "
        f"WHERE ID(p) = {author_id} "
        "MATCH (p)-[r:WROTE]->(b:Book) "
        "with p, collect({ isbn: b.isbn, title: b.title}) as books "
        "RETURN p.name as name, books"
    )
    result = tx.run(query)
    return [{"name": row["name"], "books": row["books"]} for row in result]


def _find_and_return_tag_by_id(tx, tag_id):
    query = (
        "OPTIONAL MATCH (p:Tag) "
        f"WHERE ID(p) = {tag_id} "
        "MATCH (p)<-[r:IN_TAG]-(b:Book) "
        "with p, collect({ isbn: b.isbn, title: b.title}) as books "
        "RETURN p.name as name, books"
    )
    result = tx.run(query)
    return [{"name": row["name"], "books": row["books"]} for row in result]


def _find_and_return_following(tx, user_email):
    query = ("OPTIONAL MATCH (p1:User) WHERE p1.email = $user_email "
             "MATCH (p1)-[:FOLLOWS]-(p2:User) "
             "RETURN p2"
             )
    result = tx.run(query, user_email=user_email)
    try:
        return [{"p2": [row["p2"]["name"], row["p2"]["email"]]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _delete_book(tx, isbn):
    query = "MATCH (b:Book { isbn: $isbn }) DETACH DELETE b "
    result = tx.run(query, isbn=isbn)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _add_and_return_book(tx, isbn, year, title, image):
    query = "CREATE (p:Book { isbn: $isbn, year: $year, title: $title, " \
            "image: $image }) RETURN p "
    result = tx.run(query, isbn=isbn, year=year, title=title, image=image)
    try:
        return [
            {"isbn": row["p"]["isbn"], "year": row["p"]["year"],
             "title": row["p"]["title"], "image": row["p"]["image"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _add_and_return_book_with_authors(tx, isbn, year, title, image, authors):
    query = ("CREATE (p:Book { "
             f"isbn: '{isbn}'"
             ", year: $year, title: $title, "
             "image: $image }) "
             f"FOREACH (author_name IN split('{authors}', ',') "
             "| MERGE (a:Author {name: trim(author_name)})-[:WROTE]->(p)) "
             "RETURN p ")
    result = tx.run(query, isbn=isbn, year=year, title=title, image=image)
    try:
        return [
            {"isbn": row["p"]["isbn"], "year": row["p"]["year"],
             "title": row["p"]["title"], "image": row["p"]["image"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _edit_and_return_book_with_authors(tx, isbn, year, title, image, authors):
    query = ("MATCH (b:Book {"
             f"isbn: '{isbn}'"
             "})<-[r:WROTE]-(:Author) DELETE r "
             "SET b = {year: $year, title: $title, image: $image, "
             f"isbn: '{isbn}'"
             "} "
             f"FOREACH (author_name IN split('{authors}', ',') "
             "| MERGE (a:Author {name: trim(author_name)})-[:WROTE]->(b)) "
             "RETURN b ")
    result = tx.run(query, year=year, title=title, image=image)
    try:
        return [
            {"isbn": row["b"]["isbn"], "year": row["b"]["year"],
             "title": row["b"]["title"], "image": row["b"]["image"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _find_and_return_books(tx):
    query = ("MATCH (p:Book)<-[r:RATED]-() "
             "RETURN p, avg(r.rating) AS average")
    result = tx.run(query)
    return [
        {"isbn": row["p"]["isbn"], "year": row["p"]["year"], "title": row["p"]["title"],
         "image": row["p"]["image"], "average": round(row["average"] * 2) / 2} for row in result]


def _find_and_return_authors(tx):
    query = ("MATCH (p:Author) "
             "RETURN p.name as name, ID(p) as id")
    result = tx.run(query)
    return [
        {"name": row["name"], "id": row["id"]} for row in result]


def _find_and_return_tags(tx):
    query = ("MATCH (p:Tag) "
             "RETURN p.name as name, ID(p) as id")
    result = tx.run(query)
    return [
        {"name": row["name"], "id": row["id"]} for row in result]


def _find_and_return_book(tx, book_isbn):
    query = ('MATCH (p:Book) '
             f'WHERE p.isbn = "{book_isbn}" '
             'MATCH (p) <-[:WROTE]-(a:Author) '
             'with p, collect({ name: a.name, id: ID(a) }) as authors '
             'OPTIONAL MATCH (p)-[:IN_TAG]->(t:Tag) '
             'with p, authors, collect({ name: t.name, id: ID(t) }) as tags '
             'OPTIONAL MATCH (p)<-[r:RATED]-() '
             'RETURN p, authors, tags, avg(r.rating) AS average')
    result = tx.run(query)
    return [
        {"isbn": row["p"]["isbn"], "year": row["p"]["year"], "title": row["p"]["title"],
         "image": row["p"]["image"], "authors": row["authors"], "tags": row["tags"],
         "average": round(row["average"] * 2) / 2 if row["average"] else 0} for row in result]


def _add_and_return_rating(tx, user_id, isbn, rating):
    query = (
        'MATCH (p:User) WHERE ID(p) = $user_id '
        f'MATCH (b:Book) WHERE b.isbn = "{isbn}" '
        'CREATE (p)-[r:RATED {rating: $rating}]->(b) '
        'RETURN p, b, r'
    )
    result = tx.run(query, user_id=user_id, rating=rating)
    try:
        return [{"user": row["p"]["name"], "book": row["b"]["isbn"], "rating": row["r"]["rating"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _is_book_rated(tx, user_id, isbn):
    query = ('MATCH (u:User) WHERE ID(u) = $user_id '
             'MATCH (u) -[r:RATED]->(b:Book) '
             f'WHERE b.isbn= "{isbn}" '
             'RETURN r.rating as rating')
    result = tx.run(query, user_id=user_id)
    return [{'rating': row['rating']} for row in result]


def _is_user_followed(tx, user1_id, user2_id):
    query = ('MATCH (u1:User) WHERE ID(u1) = $user1_id '
             'MATCH (u2:User) WHERE ID(u2) = $user2_id '
             'MATCH (u1)-[:FOLLOWS]->(u2) '
             'RETURN u1, u2')
    result = tx.run(query, user1_id=user1_id, user2_id=user2_id)
    return [{'u1': row['u1'], 'u2': row['u2']} for row in result]


def _delete_rating(tx, user_email, isbn):
    query = ("OPTIONAL MATCH (p:User) WHERE p.email = $user_email "
             "OPTIONAL MATCH (b:Book) WHERE b.isbn = $isbn "
             "MATCH (p)-[r:RATED]-(b) "
             "DELETE r"
             )
    result = tx.run(query, user_email=user_email, isbn=isbn)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _delete_author(tx, author_name):
    query = "MATCH (a:Author { name: $author_name }) DETACH DELETE a"
    result = tx.run(query, author_name=author_name)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _create_and_return_author(tx, author_name):
    query = ("CREATE (a:Author { name: $author_name "
             "}) RETURN a")
    result = tx.run(query, author_name=author_name)
    try:
        return [{"name": row["a"]["name"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _mass_upload(tx, filename):
    results = []
    with open(filename, 'r', encoding='utf8') as file:
        for query in file:
            result = tx.run(query)
            try:
                results.append(result)
            except ServiceUnavailable as exception:
                logging.error("{query} raised an error: \n {exception}".format(
                    query=query, exception=exception))
    return results


def _search(tx, text):
    query = ("OPTIONAL MATCH (n1:User) WHERE toLower(n1.name) CONTAINS toLower($text) "
             "WITH collect(distinct n1) as c1 "
             "OPTIONAL MATCH (n2:Author) WHERE toLower(n2.name) CONTAINS toLower($text) "
             "WITH collect(distinct n2) + c1 as c2 "
             "OPTIONAL MATCH (n3:Tag) WHERE toLower(n3.name) CONTAINS toLower($text) "
             "WITH collect(distinct n3) + c2 as c3 "
             "OPTIONAL MATCH (n4:Book) WHERE toLower(n4.title) CONTAINS toLower($text) "
             "WITH collect(distinct n4) + c3 as c4 "
             "UNWIND c4 as nodes "
             "RETURN nodes, ID(nodes), labels(nodes);")
    results = tx.run(query, text=text)
    return [row for row in results]


def _create_and_return_author_book_connection(tx, author_name, isbn):
    query = (
        "MATCH (a:Author) WHERE a.name = $author_name "
        "MATCH (b:Book) WHERE b.isbn = $isbn "
        "CREATE (a)-[:WROTE]->(b) "
        "RETURN a, b"
    )
    result = tx.run(query, author_name=author_name, isbn=isbn)
    try:
        return [{"author": row["a"]["name"], "book": row["b"]["isbn"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _delete_author_book_connection(tx, author_name, isbn):
    query = (
        "MATCH (a:Author) WHERE a.name = $author_name "
        "MATCH (b:Book) WHERE b.isbn = $isbn "
        "MATCH (a)-[r:WROTE]->(b) "
        "DELETE r"
    )
    result = tx.run(query, author_name=author_name, isbn=isbn)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _delete_tag(tx, tag_name):
    query = "MATCH (t:Tag { name: $tag_name }) DETACH DELETE t"
    result = tx.run(query, tag_name=tag_name)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _create_and_return_tag(tx, book_isbn, tag_name):
    query = ('MATCH (b:Book { isbn: "' + book_isbn + '"}) '
                                                     'MERGE (b)-[:IN_TAG]->(t:Tag { name: $tag_name }) '
                                                     'RETURN b, t')
    result = tx.run(query, tag_name=tag_name)
    try:
        return [{"name": row["t"]["name"], "title": row['b']['title']} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _create_and_return_tag_book_connection(tx, tag_name, isbn):
    query = (
        "MATCH (t:Tag) WHERE t.name = $tag_name "
        "MATCH (b:Book) WHERE b.isbn = $isbn "
        "CREATE (b)-[:IN_TAG]->(t) "
        "RETURN t, b"
    )
    result = tx.run(query, tag_name=tag_name, isbn=isbn)
    try:
        return [{"tag": row["t"]["name"], "book": row["b"]["isbn"]} for row in result]
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _delete_tag_book_connection(tx, tag_name, isbn):
    query = (
        "MATCH (t:Tag) WHERE t.name = $tag_name "
        "MATCH (b:Book) WHERE b.isbn = $isbn "
        "MATCH (b)-[r:IN_TAG]->(t) "
        "DELETE r"
    )
    result = tx.run(query, tag_name=tag_name, isbn=isbn)
    try:
        return result
    except ServiceUnavailable as exception:
        logging.error("{query} raised an error: \n {exception}".format(
            query=query, exception=exception))
        raise


def _find_and_return_foaf_users(tx, user_id):
    query = (f"MATCH (u:User) WHERE ID(u) = {user_id} "
             "MATCH (u)-[:FOLLOWS*2]->(foaf) "
             "WHERE NOT((u)-[:FOLLOWS]->(foaf)) "
             "RETURN foaf.name as name, ID(foaf) as id")
    result = tx.run(query)
    return [{"name": row["name"], "id": row['id']} for row in result]


def _find_and_return_recommendations_friends_also_read(tx, user_id):
    query = (f"MATCH (u:User) WHERE ID(u) = {user_id} "
             "MATCH (u)-[:FOLLOWS]->(f:User) "
             "MATCH (f)-[r:RATED]->(b:Book) "
             "WHERE NOT((u)-[:RATED]->(b)) "
             "WITH r, collect(distinct b) as b "
             "RETURN b ORDER BY r.rating DESC LIMIT 10;")
    result = tx.run(query)
    return [row['b'] for row in result]


def _find_and_return_recommendations_users_also_read(tx, user_id):
    query = (f"MATCH (u:User) WHERE ID(u) = {user_id} "
             "MATCH (u)-[r:RATED]->(b1:Book)<-[:RATED]-(u2:User) "
             "MATCH (u2)-[:RATED]->(rec:Book) "
             "RETURN rec.title AS title, rec.isbn as isbn, "
             "COUNT(*) AS usersWhoAlsoRead ORDER BY usersWhoAlsoRead DESC LIMIT 10;")
    result = tx.run(query)
    return [[{"title": row['title'], "isbn": row["isbn"]}] for row in result]


def _find_and_return_recommendations_tags(tx, user_id):
    query = (f"MATCH (u:User) WHERE ID(u) = {user_id} "
             "MATCH (u)-[:RATED]->(b:Book) "
             "MATCH (b)-[:IN_TAG]->(t:Tag)<-[:IN_TAG]-(rec:Book) "
             "WHERE NOT EXISTS( (u)-[:RATED]->(rec)) "
             "WITH rec, COLLECT(t.name) AS tags, COUNT(*) AS commonTags "
             "RETURN rec.title as title, rec.isbn as isbn "
             "ORDER BY commonTags DESC LIMIT 10")
    result = tx.run(query)
    return [[{"title": row["title"], "isbn": row['isbn']}] for row in result]


def _find_and_return_recommendations_tags_author_weighted(tx, user_id):
    query = (f"MATCH (u:User) WHERE ID(u) = {user_id} "
             "MATCH (u)-[:RATED]->(b:Book) "
             "MATCH (b)-[:IN_TAG]->(t:Tag)<-[:IN_TAG]-(rec:Book) "
             "WITH b, rec, COUNT(*) AS ts "
             "OPTIONAL MATCH (b)<-[:WROTE]-(a:Author)-[:WROTE]->(rec) "
             "WITH b, rec, ts, COUNT(a) AS as "
             "RETURN rec.title AS title, rec.isbn as isbn, (3*ts)+(5*as) AS score "
             "ORDER BY score DESC LIMIT 10")
    result = tx.run(query)
    return [[{"title": row["title"], "isbn": row['isbn']}] for row in result]


def _find_and_return_books_similar_users(tx, user_id):
    query = ("MATCH (u:User) WHERE ID(u) = $user_id "
             "MATCH (u)-[:RATED]->(:Book)<-[:RATED]-(o:User) "
             "MATCH (o)-[:RATED]->(rec:Book) "
             "WHERE NOT EXISTS( (u)-[:RATED]->(rec) ) "
             "RETURN rec.title LIMIT 10")
    result = tx.run(query, user_id=user_id)
    return [row["name"] for row in result]


def _find_and_return_similar_users_by_ratings(tx, user_id):
    query = (f"MATCH (u:User) WHERE ID(u) = {user_id} "
             "MATCH (u)-[x:RATED]->(b:Book)<-[y:RATED]-(p:User) "
             "WHERE NOT((u)-[:FOLLOWS]->(p)) "
             "WITH p, ABS(x.rating - y.rating) AS difference "
             "WHERE NOT(ID(u)=ID(p)) "
             "RETURN p.name as name, ID(p) as id ORDER BY difference ASC LIMIT 10;")
    result = tx.run(query)
    return [{"name": row["name"], "id": row['id']} for row in result]
