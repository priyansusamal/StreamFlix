
"""
StreamFlix Backend API
Flask + Flask-SQLAlchemy + Werkzeug + TMDB posters + Reviews

Run locally:
    pip install -r requirements.txt
    python app.py
"""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ---------------------------------------------------------------------------
# App & database configuration
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)

database_url = os.environ.get("DATABASE_URL", "sqlite:///streamflix.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    watchlist_items = db.relationship(
        "Watchlist",
        backref="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_public_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster_url = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "year": self.year,
            "description": self.description,
            "poster_url": self.poster_url
        }


class Watchlist(db.Model):
    __tablename__ = "watchlist"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    movie_id = db.Column(
        db.Integer, db.ForeignKey("movies.id"), nullable=False
    )
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship("Movie")

    __table_args__ = (
        db.UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),
    )


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    movie_id = db.Column(
        db.Integer, db.ForeignKey("movies.id"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship("User")
    movie = db.relationship("Movie")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "movie_id", name="uq_user_movie_review"
        ),
        db.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_review_rating"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "movie_id": self.movie_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# ---------------------------------------------------------------------------
# Database migration
# ---------------------------------------------------------------------------

def migrate_movie_table():
    inspector = inspect(db.engine)

    if "movies" not in inspector.get_table_names():
        return

    columns = [
        column["name"]
        for column in inspector.get_columns("movies")
    ]

    if "poster_url" not in columns:
        with db.engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE movies ADD COLUMN poster_url TEXT")
            )


# ---------------------------------------------------------------------------
# Movie catalog
# ---------------------------------------------------------------------------

