from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zaq1@WSX"

# BAZA SQL

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            points INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

init_db()

# STRONA GŁÓWNA

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# REJESTRACJA

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Użytkownik już istnieje"

    return render_template("register.html")

# LOGOWANIE

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        return "Błędne dane logowania"

    return render_template("login.html")

# PANEL UŻYTKOWNIKA

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

# GRA - PISANIE

@app.route("/game")
def game():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("game.html", username=session["username"])

# ZAPIS WYNIKU

@app.route("/save_score", methods=["POST"])
def save_score():
    if "user_id" not in session:
        return "Unauthorized", 401

    points = int(request.form["points"])

    if points <= 0:
        return "Ignored"

    conn = get_db()
    conn.execute(
        "INSERT INTO scores (user_id, points) VALUES (?, ?)",
        (session["user_id"], points)
    )
    conn.commit()
    conn.close()

    return "OK"

# TABELA WYNIKÓW

@app.route("/leaderboard")
def leaderboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    scores = conn.execute("""
        SELECT users.username, scores.points
        FROM scores
        JOIN users ON users.id = scores.user_id
        WHERE scores.points > 0
        ORDER BY scores.points DESC
        LIMIT 10
    """).fetchall()
    conn.close()

    return render_template(
        "leaderboard.html",
        username=session["username"],
        scores=scores
    )

# LISTA UŻYTKOWNIKÓW 

@app.route("/users")
def users():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    users_list = conn.execute(
        "SELECT username FROM users"
    ).fetchall()
    conn.close()

    return render_template(
        "users.html", 
        username=session["username"], 
        users=users_list
    )

# USTAWIENIA/ZMIANA HASŁA

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None
    success = None
    old_password = None
    new_password = None
    confirm_password = None

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        conn = get_db()
        user = conn.execute(
            "SELECT password FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if not user:
            error = "Nie znaleziono użytkownika"
        elif not check_password_hash(user["password"], old_password):
            error = "Podanno nieprawidłowe aktualne hasło"
        elif new_password != confirm_password:
            error = "Nowe hasła nie są identyczne"
        else:
            hashed = generate_password_hash(new_password)
            conn.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hashed, session["user_id"])
            )
            conn.commit()
            success = "Hasło zostało poprawnie zmienione"

        conn.close()
   
    return render_template(
        "settings.html",
        username=session["username"],
        error=error,
        success=success
    )
  
# WYLOGOWANIE

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)