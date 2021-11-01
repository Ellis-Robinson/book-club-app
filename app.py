import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_books")
def get_books():
    """Finds all books, reviews and users, to be used by frontend"""
    books = mongo.db.books.find().sort('title', 1)
    reviews = list(mongo.db.reviews.find())
    users = list(mongo.db.users.find())
    # checks if in session, sends neccessary variables to frontend
    if session:
        user = mongo.db.users.find_one({
            "username": session["user"]
        })
        user_reviews = list(user["books_reviewed"])

        return render_template(
            "books.html", books=books,
            reviews=reviews, user=user, users=users, user_reviews=user_reviews)

    return render_template(
        "books.html", books=books,
        reviews=reviews, users=users)


@app.route("/search", methods=["GET", "POST"])
def search():
    """Checks user input against db and returns findings"""
    query = request.form.get("query")
    books = list(mongo.db.books.find(
        {"$text": {"$search": query}}))
    reviews = list(mongo.db.reviews.find())
    if session:
        user = mongo.db.users.find_one({
            "username": session["user"]
        })
        user_reviews = list(user["books_reviewed"])
        return render_template("books.html", books=books, reviews=reviews,
                               user=user, user_reviews=user_reviews)
    return render_template(
        "books.html", books=books, reviews=reviews)


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """allows user to create username and password"""
    if request.method == "POST":
        users = mongo.db.users.find()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        # checks if username already in database
        for user in users:
            if user["username"] == request.form.get("username").lower():
                flash("Username Taken, Please Try Another")
                return redirect(url_for("sign_up"))
        # checks both passwords match
        if password != confirm_password:
            flash("Passwords Did Not Match, Please Try Again")
            return redirect(url_for("sign_up"))
        # creates user and adds to db
        register = {
            "email": request.form.get("email"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "admin": False,
            "books_read": [],
            "books_to_read": [],
            "books_reviewed": []
        }
        mongo.db.users.insert_one(register)
        flash("User successfully signed up!")
        return redirect(url_for("log_in"))

    return render_template("sign_up.html")


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    """allows user to log in"""
    if request.method == "POST":
        # checks if user already exists in db
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username").lower()})

        if existing_user:
            # checks if the password for user is correct
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back, {}".format(
                    request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))

            else:
                flash("Incorrect Username/Password")
                return redirect(url_for("log_in"))
        else:
            flash("Incorrect Username/Password")
            return redirect(url_for("log_in"))

    return render_template("log_in.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """loads users page or redirects to log in page"""
    user = mongo.db.users.find_one(
        {"username": session["user"]})

    if session["user"]:
        return render_template(
            "user_profile.html", username=username, user=user)

    return redirect(url_for("log_in"))


@app.route("/edit_account/<username>", methods=["GET", "POST"])
def edit_account(username):
    user = mongo.db.users.find_one(
        {"username": username})
    if request.method == "POST":
        mongo.db.users.update_one(
            user, {"$set": {"email": request.form.get("email"),
                            "username": request.form.get("username").lower()}})
        flash("Account Details Updated, Please Log Back In..")
        session.pop('user')
        return redirect(url_for("log_in"))
    return render_template("edit_account.html", user=user)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    """updates users password and logs them out"""
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"]})
        password = request.form.get("current-password")
        new_password = request.form.get("new-password")
        confirm_new_password = request.form.get("confirm-new-password")
        # checks all passwords are correct
        if (check_password_hash(user["password"], password) and
                new_password == confirm_new_password):
            # updates users password
            mongo.db.users.update_one(
                user, {"$set": {"password": generate_password_hash(
                       request.form.get("new-password"))}})

            flash("Password Successfully Updated. Please Log Back In..")
            return redirect(url_for("log_in"))
        flash("One or More Passwords Incorrect. Please Try Again..")
        return redirect(url_for("edit_account", user=user))

    return render_template("edit_account.html", user=user)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """if use is logged in takes to add book page otherwise
    redirects to log in page"""
    books = mongo.db.books.find()
    user = mongo.db.users.find_one({"username": session["user"]})
    # checks if user in session
    if session["user"]:

        if request.method == "POST":
            is_series = "yes" if request.form.get("is_series") else "no"
            # creates new book from user input
            new_book = {
                "title": request.form.get("title").lower(),
                "genre": request.form.get("genre").lower(),
                "author": request.form.get("author").lower(),
                "year": request.form.get("year").lower(),
                "synopsis": request.form.get("synopsis").lower(),
                "is_series": is_series,
                "series_name": request.form.get("series_name"),
                "rating": "",
                "added_by": session["user"]
            }
            # Checks if title matches a book in database
            for book in books:
                if book["title"] == new_book["title"]:
                    flash("Book Already in Database")
                    return redirect(url_for("add_book"))
            mongo.db.books.insert_one(new_book)
            # Adds book to users books read list
            mongo.db.users.update(
                user, {"$push": {"books_read": str(new_book["_id"])}})

            flash("Book Successfully Added, Now For The Review..")
            return render_template('review_book.html', book=new_book)
        # gets genres from db
        genres = mongo.db.genres.find().sort("name", 1)
        return render_template("add_book.html", genres=genres, user=user)

    return redirect(url_for('log_in'))


@app.route("/edit_book/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    """gets book current info, updates from users input"""
    # finds book
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    is_series = "yes" if request.form.get("is_series") else "no"

    if session["user"]:
        if request.method == "POST":
            # updates from users input
            update = {
                "title": request.form.get("title").lower(),
                "genre": request.form.get("genre").lower(),
                "author": request.form.get("author").lower(),
                "year": request.form.get("year").lower(),
                "synopsis": request.form.get("synopsis").lower(),
                "is_series": is_series,
                "series_name": request.form.get("series_name"),
                "rating": request.form.get("rating"),
                "added_by": session["user"]
            }

            mongo.db.books.update(book, update)
            flash("Book Successfully Edited")
            return redirect(url_for("my_library"))

        genres = mongo.db.genres.find().sort("genres", 1)

        return render_template("edit_book.html", book=book, genres=genres)

    return redirect(url_for('log_in'))


@app.route("/review_book/<book_id>", methods=["GET", "POST"])
def review_book(book_id):
    """if use is logged in takes to review book page,
    then stores review in db.
    otherwise redirects to log in page"""
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    reviews = mongo.db.reviews.find()

    if session["user"]:
        # checks if user has already reviewed book
        for review in reviews:
            if review["book_id"] == str(book["_id"]):
                if review["reviewed_by"] == str(user["_id"]):
                    flash("You Have Already Reviewed This Book")
                    return redirect(url_for("get_books"))

        if request.method == "POST":
            # creates review
            review = {
                "book_reviewed": book["title"],
                "review": request.form.get("review"),
                "reviewed_by": str(user["_id"]),
                "book_id": str(book["_id"]),
                "rating": request.form.get("rating")
            }
            mongo.db.reviews.insert_one(review)
            mongo.db.users.update_one(
                user, {"$push": {"books_reviewed": str(book["_id"])}})
            flash("Book Successfully reviewed")

            update_book_rating(book)

            return redirect(url_for("get_books"))

        return render_template("review_book.html", book=book)
    flash("You Need To Be Logged In To Review Books.")
    return redirect(url_for('log_in'))


@app.route("/update_book_rating")
def update_book_rating(book):
    """finds avarage rating for book and updates book in db"""
    reviews = mongo.db.reviews.find()
    list_of_ratings = []
    for review in reviews:
        # checks reviews against book
        if review["book_id"] == str(book["_id"]):
            # adds rating from reviews to list_of_ratings variable
            list_of_ratings.append(int(review["rating"]))
    # checks at least one review exists
    if len(list_of_ratings) > 0:
        # calculates avarage rating
        new_rating = sum(list_of_ratings) / len(list_of_ratings)
        print(round(new_rating))
        # updates books rating
        mongo.db.books.update(
                book, {
                    "$set": {"rating": round(new_rating)}})


@app.route("/my_reviews")
def my_reviews():
    """Gets all reviews user has posted"""
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    books = list(mongo.db.books.find())
    reviews = list(mongo.db.reviews.find())
    return render_template("my_reviews.html", reviews=reviews,
                           user=user, books=books)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    """ allows user to edit their reviews """
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    book = {}
    # finds book associated with review
    books = mongo.db.books.find()
    for doc in books:
        if str(doc["_id"]) == review["book_id"]:
            book = doc

    if request.method == "POST":
        # updates "review" and "rating" fields
        mongo.db.reviews.update(
            {"_id": ObjectId(review_id)}, {
                "$set": {"review": request.form.get("review"),
                         "rating": request.form.get("rating")}})

        flash("Review Successfully Edited")
        # updates book rating
        update_book_rating(book)

        return redirect(url_for('my_reviews'))

    return render_template("edit_review.html", review=review, book=book)


@app.route("/confirm_review_delete/<review_id>")
def confirm_review_delete(review_id):
    """ Checks if user definitely wants to delete the review"""
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    return render_template(
        "confirm_review_delete.html", review=review, user=user)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    """Delete review from database and removes associated
    id's from documents in users collection"""
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    # finds the review
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)}) 
    book = {}
    books = list(mongo.db.books.find())
    # finds the book linked to review
    for b in books:
        if str(b["_id"]) == review["book_id"]:
            book = b
    # removed review from database
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    # finds user who left the review
    reviewer = mongo.db.users.find_one(
        {"_id": ObjectId(review["reviewed_by"])})
    # removes book from books_reviewed section of relevent user
    if review["reviewed_by"] == str(user["_id"]):
        mongo.db.users.update_one(
            user, {"$pull": {"books_reviewed": str(book["_id"])}})
    elif review["reviewed_by"] == str(reviewer["_id"]):
        mongo.db.users.update_one(
            reviewer, {"$pull": {"books_reviewed": str(book["_id"])}})

    flash("Review Successfully Removed")
    update_book_rating(book)
    return redirect(url_for('get_books'))


