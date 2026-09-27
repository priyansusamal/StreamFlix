
"""
StreamFlix frontend (Streamlit)

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

The backend API URL is read from Streamlit secrets (BACKEND_URL) or the
BACKEND_URL environment variable, falling back to http://localhost:5000
for local development.
"""

import os
import html
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="STREAMFLIX",
    page_icon="🌌",
    layout="wide"
)


def get_backend_url():
    try:
        if "BACKEND_URL" in st.secrets:
            return st.secrets["BACKEND_URL"]
    except Exception:
        pass

    return os.environ.get(
        "BACKEND_URL",
        "http://localhost:5000"
    )


BACKEND_URL = get_backend_url().rstrip("/")
RED = "#e50914"


# ---------------------------------------------------------------------------
# Cosmic / astro theme CSS
# ---------------------------------------------------------------------------

def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background-color: #05050d;
            background-image:
                radial-gradient(1.5px 1.5px at 20px 30px, #ffffff, transparent),
                radial-gradient(1.5px 1.5px at 140px 80px, #ffffff, transparent),
                radial-gradient(1px 1px at 90px 40px, #ffffff, transparent),
                radial-gradient(1px 1px at 160px 120px, #ffffff, transparent),
                radial-gradient(2px 2px at 60px 150px, #ffffff, transparent),
                radial-gradient(1px 1px at 190px 10px, #ffffff, transparent),
                radial-gradient(ellipse 900px 600px at 12% 8%, rgba(229,9,20,0.30), transparent 60%),
                radial-gradient(ellipse 800px 600px at 88% 0%, rgba(147,51,234,0.28), transparent 60%),
                radial-gradient(ellipse 1000px 700px at 50% 105%, rgba(30,58,138,0.35), transparent 65%);
            background-repeat: repeat, repeat, repeat, repeat, repeat, repeat, no-repeat, no-repeat, no-repeat;
            background-size: 200px 200px, 200px 200px, 200px 200px, 200px 200px, 200px 200px, 200px 200px, auto, auto, auto;
            background-attachment: fixed;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        .sf-logo {{
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: 1px;
            color: {RED};
            text-shadow: 0 0 18px rgba(229,9,20,0.6);
        }}

        .sf-tagline {{
            color: #c9c9d6;
            font-size: 1rem;
            margin-top: -6px;
        }}

        .sf-card {{
            background: rgba(20, 18, 32, 0.55);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 18px 20px;
            backdrop-filter: blur(10px);
            margin-bottom: 16px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.35);
        }}

        .sf-card h3 {{
            margin: 0 0 4px 0;
            color: #fff;
            font-size: 1.15rem;
        }}

        .sf-meta {{
            color: {RED};
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.4px;
            margin-bottom: 8px;
        }}

        .sf-desc {{
            color: #b7b7c4;
            font-size: 0.88rem;
            line-height: 1.5;
        }}

        .stButton > button {{
            background: {RED};
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            padding: 6px 16px;
        }}

        .stButton > button:hover {{
            background: #ff1a25;
            color: white;
        }}

        .sf-remove button {{
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }}

        .sf-empty {{
            color: #8a8a99;
            font-style: italic;
            padding: 10px 0 20px 0;
        }}

        hr {{
            border-color: rgba(255,255,255,0.08);
        }}

        section[data-testid="stSidebar"] {{
            background: rgba(10, 8, 18, 0.85);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


inject_css()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "watchlist_ids" not in st.session_state:
    st.session_state.watchlist_ids = set()


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def api_call(method, path, **kwargs):
    try:
        resp = requests.request(
            method,
            f"{BACKEND_URL}{path}",
            timeout=15,
            **kwargs
        )

        try:
            data = resp.json()
        except ValueError:
            data = {}

        return resp.status_code, data

    except requests.exceptions.RequestException:
        return None, {
            "error": (
                "Can't reach the StreamFlix backend right now. "
                "Please try again shortly."
            )
        }


def refresh_watchlist():
    if not st.session_state.user:
        return

    status, data = api_call(
        "GET",
        f"/api/watchlist/{st.session_state.user['id']}"
    )

    if status == 200:
        st.session_state.watchlist_ids = {
            movie["id"]
            for movie in data.get("watchlist", [])
        }


def fetch_genres():
    status, data = api_call("GET", "/api/genres")

    if status == 200:
        return data.get("genres", [])

    return []


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def render_header():
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(
            '<div class="sf-logo">STREAMFLIX</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="sf-tagline">'
            'Unlimited stories. One place to watch.'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        if st.session_state.user:
            if st.button("Log Out", use_container_width=True):
                st.session_state.user = None
                st.session_state.watchlist_ids = set()
                st.rerun()

    st.write("")


# ---------------------------------------------------------------------------
# Authentication screen
# ---------------------------------------------------------------------------

def render_auth():
    st.write("")

    left, mid, right = st.columns([1, 2, 1])

    with mid:
        st.markdown(
            '<div class="sf-card">'
            '<h3 style="text-align:center;">Welcome to StreamFlix</h3>'
            '<p class="sf-desc" style="text-align:center;">'
            'Sign in or create an account to start watching.'
            '</p></div>',
            unsafe_allow_html=True
        )

        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

        # -------------------- Login --------------------

        with tab_login:
            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                submitted = st.form_submit_button(
                    "Log In",
                    use_container_width=True
                )

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")

                else:
                    status, data = api_call(
                        "POST",
                        "/api/login",
                        json={
                            "email": email,
                            "password": password
                        }
                    )

                    if status == 200:
                        st.session_state.user = data["user"]
                        refresh_watchlist()
                        st.success("Login successful.")
                        st.rerun()

                    else:
                        st.error(
                            data.get("error", "Login failed.")
                        )

        # -------------------- Signup --------------------

        with tab_signup:
            with st.form("signup_form"):
                name = st.text_input(
                    "Full name",
                    key="signup_name"
                )

                email_s = st.text_input(
                    "Email",
                    key="signup_email"
                )

                password_s = st.text_input(
                    "Password",
                    type="password",
                    key="signup_password"
                )

                confirm_s = st.text_input(
                    "Confirm password",
                    type="password",
                    key="signup_confirm"
                )

                submitted_s = st.form_submit_button(
                    "Sign Up",
                    use_container_width=True
                )

            if submitted_s:
                if not name or not email_s or not password_s or not confirm_s:
                    st.error("Please fill in every field.")

                elif password_s != confirm_s:
                    st.error("Passwords do not match.")

                elif len(password_s) < 8:
                    st.error(
                        "Password must be at least 8 characters long."
                    )

                else:
                    status, data = api_call(
                        "POST",
                        "/api/register",
                        json={
                            "name": name,
                            "email": email_s,
                            "password": password_s
                        }
                    )

                    if status == 201:
                        st.success(
                            "Account created! Please log in from the Log In tab."
                        )
                    else:
                        st.error(
                            data.get("error", "Registration failed.")
                        )


# ---------------------------------------------------------------------------
# Movie cards
# ---------------------------------------------------------------------------

def render_movie_card(movie, in_watchlist, key_prefix):
    movie_id = movie["id"]

    title = html.escape(str(movie.get("title", "Untitled")))
    genre = html.escape(str(movie.get("genre", "Unknown")))
    year = html.escape(str(movie.get("year", "")))
    description = html.escape(
        str(movie.get("description", "No description available."))
    )

    poster_url = movie.get("poster_url")

    with st.container():
        # Poster image - fixed width
        if poster_url:
            st.image(
                poster_url,
                width=180
            )
        else:
            st.markdown(
                '<div class="sf-card" '
                'style="text-align:center; padding:50px 10px;">'
                '<div style="font-size:3rem;">🎬</div>'
                '<div class="sf-desc">Poster unavailable</div>'
                '</div>',
                unsafe_allow_html=True
            )

        # Movie information
        st.markdown(
            f"""
            <div class="sf-card">
                <h3>{title}</h3>
                <div class="sf-meta">{genre} &middot; {year}</div>
                <div class="sf-desc">{description}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Watchlist button
        btn_label = (
            "− Remove from Watchlist"
            if in_watchlist
            else "+ Add to Watchlist"
        )

        if st.button(
            btn_label,
            key=f"{key_prefix}_{movie_id}",
            use_container_width=True
        ):
            user_id = st.session_state.user["id"]

            if in_watchlist:
                status, data = api_call(
                    "DELETE",
                    f"/api/watchlist/{user_id}/{movie_id}"
                )
            else:
                status, data = api_call(
                    "POST",
                    "/api/watchlist",
                    json={
                        "user_id": user_id,
                        "movie_id": movie_id
                    }
                )

            if status in (200, 201):
                refresh_watchlist()
                st.rerun()

            else:
                st.error(
                    data.get("error", "Something went wrong.")
                )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def render_dashboard():
    user = st.session_state.user

    first_name = html.escape(
        user.get("name", "User").split(" ")[0]
    )

    st.markdown(f"### Welcome back, {first_name} 👋")
    st.write("")

    # -----------------------------------------------------------------------
    # My Watchlist
    # -----------------------------------------------------------------------

    st.markdown("#### ❤️ My Watchlist")

    status, data = api_call(
        "GET",
        f"/api/watchlist/{user['id']}"
    )

    watchlist = (
        data.get("watchlist", [])
        if status == 200
        else []
    )

    st.session_state.watchlist_ids = {
        movie["id"]
        for movie in watchlist
    }

    if status is None:
        st.error(data.get("error"))

    elif status != 200:
        st.error(data.get("error", "Could not load your watchlist."))

    elif not watchlist:
        st.markdown(
            '<p class="sf-empty">'
            'Your watchlist is empty — add something below.'
            '</p>',
            unsafe_allow_html=True
        )

    else:
        # Five-column watchlist layout
        cols = st.columns(5)

        for i, movie in enumerate(watchlist):
            with cols[i % 5]:
                render_movie_card(
                    movie,
                    in_watchlist=True,
                    key_prefix="wl"
                )

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Browse / Search / Genre filter
    # -----------------------------------------------------------------------

    st.markdown("#### 🎬 Browse Movies & Shows")

    search_col, genre_col = st.columns([2, 1])

    with search_col:
        query = st.text_input(
            "Search by title or genre",
            placeholder="e.g. Sci-Fi, Dark, Money Heist",
            key="movie_search"
        )

    with genre_col:
        genres = fetch_genres()

        genre_options = ["All Genres"] + sorted(
            [g for g in genres if g]
        )

        selected_genre = st.selectbox(
            "Filter by genre",
            options=genre_options,
            key="genre_filter"
        )

    # Build API query parameters
    params = {}

    if query.strip():
        params["q"] = query.strip()

    if selected_genre != "All Genres":
        params["genre"] = selected_genre

    status, data = api_call(
        "GET",
        "/api/movies",
        params=params
    )

    if status is None:
        st.error(data.get("error"))
        return

    if status != 200:
        st.error(
            data.get("error", "Could not load the movie catalog.")
        )
        return

    movies = data.get("movies", [])

    if not movies:
        st.markdown(
            '<p class="sf-empty">'
            'No titles match your search or selected genre.'
            '</p>',
            unsafe_allow_html=True
        )
        return

    st.caption(f"{len(movies)} title(s) found")

    # Five-column movie layout
    cols = st.columns(5)

    for i, movie in enumerate(movies):
        with cols[i % 5]:
            render_movie_card(
                movie,
                in_watchlist=(
                    movie["id"] in st.session_state.watchlist_ids
                ),
                key_prefix="cat"
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

render_header()

if st.session_state.user is None:
    render_auth()
else:
    render_dashboard()