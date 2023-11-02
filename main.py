from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class Add(FlaskForm):
    movie_data = StringField("Search your MOVIE")
    submit = SubmitField("Done")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String(500))
    rating = db.Column(db.String(250))
    ranking = db.Column(db.String(250))
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))


@app.route("/")
def home():
    while True:
        result = db.session.execute(db.select(Movie))
        all_movies = result.scalars()
        return render_template("index.html", values=all_movies)


@app.route("/select")
def select():
    name = request.args.get("dta")
    url = f"https://api.themoviedb.org/3/search/movie?query={name}&include_adult=false&language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlZDIzMzBhMTNiNzEwZGVmYzgxMDQyOGEzZDQ2Yjg2MSIsInN1YiI6IjY1MTY3MTJjOTY3Y2M3MDBhY2I4NDkyNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.laBMOt0bMk4Uzu3PVYtJTWy2z5KWZZpGRPsfp6oPH5M"

    }

    response = requests.get(url, headers=headers)
    data = response.json()['results']

    return render_template("select.html", data=data)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', form=form)


@app.route("/del")
def dele():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    frm = Add()
    if frm.validate_on_submit():
        movie = frm.movie_data.data
        return redirect(url_for('select', dta=movie))

    return render_template("add.html", frm=frm)


@app.route("/dta", methods=["GET", "POST"])
def dsat():
    data = request.args.get("id")
    url = f"https://api.themoviedb.org/3/movie/{data}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlZDIzMzBhMTNiNzEwZGVmYzgxMDQyOGEzZDQ2Yjg2MSIsInN1YiI6IjY1MTY3MTJjOTY3Y2M3MDBhY2I4NDkyNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.laBMOt0bMk4Uzu3PVYtJTWy2z5KWZZpGRPsfp6oPH5M"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    title = data['original_title']
    year = data['release_date']
    description = data['overview']
    rating = data['vote_average']
    second_movie = Movie(
        title=title,
        year=year,
        description=description,
        rating=rating,
        ranking=9,
        review="I liked the water.",
        img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    )
    db.session.add(second_movie)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