MOVIE_DATA = [
    ("Stranger Things", "Sci-Fi", 2016,
     "A group of kids uncover supernatural secrets in their small town."),
    ("Wednesday", "Mystery", 2022,
     "Wednesday Addams navigates a new school while solving a supernatural mystery."),
    ("The Queen's Gambit", "Drama", 2020,
     "An orphaned chess prodigy rises to the top of the competitive chess world."),
    ("Money Heist", "Crime", 2017,
     "A criminal mastermind leads a group through an elaborate heist."),
    ("Dark", "Mystery", 2017,
     "A missing child sets off events tied to a town's secrets across time."),
    ("Our Planet", "Documentary", 2019,
     "A look at the natural world and the challenges facing its wildlife."),
    ("Interstellar", "Sci-Fi", 2014,
     "Explorers travel through a wormhole in search of a future for humanity."),
    ("Inception", "Sci-Fi", 2010,
     "A skilled thief enters dreams to carry out a complex mission."),
    ("The Dark Knight", "Action", 2008,
     "Batman faces a criminal mastermind who threatens Gotham City."),
    ("Avatar", "Fantasy", 2009,
     "A former Marine discovers the world of Pandora."),
    ("Titanic", "Romance", 1997,
     "Two passengers from different backgrounds fall in love aboard a ship."),
    ("La La Land", "Romance", 2016,
     "An aspiring actress and a jazz musician pursue their dreams."),
    ("The Notebook", "Romance", 2004,
     "A lifelong love story unfolds through memories and changing circumstances."),
    ("The Hangover", "Comedy", 2009,
     "Friends try to piece together a wild night before a wedding."),
    ("Home Alone", "Comedy", 1990,
     "A young boy protects his home after being accidentally left behind."),
    ("Jumanji", "Adventure", 1995,
     "A mysterious game brings a dangerous jungle into the real world."),
    ("Jurassic Park", "Adventure", 1993,
     "A theme park featuring cloned dinosaurs descends into chaos."),
    ("The Conjuring", "Horror", 2013,
     "Paranormal investigators help a family experiencing disturbing events."),
    ("A Quiet Place", "Horror", 2018,
     "A family must remain silent to survive creatures that hunt by sound."),
    ("Get Out", "Horror", 2017,
     "A visit to a girlfriend's family reveals unsettling secrets."),
    ("The Shawshank Redemption", "Drama", 1994,
     "Two prisoners form a friendship while holding on to hope."),
    ("Forrest Gump", "Drama", 1994,
     "A man recounts his extraordinary life and the people he meets."),
    ("The Social Network", "Drama", 2010,
     "The story of the founding of a major social networking company."),
    ("Spider-Man: No Way Home", "Action", 2021,
     "Spider-Man faces challenges after his identity becomes public."),
    ("Avengers: Endgame", "Action", 2019,
     "The Avengers attempt to reverse the consequences of a devastating event."),
    ("Black Panther", "Action", 2018,
     "A new king must protect his nation and its future."),
    ("Inside Out", "Animation", 2015,
     "A young girl's emotions navigate the challenges of growing up."),
    ("Coco", "Animation", 2017,
     "A young musician journeys into the Land of the Dead."),
    ("Finding Nemo", "Animation", 2003,
     "A clownfish crosses the ocean to find his missing son."),
    ("The Lord of the Rings: The Fellowship of the Ring", "Fantasy", 2001,
     "A group sets out to destroy a powerful ring."),
    ("Harry Potter and the Philosopher's Stone", "Fantasy", 2001,
     "A young wizard discovers a magical world and his own history."),
    ("Dune", "Sci-Fi", 2021,
     "A young noble travels to a desert planet with a valuable resource."),
    ("Knives Out", "Mystery", 2019,
     "A detective investigates a suspicious death in a wealthy family."),
    ("The Martian", "Sci-Fi", 2015,
     "An astronaut stranded on Mars fights to survive."),
    ("Top Gun: Maverick", "Action", 2022,
     "A veteran pilot trains a new generation for a dangerous mission."),
    ("The Grand Budapest Hotel", "Comedy", 2014,
     "A hotel concierge and his protégé become involved in an unusual adventure."),
    ("Whiplash", "Drama", 2014,
     "A young drummer faces intense pressure at a music conservatory."),
    ("The Imitation Game", "Drama", 2014,
     "A team works to decipher an encrypted code during World War II."),
    ("The Pursuit of Happyness", "Drama", 2006,
     "A father works to build a better life for himself and his son."),
    ("The Wolf of Wall Street", "Crime", 2013,
     "A stockbroker rises to wealth and faces the consequences of his actions."),
    ("The Truman Show", "Comedy", 1998,
     "A man begins to question whether his entire world is staged.")
]


def seed_movies():
    for title, genre, year, description in MOVIE_DATA:
        movie = Movie.query.filter_by(title=title).first()

        if movie is None:
            movie = Movie(
                title=title,
                genre=genre,
                year=year,
                description=description,
                poster_url=None
            )
            db.session.add(movie)
        else:
            movie.genre = genre
            movie.year = year
            movie.description = description

    db.session.commit()


# ---------------------------------------------------------------------------
# TMDB poster integration
# ---------------------------------------------------------------------------

def fetch_tmdb_poster(title, year=None):
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        print("TMDB_API_KEY is missing.")
        return None

    base_url = "https://api.themoviedb.org/3/search/"

    for media_type in ["movie", "tv"]:
        url = base_url + media_type

        params = {
            "api_key": api_key,
            "query": title
        }

        if year:
            if media_type == "movie":
                params["year"] = year
            else:
                params["first_air_date_year"] = year

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            results = response.json().get("results", [])

            if not results and year:
                params.pop("year", None)
                params.pop("first_air_date_year", None)

                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                results = response.json().get("results", [])

            for result in results:
                poster_path = result.get("poster_path")

                if poster_path:
                    return (
                        "https://image.tmdb.org/t/p/w500"
                        + poster_path
                    )

        except requests.RequestException as e:
            print(f"TMDB {media_type} search failed for {title}: {e}")

    print(f"No poster found for: {title}")
    return None