@app.route("/confirm_book_delete/<book_id>")
def confirm_book_delete(book_id):
    """ Checks the user definitely wants to delete the book """
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    print(book)
    return render_template("confirm_book_delete.html", book=book, user=user)


@app.route("/delete_book/<book_id>")
def delete_book(book_id):
    """ deletes book, all associated reviews
    removes book id from all documents in db"""
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    users = list(mongo.db.users.find())

    if user["admin"]:
        book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
        reviews = mongo.db.reviews.find()
        mongo.db.books.remove(book)
        # finds reviews connected to book via book id
        for review in reviews:
            if review["book_id"] == str(book["_id"]):
                mongo.db.reviews.remove(review)
        # removes book id from users books_read array
        for user in users:
            mongo.db.users.update_one(
                user, {"$pull": {"books_read": str(book["_id"])}})

        flash("Book Successfully Removed")
        return redirect(url_for('get_books'))
    flash("Sorry, You are not autherised to do that")
    return redirect(url_for('get_books'))


@app.route("/add_genre", methods=["GET", "POST"])
def add_genre():
    """allows admin users to add genre"""
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    # finds all genres
    genres = mongo.db.genres.find().sort('name', 1)
    if request.method == "POST":

        genre = {
            "name": request.form.get("name").lower(),
        }
        mongo.db.genres.insert_one(genre)
        flash("Genre Successfully Added")
        return redirect(url_for("add_genre"))

    # checks if user is admin
    if user["admin"]:
        return render_template("add_genre.html", genres=genres)
    return redirect(url_for("get_books"))


