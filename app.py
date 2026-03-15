from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
import random
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)


# DATABASE CONNECTION (SQLite)




# ADMIN CREDENTIALS from environment variables
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# CREATE USERS TABLE
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


create_table()


# ADMIN LOGIN
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_users"))

        return "Invalid admin credentials"

    return render_template("admin_login.html")


# ADMIN USERS PAGE
@app.route("/admin/users")
def admin_users():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, email, phone FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("admin_users.html", users=users)


# ADMIN LOGOUT
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


# ROUTES

@app.route("/")
def index():
    return render_template("login_signup.html")


# SIGNUP

@app.route("/signup", methods=["POST"])
def signup():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "INSERT INTO users (name,email,phone,password) VALUES (?,?,?,?)",
            (name, email, phone, password)
        )

        conn.commit()

        return redirect(url_for("index"))

    except sqlite3.IntegrityError:

        return jsonify({"error": "Email already exists"}), 400

    finally:
        conn.close()


# LOGIN

@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()

    conn.close()

    if user:
        return redirect(url_for("home"))
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# HOME

@app.route("/home")
def home():
    return render_template("home.html")


# FORGOT PASSWORD

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


# SEND OTP

@app.route("/send-otp", methods=["POST"])
def send_otp():

    email = request.form.get("email")

    otp = str(random.randint(100000, 999999))

    session["otp"] = otp
    session["reset_email"] = email

    msg = Message(
        "Password Reset OTP",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[email]
    )

    msg.body = f"Your OTP for password reset is {otp}"

    mail.send(msg)

    return render_template("verify_otp.html")


# VERIFY OTP

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    user_otp = request.form.get("otp")

    if user_otp == session.get("otp"):
        return render_template("reset_password.html")
    else:
        return "Invalid OTP"


# RESEND OTP

@app.route("/resend-otp")
def resend_otp():

    email = session.get("reset_email")

    otp = str(random.randint(100000, 999999))

    session["otp"] = otp

    msg = Message(
        "Resent OTP",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[email]
    )

    msg.body = f"Your new OTP is {otp}"

    mail.send(msg)

    return render_template("verify_otp.html")


# RESET PASSWORD

@app.route("/reset-password", methods=["POST"])
def reset_password():

    new_password = request.form.get("password")
    email = session.get("reset_email")

    conn = get_db_connection()

    conn.execute(
        "UPDATE users SET password=? WHERE email=?",
        (new_password, email)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# CYBER AWARENESS PAGES

@app.route("/cyber-hygiene")
def cyber_hygiene():
    return render_template("cyber-hygiene.html")


@app.route("/financial-frauds")
def financial_frauds():
    return render_template("financial-frauds.html")


@app.route("/malware-threats")
def malware_threats():
    return render_template("malware-threats.html")


@app.route("/mobile-frauds")
def mobile_frauds():
    return render_template("mobile-frauds.html")


@app.route("/online-scams")
def online_scams():
    return render_template("online-scams.html")


@app.route("/personal-threats")
def personal_threats():
    return render_template("personal-threats.html")


@app.route("/social-engineering")
def social_engineering():
    return render_template("social-engineering.html")


@app.route("/help-and-support")
def help_and_support():
    return render_template("help-and-support.html")


# RUN APP

if __name__ == "__main__":
    app.run()