# ---------------------------------------------------------------------------
# Initialize database
# ---------------------------------------------------------------------------

with app.app_context():
    db.create_all()
    migrate_movie_table()
    seed_movies()


# ---------------------------------------------------------------------------
# Generic error helper
# ---------------------------------------------------------------------------

def error(message, status=400):
    return jsonify({"error": message}), status


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "StreamFlix API"
    })


# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return error("Name, email and password are all required.")

    if "@" not in email or "." not in email:
        return error("Please enter a valid email address.")

    if len(password) < 8:
        return error("Password must be at least 8 characters long.")

    if User.query.filter_by(email=email).first():
        return error("An account with that email already exists.", 409)

    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password)
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("An account with that email already exists.", 409)

    return jsonify({
        "message": "Account created successfully.",
        "user": user.to_public_dict()
    }), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error("Email and password are required.")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return error("Incorrect email or password.", 401)

    return jsonify({
        "message": "Login successful.",
        "user": user.to_public_dict()
    })


# ---------------------------------------------------------------------------
# Movie catalog, search & genre filtering
# ---------------------------------------------------------------------------

@app.route("/api/movies", methods=["GET"])
def get_movies():
    q = (request.args.get("q") or "").strip()
    genre = (request.args.get("genre") or "").strip()

    query = Movie.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Movie.title.ilike(like),
                Movie.genre.ilike(like)
            )
        )

    if genre and genre.lower() != "all":
        query = query.filter(Movie.genre.ilike(genre))

    movies = query.order_by(Movie.id).all()

    return jsonify({
        "movies": [movie.to_dict() for movie in movies]
    })


@app.route("/api/genres", methods=["GET"])
def get_genres():
    genres = [
        row[0]
        for row in db.session.query(Movie.genre)
        .distinct()
        .order_by(Movie.genre)
        .all()
    ]

    return jsonify({"genres": genres})


@app.route("/api/movies/refresh-posters", methods=["POST"])
def refresh_posters():
    if not os.getenv("TMDB_API_KEY"):
        return error(
            "TMDB_API_KEY is missing from the backend .env file.",
            500
        )

    movies = Movie.query.filter(
        db.or_(
            Movie.poster_url.is_(None),
            Movie.poster_url == "",
            Movie.poster_url.like("%placehold%"),
            Movie.poster_url.like("%placeholder%")
        )
    ).all()

    updated = 0
    failed = []

    try:
        for movie in movies:
            poster_url = fetch_tmdb_poster(movie.title, movie.year)

            if poster_url:
                movie.poster_url = poster_url
                updated += 1
            else:
                failed.append(movie.title)

        db.session.commit()

    except Exception:
        db.session.rollback()
        app.logger.exception("Poster refresh failed")
        return error("Poster refresh failed. Please try again.", 500)

    return jsonify({
        "message": "Poster refresh completed.",
        "updated": updated,
        "failed_count": len(failed),
        "failed": failed
    })


# ---------------------------------------------------------------------------
# Watchlist endpoints
# ---------------------------------------------------------------------------

