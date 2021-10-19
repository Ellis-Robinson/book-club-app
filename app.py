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

#make home page that explains how the app works
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# loads page with list of all books
@app.route("/")
@app.route("/get_books")
def get_books():
    if session:
        books = mongo.db.books.find()
        reviews = list(mongo.db.reviews.find())
        user = mongo.db.users.find_one({
            "username": session["user"]
        })
        return render_template(
            "books.html", books=books, reviews=reviews, user=user)
    
    flash("You need to log in first")
    return redirect(url_for("log_in"))


# allows user to create username and password
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # checks if username already in database
        users = mongo.db.users.find()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        for user in users:
            if user["username"] == request.form.get("username").lower():
                flash("Username Taken, Please Try Another")
                return redirect(url_for("sign_up"))

        if password != confirm_password:
            flash("Passwords Did Not Match, Please Try Again")
            return redirect(url_for("sign_up"))
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "admin": False,
            "books_read": [],
            "books_to_read": []
        }
        mongo.db.users.insert_one(register)
        flash("User successfully signed up!")
        return redirect(url_for("log_in"))

    return render_template("sign_up.html")


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        # checks if user already exists in db
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username").lower()})

        if existing_user:
            # checks if the password for user is correct
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
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


# loads users page or redirects to log in page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    user = mongo.db.users.find_one(
        {"username": session["user"]})

    if session["user"]:
        return render_template(
            "user_profile.html", username=username, user=user)

    return redirect(url_for("log_in"))


# if use is logged in takes to add book page
# otherwise redirects to log in page
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if session["user"]:

        if request.method == "POST":
            is_series = "yes" if request.form.get("is_series") else "no"

            book = {
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
            mongo.db.books.insert_one(book)
            flash("Book Successfully Added")
            return redirect(url_for('my_library'))

        genres = mongo.db.genres.find().sort("genres", 1)
        return render_template("add_book.html", genres=genres)

    return redirect(url_for('log_in'))


@app.route("/edit_book/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})

    is_series = "yes" if request.form.get("is_series") else "no"

    if session["user"]:
        if request.method == "POST":
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


# if use is logged in takes to review book page
# otherwise redirects to log in page
@app.route("/review_book/<book_id>", methods=["GET", "POST"])
def review_book(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    reviews = mongo.db.reviews.find()

    if session["user"]:
        # checks if user has already reviewed book
        for review in reviews:
            if review["book_id"] == str(book["_id"]):
                if review["reviewed_by"] == session["user"]:
                    flash("You Have Already Reviewed This Book")
                    return redirect(url_for("get_books"))

        if request.method == "POST":
            review = {
                "book_reviewed": request.form.get("book_reviewed"),
                "review": request.form.get("review"),
                "reviewed_by": request.form.get("reviewed_by"),
                "book_id": request.form.get("book_id")
            }
            mongo.db.reviews.insert_one(review)
            flash("Book Successfully reviewed")
            return redirect(url_for("get_books"))
            
        return render_template("review_book.html", book=book)
    flash("You Need To Be Logged In To Review Books.")
    return redirect(url_for('log_in'))


# shows all reviews user has posted
@app.route("/my_reviews")
def my_reviews():

    reviews = mongo.db.reviews.find()
    return render_template("my_reviews.html", reviews=reviews)


# allows user to edit their reviews
@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    if request.method == "POST":
        #updates the "review" field only
        mongo.db.reviews.update(
            {"_id": ObjectId(review_id)}, {
                "$set": {"review": request.form.get("review")}})

        flash("Review Successfully Edited")
        return redirect(url_for('my_reviews'))

    return render_template("edit_review.html", review=review)


# allows user to delete their reviews
@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review Successfully Removed")
    return redirect(url_for('my_reviews'))


@app.route("/delete_book/<book_id>")
def delete_book(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    reviews = mongo.db.reviews.find()
    mongo.db.books.remove(book)
    #finds reviews connected to book via book id
    for review in reviews:
        if review["book_id"] == str(book["_id"]):
            mongo.db.reviews.remove(review)

    flash("Book Successfully Removed")
    return redirect(url_for('my_library'))


# allows admin users to add genre
@app.route("/add_genre", methods=["GET", "POST"])
def add_genre():
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    if request.method == "POST":

        genre = {
            "name": request.form.get("name").lower(),
        }
        mongo.db.genres.insert_one(genre)
        flash("Genre Successfully Added")
        return redirect(url_for("get_books"))

    # checks if user is admin
    if user["admin"]:
        return render_template("add_genre.html")
    return redirect(url_for("get_books"))


@app.route("/edit_genre", methods=["GET", "POST"])
def edit_genre():
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
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    if user["admin"]:

        users = mongo.db.users.find()
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
    books = list(mongo.db.books.find())
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    books_read = user["books_read"]
    books_to_read = user["books_to_read"]
    reviews = list(mongo.db.reviews.find())
    return render_template(
        "my_library.html", books=books, reviews=reviews,
        books_read=books_read, books_to_read=books_to_read)


@app.route("/add_to_library/<book_id>", methods=["GET", "POST"])
def add_to_library(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    user = mongo.db.users.find_one({
        "username": session["user"]
    })
    books_read = user["books_read"]
    books_to_read = user["books_to_read"]

    if request.method == "POST":
        if request.form.get("read_book"):
            for books in books_read:
                if books == book:
                    flash("Book already in library")
                    return redirect(url_for("get_books"))

            # Embeds book in users 'books_read' field
            mongo.db.users.update(
                user, {"$set": {
                    "books_read": books_read + [book]}})

            flash("Book Added To Library")
            return redirect(url_for("get_books"))

        if request.form.get("to_read_book"):
            for books in books_to_read:
                if books == book:
                    flash("Book already in library")
                    return redirect(url_for("get_books"))

            # Embeds book in users 'books_to_read' field
            mongo.db.users.update(
                user, {"$set": {
                    "books_to_read": books_to_read + [book]}})

            flash("Book Added To Library")
            return redirect(url_for("get_books"))

    return render_template("add_to_library.html", book=book, user=user)


@app.route("/log_out")
def log_out():
    session.pop("user")
    flash("You have successfully logged out")
    return redirect(url_for("log_in"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)