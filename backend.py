from flask import Flask, request, jsonify, render_template, redirect, url_for
import oracledb
import os

# Initialize Oracle client (update path if needed)
oracledb.init_oracle_client(lib_dir=r"C:\orac\instantclient_23_9")

# Create Flask app
app = Flask(__name__, template_folder="templates")

# DB connection
dsn = oracledb.makedsn("localhost", 1521, service_name="XE")
conn = oracledb.connect(user="system", password="root", dsn=dsn)

# ROUTES
@app.route("/")
def index():
    return render_template("login_signup.html")  # Your login/signup page

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
        """, {"name": name, "email": email, "phone": phone, "password": password})
        conn.commit()
        # Redirect to login page after successful registration
        return redirect(url_for("index"))
    except oracledb.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    finally:
        cursor.close()

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=:email AND password=:password", 
                   {"email": email, "password": password})
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        return redirect(url_for("home"))
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/home")
def home():
    return render_template("home.html")

# Other pages
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

if __name__ == "__main__":
    app.run(debug=True)
