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
    books = mongo.db.books.find()
    reviews = list(mongo.db.reviews.find())
    return render_template("books.html", books=books, reviews=reviews)


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        register = { 
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)
        flash("User successfully signed up!")

    return render_template("sign_up.html")

@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        #checks if user already exists in db
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username").lower()})

        if existing_user:
            #checks if the password for user is correct
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


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("user_profile.html", username=username)

    return redirect(url_for("log_in"))


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
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
            "rating": request.form.get("rating")
        }
        mongo.db.books.insert_one(book)
        flash("Book Successfully Added")

    if session["user"]:
        genres = mongo.db.genres.find().sort("genres", 1)
        return render_template("add_book.html", genres=genres)

    return redirect(url_for('log_in'))


@app.route("/review_book/<book_id>", methods=["GET", "POST"])
def review_book(book_id):
    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})

    if request.method == "POST":
        review = {
            "book_reviewed": request.form.get("book_reviewed"),
            "review": request.form.get("review"),
            "reviewer": request.form.get("reviewer"),
            "book_id": request.form.get("book_id")
        }
        mongo.db.reviews.insert_one(review)
        flash("Book Successfully reviewed")
        return redirect(url_for("my_reviews"))

    return render_template("review_book.html", book=book)



@app.route("/my_reviews")
def my_reviews():

    reviews = mongo.db.reviews.find()
    return render_template("my_reviews.html", reviews=reviews)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    if request.method == "POST":
        edit = {
            "book_reviewed": request.form.get("book_reviewed"),
            "review": request.form.get("review"),
            "reviewer": request.form.get("reviewer"),
            "book_id": request.form.get("book_id"),
        }

        mongo.db.reviews.update({"_id": ObjectId(review_id)}, edit)
        flash("Review Successfully Edited")
        return redirect(url_for('my_reviews'))

    return render_template("edit_review.html", review=review)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review Successfully Removed")
    return redirect(url_for('my_reviews'))


@app.route("/log_out")
def log_out():
    session.pop("user")
    flash("You have successfully logged out")
    return redirect(url_for("log_in"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)