from flask import Flask, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import argparse
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecochain.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return jsonify({
        "status": "success", 
        "message": "Welcome to EcoChain"
        }), 200

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(Email=email).first()
        print(user)

        if user and check_password_hash(user.Password, password):
            login_user(user)
            return jsonify({
                "status": "success", 
                "message": "Logged in successfully"
                }), 200
        
        return jsonify({
            "status": "error", 
            "message": "Invalid email or password"
            }), 401
    
    return jsonify({
        "status": "info", 
        "message": "GET request for login"
        }), 200

@app.route("/logout", methods=["POST"])
def logout():
    # Log out the current user
    logout_user()
    
    return jsonify({
        "status": "success", 
        "message": "Logged out successfully"
    }), 200

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)
        
        new_user = User(Email=email, Password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "User registered successfully"
            }), 201
    
    return jsonify({
        "status": "info", 
        "message": "GET request for register"
        }), 200

# Use this protected decorator for all sensitive information
@app.route('/protected')
@login_required
def protected_route():
    return jsonify({
        "status": "success", 
        "message": "You've successfully accessed a protected route",
        "id": current_user.UserID,
        "email" : current_user.Email
    }), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the Flask app.")
    parser.add_argument('--init', action='store_true', help='Initialize the database tables.')
    args = parser.parse_args()

    if args.init:
        print(" * Initializating database tables")
        with app.app_context():
            db.create_all()

    app.run(debug=True)