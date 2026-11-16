
import os
import re
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = Path(__file__).with_name("waitlist.db")


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS waitlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                zipcode TEXT NOT NULL,
                vehicle TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        # Hidden field used to discourage simple spam bots.
        if request.form.get("website"):
            return redirect(url_for("home"))

        email = request.form.get("email", "").strip().lower()
        zipcode = request.form.get("zipcode", "").strip()
        vehicle = request.form.get("vehicle", "").strip()

        if (
            not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
            or len(email) > 254
            or not re.fullmatch(r"\d{5}", zipcode)
            or not 1 <= len(vehicle) <= 100
        ):
            error = "Please enter a valid email, ZIP code and vehicle."
        else:
            try:
                with sqlite3.connect(DATABASE) as conn:
                    conn.execute(
                        """
                        INSERT INTO waitlist (email, zipcode, vehicle)
                        VALUES (?, ?, ?)
                        """,
                        (email, zipcode, vehicle)
                    )
                return redirect(url_for("home", success="1"))
            except sqlite3.IntegrityError:
                error = "This email is already on our interest list."

    return render_template(
        "index.html",
        success=request.args.get("success") == "1",
        error=error
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