@app.route("/edit_genre", methods=["GET", "POST"])
def edit_genre():
    """ allows admin to edit genre """
    # gets all genres in collection
    genres = list(mongo.db.genres.find())
    if request.method == "POST":

        new_genre = {
            "name": request.form.get("new_genre")
        }
        # links selected genre with correct genre in database and updates
        for genre in genres:
            if genre["name"] == request.form.get("current_genre"):
                current_genre = genre
                mongo.db.genres.update(current_genre, new_genre)

        flash("genre successfully edited")
        return redirect(url_for("edit_genre"))
    return render_template("edit_genre.html", genres=genres)


@app.route("/remove_user", methods=["GET", "POST"])
def remove_user():
    """ allows admin to remove user from db"""
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    if user["admin"]:

        users = list(mongo.db.users.find())
        if request.method == "POST":
            # links selected user with correct user in database and removes
            for user in users:
                if user["username"] == request.form.get("selected_user"):
                    selected_user = user
                    mongo.db.users.remove(selected_user)

            flash("User Successfully Deleted")
            return redirect(url_for("remove_user"))

        return render_template("remove_user.html", users=users)

    flash("You Are Not Authorised To Do That!")
    return redirect(url_for("get_books"))


@app.route("/my_library")
def my_library():
    """loads users library with books they have read
     and books they want to read"""
    books = list(mongo.db.books.find())
    user = mongo.db.users.find_one({
        "username": session["user"]
    })

    books_read = []
    # Creates list of book objects, from object ids in users books_read list
    for book_id in user["books_read"]:
        books_read.append(mongo.db.books.find_one(
            {"_id": ObjectId(book_id)}))

    books_to_read = []
    # Creates list of book objects, from object ids in users books_to_read list
    for book_id in user["books_to_read"]:
        books_to_read.append(mongo.db.books.find_one(
            {"_id": ObjectId(book_id)}))

    reviews = list(mongo.db.reviews.find())
    return render_template(
        "my_library.html", books=books, reviews=reviews,
        books_read=books_read, books_to_read=books_to_read, user=user)


