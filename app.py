import os
import re
import sqlite3

from flask import (
    Flask, render_template, request, flash,
    redirect, url_for, jsonify
)

import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


db.init_db()

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


NAV_LINKS = [
    ("Home", "home"),
    ("About", "about"),
    ("Socials", "socials"),
    ("Newsletter", "newsletter"),
]


@app.context_processor
def inject_globals():
    return {
        "nav_links": NAV_LINKS,
        "subscriber_count": db.count_subscribers(),
    }


@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/socials")
def socials():
    return render_template("socials.html")


@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        moment = request.form.get("moment", "").strip()

        error = None
        if not name or not email:
            error = "Name and email are required."
        elif len(name) > 80 or len(moment) > 500:
            error = "Name or message is too long."
        elif not EMAIL_REGEX.match(email):
            error = "Please enter a valid email."
        elif db.email_exists(email):
            error = "You're already subscribed!"

        if error:
            flash(error, "error")
            
            return render_template(
                "newsletter.html", name=name, email=email, moment=moment
            ), 400

        try:
            db.add_subscriber(name, email, moment)
        except sqlite3.IntegrityError:
            flash("You're already subscribed!", "error")
            return redirect(url_for("newsletter"))

        flash("You're on the list! Welcome to the community.", "success")
        return redirect(url_for("newsletter"))

    return render_template("newsletter.html")



@app.route("/api/subscribers")
def api_subscribers():
    return jsonify({"subscribers": db.count_subscribers()})



@app.route("/admin/subscribers")
def admin_subscribers():
    if request.args.get("key") != os.environ.get("ADMIN_KEY", "haaland123"):
        return "Unauthorized", 401
    return jsonify(db.get_all_subscribers())


if __name__ == "__main__":
    app.run(debug=True)