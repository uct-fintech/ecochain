from flask import Flask, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import argparse
from models import db, User, Transaction, Submission, Peoplemetrics, Planetmetrics, Prosperitymetrics, Governancemetrics
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from algosdk import account
import json
from algotransaction import first_transaction_example
from algosdk.v2client import algod
from asa_creation import createASA, optinASA, transferASA
import json
from base64 import b64decode
from algosdk import transaction
from algosdk.transaction import PaymentTxn
from utils import algod_details
from faker import Faker
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import random

ecochainPK = "4pGX12svaEoBYqBX7WfriGIhUB3VjkeUofm6IM3Y+6b69JOah+47V6+PX/KeLfpDMv683zGwQ2R83pkdj7FwCA=="
ecochainAddress = "7L2JHGUH5Y5VPL4PL7ZJ4LP2IMZP5PG7GGYEGZD432MR3D5ROAEDKWFGRU"
load_dotenv() 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecochain.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this in production
mail = Mail(app)

jwt = JWTManager(app)

db.init_app(app)
CORS(app)
fake = Faker()

@app.route("/")
def home():
    return jsonify({
        "status": "success", 
        "message": "Welcome to EcoChain"
        }), 200

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        email = request.json.get('email')
        password = request.json.get('password')

        print(f"email: {email}, password: {password}")
        
        user = User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.Password, password):
            access_token = create_access_token(identity=user.UserID)
            print("Access token created: ", access_token)
            return jsonify(access_token=access_token, success=True), 200
        
        return jsonify({
            "success": False, 
            "message": "Invalid email or password"
            }), 401

@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        email = request.json.get("email")
        password = request.json.get("password")
        name = request.json.get("name")

        # Check if the email is already in use
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email is already in use"
            }), 400

        hashed_password = generate_password_hash(password)
        private_key, address = account.generate_account()

        #add funds to user account
        transamount = 1000000  #0.3 algos as algo account must have a minimum of 0.1 algo, gas fees are 0.0001 so users have 300 free transactions
        algonote = {"algo top-up": transamount}

        confirmedTxn = first_transaction_example(ecochainPK, ecochainAddress, address, transamount,  algonote)
        
        new_user = User(Email=email, 
                        Password=hashed_password, 
                        Name = name,
                        AlgorandPrivateKey = private_key,
                        AlgorandAddress = address
                        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=new_user.UserID)
            print("Access token created: ", access_token)
            return jsonify(access_token=access_token, success=True), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "An error occurred while registering the user"
            }), 500

@app.route("/update_org", methods=["POST"])
@jwt_required()
def update_org():
    if request.method == "POST":
        location = request.json.get("location")
        industry = request.json.get("industry")
        size = request.json.get("size")
        description = request.json.get("description")

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Update the fields
        user.Location = location
        user.Size = size
        user.Industry = industry
        user.Description = description
        # Commit the changes to the database
        db.session.commit()
        return jsonify(success=True), 200


@app.route("/start_submission", methods=["GET"])
@jwt_required()
def start_submission():
    if request.method == "GET":
        
        # Check if a submission ID already exists in the session
        submission_id = session.get('submission_id')
        
        if not submission_id:
            # If not, create a new Submission record
            current_user_id = get_jwt_identity()
            new_submission = Submission(UserID=current_user_id,
                                        Status=0)
            db.session.add(new_submission)
            db.session.commit()
            submission_id = new_submission.SubmissionID
            session['submission_id'] = submission_id
        
        # Return a success message along with the submission ID.
        return jsonify({
            "success": True, 
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
@jwt_required()
def input_peoplemetrics():
    # Retrieve the submission_id from the session
    submission_id = session.get("submission_id")
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "success": False, 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    data = request.get_json()
    diversity_inclusion = data.get("DiversityAndInclusion")
    pay_equality = data.get("PayEquality")
    wage_level = data.get("WageLevel")
    health_safety_level = data.get("HealthAndSafetyLevel")
    
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
            "success": True, 
            "message": "Metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/input_planetmetrics", methods=["POST"])
@jwt_required()
def input_planetmetrics():

    # Retrieve the submission_id from the session
    submission_id = session.get("submission_id")
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "success": False, 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    data = request.get_json()
    greenhouse_gas_emission = data.get("GreenhouseGasEmission")
    water_consumption = data.get("WaterConsumption")
    land_use = data.get("LandUse")

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
            "success": True, 
            "message": "Planet metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/input_prosperitymetrics", methods=["POST"])