@app.route("/add_to_library/<book_id>", methods=["GET", "POST"])
def add_to_library(book_id):
    """ lets user add books to library """
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    reviews = mongo.db.reviews.find()
    user = mongo.db.users.find_one({
        "username": session["user"]})
    books_read = user["books_read"]
    books_to_read = user["books_to_read"]

    if request.method == "POST":
        if request.form.get("read_book"):
            # checks if book already in 'books read' list
            for books in books_read:
                if books == str(book["_id"]):
                    flash("Book already in library")
                    return redirect(url_for("get_books"))

            # Embeds book in users 'books_read' list
            mongo.db.users.update_one(
                user, {"$push": {"books_read": str(book["_id"])}})

            flash("Book Added To Library")
            return redirect(url_for("get_books"))

        if request.form.get("to_read_book"):
            # checks if book already in users 'to read' list
            for books in books_to_read:
                if books == str(book["_id"]):
                    flash("Book already in library")
                    return redirect(url_for("get_books"))
            # checks if book already in 'books read' list
            for books in books_read:
                if books == str(book["_id"]):
                    flash("Book already in library")
                    return redirect(url_for("get_books"))
            # Embeds book in users 'books_to_read' list
            mongo.db.users.update_one(
                user, {"$push": {"books_to_read": str(book["_id"])}})
            flash("Book Added To Library")
            return redirect(url_for("get_books"))

    return render_template("add_to_library.html",
                           book=book, user=user, reviews=reviews)


@app.route("/remove_from_books_read/<book_id>", methods=["GET", "POST"])
def remove_from_books_read(book_id):
    """ removes book from library and
    id from books read array in user document in db """
    user = mongo.db.users.find_one({
        "username": session["user"]})
    if request.method == "POST":
        # removes book id from users book_read array
        mongo.db.users.update_one(
                user, {"$pull": {"books_read": str(book_id)}})
        flash("Book removed from library")
        return redirect(url_for("my_library"))
    return redirect(url_for("my_library"))


@app.route("/remove_from_to_read/<book_id>", methods=["GET", "POST"])
def remove_from_to_read(book_id):
    """removes book from library and
    id from books to read array in user document in db"""
    user = mongo.db.users.find_one({
        "username": session["user"]})

    if request.method == "POST":

        # removes book id from users books_to_read array
        mongo.db.users.update(
                user, {"$pull": {"books_to_read": str(book_id)}})

        flash("Book removed from to read list")
        return redirect(url_for("my_library"))
    return redirect(url_for("my_library"))


@app.route("/add_to_books_read/<book_id>", methods=["GET", "POST"])
def add_to_books_read(book_id):
    """adds book to users books read section in library
    and removes it from users books to read section"""
    user = mongo.db.users.find_one({
        "username": session["user"]})

    if request.method == "POST":

        # adds book id to users books_read array and removes it from books_to_read array
        mongo.db.users.update(
                user, {"$push": {"books_read": str(book_id)},
                       "$pull": {"books_to_read": str(book_id)}})

        flash("Book added to books read list")
        return redirect(url_for("my_library"))
    return redirect(url_for("my_library"))


@app.route("/log_out")
def log_out():
    """ logs user out """
    # removes user from session
    session.pop("user")
    flash("You have successfully logged out")
    return redirect(url_for("log_in"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