@app.route("/api/watchlist/<int:user_id>", methods=["GET"])
def get_watchlist(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return error("User not found.", 404)

    items = (
        Watchlist.query
        .filter_by(user_id=user_id)
        .order_by(Watchlist.added_at.desc())
        .all()
    )

    return jsonify({
        "watchlist": [item.movie.to_dict() for item in items]
    })


@app.route("/api/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    movie_id = data.get("movie_id")

    if not user_id or not movie_id:
        return error("user_id and movie_id are both required.")

    if not db.session.get(User, user_id):
        return error("User not found.", 404)

    if not db.session.get(Movie, movie_id):
        return error("Movie not found.", 404)

    existing = Watchlist.query.filter_by(
        user_id=user_id,
        movie_id=movie_id
    ).first()

    if existing:
        return error("That title is already in your watchlist.", 409)

    db.session.add(Watchlist(user_id=user_id, movie_id=movie_id))
    db.session.commit()

    return jsonify({"message": "Added to watchlist."}), 201


@app.route(
    "/api/watchlist/<int:user_id>/<int:movie_id>",
    methods=["DELETE"]
)
def remove_from_watchlist(user_id, movie_id):
    item = Watchlist.query.filter_by(
        user_id=user_id,
        movie_id=movie_id
    ).first()

    if not item:
        return error("That title is not in the watchlist.", 404)

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Removed from watchlist."})


# ---------------------------------------------------------------------------
# Ratings & Reviews endpoints
# ---------------------------------------------------------------------------

@app.route("/api/movies/<int:movie_id>/reviews", methods=["GET"])
def get_movie_reviews(movie_id):
    movie = db.session.get(Movie, movie_id)

    if not movie:
        return error("Movie not found.", 404)

    reviews = (
        Review.query
        .filter_by(movie_id=movie_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    average_rating = (
        db.session.query(db.func.avg(Review.rating))
        .filter_by(movie_id=movie_id)
        .scalar()
    )

    return jsonify({
        "movie_id": movie_id,
        "average_rating": round(float(average_rating), 1)
        if average_rating is not None else 0,
        "total_reviews": len(reviews),
        "reviews": [review.to_dict() for review in reviews]
    })


@app.route("/api/reviews", methods=["POST"])
def create_review():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    movie_id = data.get("movie_id")
    rating = data.get("rating")
    review_text = (data.get("review_text") or "").strip()

    if not user_id or not movie_id:
        return error("user_id and movie_id are required.")

    if not db.session.get(User, user_id):
        return error("User not found.", 404)

    if not db.session.get(Movie, movie_id):
        return error("Movie not found.", 404)

    if (
        not isinstance(rating, int)
        or isinstance(rating, bool)
        or rating < 1
        or rating > 5
    ):
        return error("Rating must be an integer from 1 to 5.")

    if not review_text:
        return error("Review text is required.")

    existing = Review.query.filter_by(
        user_id=user_id,
        movie_id=movie_id
    ).first()

    if existing:
        return error(
            "You have already reviewed this movie. Please edit your review.",
            409
        )

    review = Review(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating,
        review_text=review_text
    )

    db.session.add(review)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("You have already reviewed this movie.", 409)

    return jsonify({
        "message": "Review submitted successfully.",
        "review": review.to_dict()
    }), 201


@app.route("/api/reviews/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    review = db.session.get(Review, review_id)

    if not review:
        return error("Review not found.", 404)

    if not user_id:
        return error("user_id is required.")

    if review.user_id != user_id:
        return error("You can only edit your own review.", 403)

    rating = data.get("rating")
    review_text = data.get("review_text")

    if rating is not None:
        if (
            not isinstance(rating, int)
            or isinstance(rating, bool)
            or rating < 1
            or rating > 5
        ):
            return error("Rating must be an integer from 1 to 5.")

        review.rating = rating

    if review_text is not None:
        review_text = review_text.strip()

        if not review_text:
            return error("Review text cannot be empty.")

        review.review_text = review_text

    review.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Review updated successfully.",
        "review": review.to_dict()
    })


@app.route("/api/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    review = db.session.get(Review, review_id)

    if not review:
        return error("Review not found.", 404)

    if not user_id:
        return error("user_id is required.")

    if review.user_id != user_id:
        return error("You can only delete your own review.", 403)

    db.session.delete(review)
    db.session.commit()

    return jsonify({
        "message": "Review deleted successfully."
    })


# ---------------------------------------------------------------------------
# Generic error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(_e):
    return error("Not found.", 404)


@app.errorhandler(500)
def server_error(_e):
    db.session.rollback()
    return error(
        "Something went wrong on the server. Please try again.",
        500
    )


# ---------------------------------------------------------------------------
# Run server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)