@jwt_required()
def input_prosperitymetrics():

    # Retrieve the submission_id from the session
    submission_id = session.get('submission_id')
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "success": False, 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    data = request.get_json()
    total_tax_paid = data.get("TotalTaxPaid")
    abs_number_of_new_emps = data.get("AbsNumberOfNewEmps")
    abs_number_of_new_emp_turnover = data.get("AbsNumberOfNewEmpTurnover")
    economic_contribution = data.get("EconomicContribution")
    total_rnd_expenses = data.get("TotalRNDExpenses")
    total_capital_expenditures = data.get("TotalCapitalExpenditures")
    share_buybacks_and_dividend_payments = data.get("ShareBuyBacksAndDividendPayments")

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
            "success": True, 
            "message": "Prosperity metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/input_governancemetrics", methods=["POST"])
@jwt_required()
def input_governancemetrics():

    # Retrieve the submission_id from the session
    submission_id = session.get('submission_id')
    
    # Check if submission_id exists in the session
    if not submission_id:
        return jsonify({
            "success": False, 
            "message": "No active submission session found. Start a new submission first."
        }), 400
    data = request.get_json()
    anti_corruption_training = data.get("AntiCorruptionTraining")
    confirmed_corruption_incident_prev = data.get("ConfirmedCorruptionIncidentPrev")
    confirmed_corruption_incident_current = data.get("ConfirmedCorruptionIncidentCurrent")

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
            "success": True, 
            "message": "Governance metrics added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/trans', methods=['GET'])
