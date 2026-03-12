from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import oracledb
import os
import random
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Initialize Oracle client (update path if needed)
oracledb.init_oracle_client(lib_dir=r"E:\orac\instantclient_23_9")

# Create Flask app
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY")

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# DB connection
dsn = oracledb.makedsn("localhost", 1521, service_name="XE")
conn = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=dsn
)

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

    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, email, phone, password)
            VALUES (:name, :email, :phone, :password)
        """, {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password
        })

        conn.commit()

        return redirect(url_for("index"))

    except oracledb.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

    finally:
        cursor.close()


# LOGIN
@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=:email AND password=:password",
        {"email": email, "password": password}
    )

    user = cursor.fetchone()

    cursor.close()

    if user:
        return redirect(url_for("home"))
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# HOME
@app.route("/home")
def home():
    return render_template("home.html")


# FORGOT PASSWORD PAGE
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

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET password=:password WHERE email=:email",
        {"password": new_password, "email": email}
    )

    conn.commit()

    cursor.close()

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
    app.run(debug=True)