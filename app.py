from flask import Flask, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import argparse
from models import db, User
from models import Transaction, Submission, Peoplemetrics, Planetmetrics, Prosperitymetrics, Governancemetrics
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from algosdk import account
import json
from algotransaction import first_transaction_example
from algosdk.v2client import algod
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn
from utils import algod_details
from manage_account import get_user_account
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecochain.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)
CORS(app)

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

    # Reset the submission_id in the session
    session.pop('submission_id', None)
    
    return jsonify({
        "status": "success", 
        "message": "Logged out successfully"
    }), 200

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")

        # Check if the email is already in use
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            return jsonify({
                "status": "error",
                "message": "Email is already in use"
            }), 400

        hashed_password = generate_password_hash(password)
        private_key, address = account.generate_account()
        
        new_user = User(Email=email, 
                        Password=hashed_password, 
                        Name = name,
                        AlgorandPrivateKey = private_key,
                        AlgorandAddress = address
                        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return jsonify({
                "status": "success", 
                "message": "User registered and logged in successfully"
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": "An error occurred while registering the user"
            }), 500
            
    return jsonify({
        "status": "info", 
        "message": "GET request for register"
        }), 200

@app.route("/start_submission", methods=["POST"])
@login_required
def start_submission():
    if request.method == "POST":
        first_name = request.form.get("FirstName")
        last_name = request.form.get("LastName")
        
        # Store these names in the current session for further use
        session['first_name'] = first_name
        session['last_name'] = last_name
        
        # Check if a submission ID already exists in the session
        submission_id = session.get('submission_id')
        
        if not submission_id:
            # If not, create a new Submission record
            new_submission = Submission(UserID=current_user.UserID, FirstName=first_name, LastName=last_name)
            db.session.add(new_submission)
            db.session.commit()
            submission_id = new_submission.SubmissionID
            session['submission_id'] = submission_id
        
        # Return a success message along with the submission ID.
        return jsonify({
            "status": "success", 
            "message": "Submission started successfully",
            "submission_id": submission_id
        }), 200

    else:
        # Handle GET or other methods if necessary.
        return jsonify({
            "status": "info", 
            "message": "GET request for start_submission"
        }), 200


@app.route("/input_peoplemetrics", methods=["POST"])
@login_required
def input_peoplemetrics():
        # Retrieve the submission_id from the session
    submission_id = session.get('submission_id')
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "status": "error", 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    
    diversity_inclusion = request.form.get("DiversityAndInclusion")
    pay_equality = request.form.get("PayEquality")
    wage_level = request.form.get("WageLevel")
    health_safety_level = request.form.get("HealthAndSafetyLevel")
    
    existing_metric = Peoplemetrics.query.filter_by(SubmissionID=submission_id).first()
    
    if existing_metric:
        existing_metric.DiversityAndInclusion = diversity_inclusion
        existing_metric.PayEquality = pay_equality
        existing_metric.WageLevel = wage_level
        existing_metric.HealthAndSafetyLevel = health_safety_level
    else:
        new_metric = Peoplemetrics(
            DiversityAndInclusion=diversity_inclusion,
            PayEquality=pay_equality,
            WageLevel=wage_level,
            HealthAndSafetyLevel=health_safety_level,
            SubmissionID=submission_id
        )
        db.session.add(new_metric)
    
    try:
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/input_planetmetrics", methods=["POST"])
@login_required
def input_planetmetrics():

    # Retrieve the submission_id from the session
    submission_id = session.get('submission_id')
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "status": "error", 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    
    greenhouse_gas_emission = request.form.get("GreenhouseGasEmission")
    water_consumption = request.form.get("WaterConsumption")
    land_use = request.form.get("LandUse")

    existing_metric = Planetmetrics.query.filter_by(SubmissionID=submission_id).first()

    if existing_metric:
        existing_metric.GreenhouseGasEmission = greenhouse_gas_emission
        existing_metric.WaterConsumption = water_consumption
        existing_metric.LandUse = land_use
    else:
        new_metric = Planetmetrics(
            GreenhouseGasEmission=greenhouse_gas_emission,
            WaterConsumption=water_consumption,
            LandUse=land_use,
            SubmissionID=submission_id
        )
        db.session.add(new_metric)

    try:
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Planet metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/input_prosperitymetrics", methods=["POST"])
@login_required
def input_prosperitymetrics():

    # Retrieve the submission_id from the session
    submission_id = session.get('submission_id')
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "status": "error", 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    
    total_tax_paid = request.form.get("TotalTaxPaid")
    abs_number_of_new_emps = request.form.get("AbsNumberOfNewEmps")
    abs_number_of_new_emp_turnover = request.form.get("AbsNumberOfNewEmpTurnover")
    economic_contribution = request.form.get("EconomicContribution")
    total_rnd_expenses = request.form.get("TotalRNDExpenses")
    total_capital_expenditures = request.form.get("TotalCapitalExpenditures")
    share_buybacks_and_dividend_payments = request.form.get("ShareBuyBacksAndDividendPayments")

    # Check if an entry with the submission_id already exists
    existing_metric = Prosperitymetrics.query.filter_by(SubmissionID=submission_id).first()

    if existing_metric:
        # Update the existing entry
        existing_metric.TotalTaxPaid = total_tax_paid
        existing_metric.AbsNumberOfNewEmps = abs_number_of_new_emps
        existing_metric.AbsNumberOfNewEmpTurnover = abs_number_of_new_emp_turnover
        existing_metric.EconomicContribution = economic_contribution
        existing_metric.TotalRNDExpenses = total_rnd_expenses
        existing_metric.TotalCapitalExpenditures = total_capital_expenditures
        existing_metric.ShareBuyBacksAndDividendPayments = share_buybacks_and_dividend_payments
    else:
        # Create a new entry
        new_metric = Prosperitymetrics(
            TotalTaxPaid=total_tax_paid,
            AbsNumberOfNewEmps=abs_number_of_new_emps,
            AbsNumberOfNewEmpTurnover=abs_number_of_new_emp_turnover,
            EconomicContribution=economic_contribution,
            TotalRNDExpenses=total_rnd_expenses,
            TotalCapitalExpenditures=total_capital_expenditures,
            ShareBuyBacksAndDividendPayments=share_buybacks_and_dividend_payments,
            SubmissionID=submission_id
        )
        db.session.add(new_metric)
        
    try:
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Prosperity metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/input_governancemetrics", methods=["POST"])
@login_required
def input_governancemetrics():

    # Retrieve the submission_id from the session
    submission_id = session.get('submission_id')
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "status": "error", 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    
    anti_corruption_training = request.form.get("AntiCorruptionTraining")
    confirmed_corruption_incident_prev = request.form.get("ConfirmedCorruptionIncidentPrev")
    confirmed_corruption_incident_current = request.form.get("ConfirmedCorruptionIncidentCurrent")

    existing_metric = Governancemetrics.query.filter_by(SubmissionID=submission_id).first()

    if existing_metric:
        existing_metric.AntiCorruptionTraining = anti_corruption_training
        existing_metric.ConfirmedCorruptionIncidentPrev = confirmed_corruption_incident_prev
        existing_metric.ConfirmedCorruptionIncidentCurrent = confirmed_corruption_incident_current
    else:
        new_metric = Governancemetrics(
            AntiCorruptionTraining=anti_corruption_training,
            ConfirmedCorruptionIncidentPrev=confirmed_corruption_incident_prev,
            ConfirmedCorruptionIncidentCurrent=confirmed_corruption_incident_current,
            SubmissionID=submission_id
        )
        db.session.add(new_metric)


    try:
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Governance metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/trans', methods=['GET'])
@login_required
def trans():

    submission_id = session.get('submission_id')
    
    if not submission_id:
        return jsonify({
            "status": "error", 
            "message": "No active submission session found. Start a new submission first."
        }), 400

    # List of models to fetch data from
    models = [Peoplemetrics, Planetmetrics, Prosperitymetrics, Governancemetrics]

    # Fetch metrics and create a combined dictionary
    data = {}
    for model in models:
        metric = model.query.filter_by(SubmissionID=submission_id).first()
        if metric:
            # Get the column names and values for the metric using introspection
            columns = {column.name: getattr(metric, column.name) for column in inspect(model).columns}
            data.update(columns)

    # Remove the SubmissionID key as it's common and not needed in the output
    data.pop('SubmissionID', None)

    private_key = "4pGX12svaEoBYqBX7WfriGIhUB3VjkeUofm6IM3Y+6b69JOah+47V6+PX/KeLfpDMv683zGwQ2R83pkdj7FwCA=="
    my_address = "7L2JHGUH5Y5VPL4PL7ZJ4LP2IMZP5PG7GGYEGZD432MR3D5ROAEDKWFGRU"
    rec_address = current_user.AlgorandAddress

    AlgoTransaction = first_transaction_example(private_key, my_address, rec_address, data)

    new_metric = Transaction(
            TransactionID=AlgoTransaction,
            SubmissionID=submission_id
    )

    try:
        db.session.add(new_metric)
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Transaction recorded successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



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


@app.route('/get_reports')
@login_required
def get_reports():
    if request.method == "GET":
        #return json object with report data for current_user.companyID
        return jsonify({
            "status": "success", 
            "message": "You've successfully accessed report data",
            "id": current_user.CompanyID
        }), 200

# generate_report_id()
# firstname, lastname, email to receive report
# Creates new report record  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the Flask app.")
    parser.add_argument('--init', action='store_true', help='Initialize the database tables.')
    args = parser.parse_args()

    if args.init:
        print(" * Initializating database tables")
        with app.app_context():
            db.create_all()
    app.run(debug=True)