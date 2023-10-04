from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    UserID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Username = db.Column(db.String(20), nullable=False, unique=True)
    Password = db.Column(db.String(80), nullable=False)
    CompanyID = db.Column(db.Integer, db.ForeignKey('company.CompanyID'))

class Company(db.Model):
    CompanyID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    CompanySize = db.Column(db.String(50))
    AlgorandAddress = db.Column(db.String(100))

class PeopleMetrics(db.Model):
    PeopleMetricsID = db.Column(db.Integer, primary_key=True)
    DiversityAndInclusion = db.Column(db.Double)
    PayEquality = db.Column(db.Double)
    WageLevel = db.Column(db.Double)
    HealthAndSafetyLevel = db.Column(db.Double)

class PlanetMetrics(db.Model):
    PlanetMetricsID = db.Column(db.Integer, primary_key=True)
    GreenhouseGasEmission = db.Column(db.Double)
    WaterConsumption = db.Column(db.Double)
    LandUse = db.Column(db.Double)

class ProsperityMetrics(db.Model):
    ProsperityMetricsID = db.Column(db.Integer, primary_key=True)
    TotalTaxPaid = db.Column(db.Double)
    AbsNumberOfNewEmps = db.Column(db.Double)
    AbsNumberOfNewEmpTurnover = db.Column(db.Double)
    EconomicContribution = db.Column(db.Double)
    TotalRNDExpenses = db.Column(db.Double)
    TotalCapitalExpenditures = db.Column(db.Double)
    ShareBuyBacksAndDividendPayments = db.Column(db.Double)

class GovernanceMetrics(db.Model):
    GovernanceMetricsID = db.Column(db.Integer, primary_key=True)
    AntiCorruptionTraining = db.Column(db.Double)
    ConfirmedCorruptionIncidentPrev = db.Column(db.Double)
    ConfirmedCorruptionIncidentCurrent = db.Column(db.Double)

class Report(db.Model):
    ReportID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    ReportPeriod = db.Column(db.String(100))
    CreatedDate = db.Column(db.DateTime)
    CreatedByID = db.Column(db.Integer, db.ForeignKey('user.UserID'))
    CompanyID = db.Column(db.Integer, db.ForeignKey('company.CompanyID'))
    PeopleMetricsID = db.Column(db.Integer, db.ForeignKey('peoplemetrics.PeopleMetricsID'))
    ProsperityMetricsID = db.Column(db.Integer, db.ForeignKey('prosperitymetrics.ProsperityMetricsID'))
    GovernanceMetricsID = db.Column(db.Integer, db.ForeignKey('governancemetrics.GovernanceMetricsID'))
    Status = db.Column(db.String(100))

class Transaction(db.Model):
    TransactionID = db.Column(db.Integer, primary_key=True)
    ReportID = db.Column(db.Integer, db.ForeignKey('report.ReportID'))
    NFTTransactionID = db.Column(db.String(100))
    SubmissionTransactionID = db.Column(db.String(100))