@jwt_required()
def trans():

    submission_id = session.get('submission_id')
    
    if not submission_id:
        return jsonify({
            "success": False, 
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

    private_key = ecochainPK
    my_address = ecochainAddress
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    rec_address = current_user.AlgorandAddress
    rec_privateKey = current_user.AlgorandPrivateKey
    transamount = 0

    txid, confirmedTxn = first_transaction_example(private_key, my_address, rec_address, transamount,  data)

    # Check if confirmed_txn has the expected structure or keys
    if not confirmedTxn:
        return jsonify({
            "success": False,
            "message": "Failed to confirm the transaction"
        }), 500
    
    txidNFT, confirmed_txnNFT, created_asset = createASA(private_key, my_address, txid)


    if not confirmed_txnNFT:
        return jsonify({
        "success": False,
        "message": "Failed to confirm the transaction"
    }), 500


    signed_optin_txid, Opt_in_confirmed_txn = optinASA (rec_address,rec_privateKey,created_asset)

    if not Opt_in_confirmed_txn:
        return jsonify({
        "success": False,
        "message": "Failed to confirm the transaction"
    }), 500



    asa_receive_txid, user_recieved_confirm = transferASA (my_address, private_key, rec_address, created_asset)

    if not user_recieved_confirm:
        return jsonify({
        "success": False,
        "message": "Failed to confirm the transaction"
    }), 500


    NFTTransactionTransfer = asa_receive_txid
    AlgoTransaction = txid
    NFTTransactionMint = txidNFT
    NFTAsset = created_asset
    
    new_metric = Transaction(
            TransactionID=AlgoTransaction,
            NFTTransactionMintID=NFTTransactionMint,
            NFTTransactionTransferID = NFTTransactionTransfer,
            NFTAssetID=NFTAsset,
            SubmissionID=submission_id
    )
    
    try:
        db.session.add(new_metric)
        db.session.commit()
        user_email = current_user.Email  
        sendEmail(user_email, "Eco Chain ESG Report", AlgoTransaction, NFTAsset)
        return jsonify({
            "success": True,  
            "message": "Transaction recorded successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": str(e)
        }), 500


# Use this protected decorator for all sensitive information
@app.route('/protected')
@jwt_required()
def protected_route():
    user_id = get_jwt_identity()
    current_user = db.session.get(User, user_id)
    return jsonify({
        "success": True,  
        "message": "You've successfully accessed a protected route",
        "id": current_user.UserID,
        "email" : current_user.Email
    }), 200

def sendEmail(recipient, subject, transaction_id, nft_id):
    
    transaction_link = f"https://testnet.algoexplorer.io/tx/{transaction_id}"
    nft_link = f"https://testnet.algoexplorer.io/asset/{nft_id}"

   
    body = f"Thank you for submitting your report. Please find your transaction below: {transaction_link} and the NFT here: {nft_link}."

    msg = Message(subject, sender=('Ecochain', 'ecochain0@gmail.com'), recipients=[recipient])
    msg.body = body
    mail.send(msg)

    flash('Email sent successfully!', 'success') #change this 

   
@app.route('/get_reports')
@jwt_required()
def get_reports():
    if request.method == "GET":
        #return json object with report data for current_user.companyID
        user_id = get_jwt_identity()
        current_user = db.session.get(User, user_id)
        return jsonify({
            "success": True,  
            "message": "You've successfully accessed report data",
            "id": current_user.CompanyID
        }), 200

@app.route('/get_dashboard')
@jwt_required()    
def get_dashboard_data():
    if request.method == "GET":
        user_id = get_jwt_identity()
        current_user = db.session.get(User, user_id)
        subs = Submission.query.filter_by(UserID = user_id).all()

        serialized_subs = [sub.as_dict() for sub in subs]

        return jsonify({
            "success": True,
            "id": current_user.UserID,
            "email" : current_user.Email,
            "name": current_user.Name,
            "algo_add" : current_user.AlgorandAddress,
            "location": current_user.Location,
            "industry" : current_user.Industry,
            "size": current_user.Size,
            "description" : current_user.Description,
            "submissions": serialized_subs
        }), 200

def generate_dummy_data():
    with app.app_context():
        users = User.query.all()

        # Add dummy submissions
        submissions = []
        for user in users:
            for _ in range(3):
                submission = Submission(
                    FirstName=fake.first_name(),
                    LastName=fake.last_name(),
                    Date=fake.date_this_decade(),
                    Year=fake.year(),  # Generate a year
                    Score=random.uniform(0, 100),  # Generate a random score between 0 and 100
                    Status=random.choice([0, 1, 2]),  # Randomly choose a status
                    UserID=user.UserID
                )
                db.session.add(submission)
                submissions.append(submission)

        db.session.commit()

        # Add dummy metrics
        for sub in submissions:
            db.session.add(Peoplemetrics(
                DiversityAndInclusion=fake.random_number(digits=2),
                PayEquality=fake.random_number(digits=2),
                WageLevel=fake.random_number(digits=2),
                HealthAndSafetyLevel=fake.random_number(digits=2),
                SubmissionID=sub.SubmissionID
            ))

            db.session.add(Planetmetrics(
                GreenhouseGasEmission=fake.random_number(digits=2),
                WaterConsumption=fake.random_number(digits=2),
                LandUse=fake.random_number(digits=2),
                SubmissionID=sub.SubmissionID
            ))
            
            db.session.add(Prosperitymetrics(
                TotalTaxPaid=fake.random_number(digits=2),
                AbsNumberOfNewEmps=fake.random_number(digits=2),
                AbsNumberOfNewEmpTurnover=fake.random_number(digits=2),
                EconomicContribution=fake.random_number(digits=2),
                TotalRNDExpenses=fake.random_number(digits=2),
                TotalCapitalExpenditures=fake.random_number(digits=2),
                ShareBuyBacksAndDividendPayments=fake.random_number(digits=2),
                SubmissionID=sub.SubmissionID
            ))
            
            db.session.add(Governancemetrics(
                AntiCorruptionTraining=fake.random_number(digits=2),
                ConfirmedCorruptionIncidentPrev=fake.random_number(digits=2),
                ConfirmedCorruptionIncidentCurrent=fake.random_number(digits=2),
                SubmissionID=sub.SubmissionID
            ))

        db.session.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the Flask app.")
    parser.add_argument('--init', action='store_true', help='Initialize the database tables.')
    args = parser.parse_args()

    
    if args.init:
        print(" * Initializating database tables")
        with app.app_context():
            db.create_all()
            generate_dummy_data()
    else:
        app.run(debug=True)