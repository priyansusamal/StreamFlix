
#  StreamFlix

### Discover Movies. Build Your Watchlist. Share Your Reviews.

StreamFlix is a movie discovery and watchlist web application built using **Python, Flask, and Streamlit**. It allows users to explore movies, view detailed movie information, manage a personal watchlist, and share ratings and reviews.

The application integrates with **The Movie Database (TMDB) API** to retrieve movie information and poster images, while Flask handles backend operations and database management.

---

##  Features

###  Movie Discovery
- Browse a collection of movies.
- View movie posters and basic information.
- Explore movies by genre.
- Discover movies using TMDB data.

###  Movie Details
- View detailed information about a selected movie.
- Explore movie descriptions and poster images.
- Access ratings and reviews for individual movies.

###  Ratings & Reviews
- Rate movies on a scale of 1 to 5 stars.
- Write and submit reviews.
- View average ratings and total review counts.
- Edit your own reviews.
- Delete your own reviews.

###  Personal Watchlist
- Add movies to your watchlist.
- View your saved movies.
- Remove movies from your watchlist.

###  User Management
- User registration and login.
- User-specific watchlists and reviews.

###  Interface
- Dark, cosmic-inspired UI.
- Movie poster cards arranged in a grid.
- Dedicated movie details and review sections.

---

##  Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Frontend and user interface |
| Flask | Backend REST API |
| SQLAlchemy | Database ORM |
| SQLite | Local database |
| PostgreSQL | Production database support |
| TMDB API | Movie information and posters |
| Requests | HTTP communication between frontend and backend |
| HTML & CSS | UI styling |

---

##  Project Architecture

StreamFlix follows a frontend-backend architecture.

```text
                 ┌─────────────────────┐
                 │      Streamlit      │
                 │      Frontend       │
                 └──────────┬──────────┘
                            │
                            │ HTTP Requests
                            ▼
                 ┌─────────────────────┐
                 │        Flask        │
                 │      REST API       │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        ┌────────────────┐   ┌────────────────┐
        │   SQLAlchemy   │   │    TMDB API    │
        │    Database    │   │ Movie Metadata │
        └────────────────┘   └────────────────┘
```

---

##  Project Structure

```text
StreamFlix/
│
├── backend/
│   ├── app.py
│   ├── .env
│   └── instance/
│       └── streamflix.db
│
├── frontend/
│   ├── app.py
│   └── .streamlit/
│       └── secrets.toml
│
├── .gitignore
└── README.md
```

> The database file and environment configuration files are local and should not be committed to GitHub.

---

##  Getting Started

Follow these steps to run StreamFlix locally.

### 1. Prerequisites

Make sure you have the following installed:

- Python 3.10 or later
- Git
- A TMDB API key

### 2. Clone the Repository

```bash
git clone https://github.com/priyansusamal/StreamFlix.git
cd StreamFlix
```

### 3. Set Up the Backend

Open a terminal and navigate to the backend folder.

```bash
cd backend
```

Create and activate a virtual environment.

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the `backend` folder:

```env
TMDB_API_KEY=your_tmdb_api_key
```

Replace `your_tmdb_api_key` with your actual TMDB API key.

Start the Flask backend:

```bash
python app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

### 4. Set Up the Frontend

Open a **new terminal** and navigate to the frontend folder.

```powershell
cd "C:\Users\Prachi\OneDrive\Documents\Desktop\Project\StreamFlix\frontend"
```

Create and activate a virtual environment if required.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

Create the file `frontend/.streamlit/secrets.toml`:

```toml
BACKEND_URL = "http://127.0.0.1:5000"
```

Start the Streamlit frontend:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

---

##  Environment Variables

| Variable | Description |
|---|---|
| `TMDB_API_KEY` | API key used to retrieve movie information from TMDB |
| `BACKEND_URL` | Base URL of the Flask backend used by Streamlit |

**Important:** Never commit API keys, secrets, or database credentials to GitHub.

---

##  API Endpoints

The Flask backend exposes REST API endpoints for movie data, watchlists, and reviews.

###  Movies

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/movies` | Retrieve the movie collection |
| GET | `/api/movies/<movie_id>/reviews` | Retrieve reviews and average rating for a movie |

###  Watchlist

The watchlist API supports retrieving, adding, and removing movies from a user's watchlist.

###  Reviews

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/reviews` | Create a review |
| PUT | `/api/reviews/<review_id>` | Update an existing review |
| DELETE | `/api/reviews/<review_id>` | Delete a review |

> API routes may vary depending on the backend implementation. Check `backend/app.py` for the complete route definitions.

---

##  Database

StreamFlix uses SQLAlchemy to interact with its database.

The database stores information related to:

- Users
- Movies
- Watchlists
- Ratings and reviews

SQLite is used for local development, with PostgreSQL support for production configurations.

---

##  Future Enhancements

- Advanced movie search and filtering.
- Personalized movie recommendations.
- User profile pages.
- Improved authentication and authorization.
- Pagination and sorting.
- Enhanced mobile responsiveness.
- Deployment with a production database.

---

##  Project Objective

StreamFlix was developed as a project to explore full-stack application development, REST API integration, database management, and interactive UI design using Python-based technologies.

---

##  Author

**Priyansu Samal**

- GitHub: [@priyansusamal](https://github.com/priyansusamal)

---

##  License

This project is intended for educational and personal development purposes.