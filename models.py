from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    UserID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Password = db.Column(db.String(80), nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    AlgorandPrivateKey = db.Column(db.String(100))
    AlgorandAddress = db.Column(db.String(100))
    Location = db.Column(db.String(100))
    Industry = db.Column(db.String(100))
    Size = db.Column(db.String(100))
    Description = db.Column(db.String())
    

    def get_id(self):
        return str(self.UserID)

class Submission(db.Model):
    SubmissionID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(100))
    LastName = db.Column(db.String(100))
    Date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    StartPeriod = db.Column(db.Date, nullable=False)
    EndPeriod = db.Column(db.Date, nullable=False)
    Year = db.Column(db.Integer)
    Score = db.Column(db.Double)
    Status = db.Column(db.Integer) # 0: in progress, 1: complete, 2: rejected
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Peoplemetrics(db.Model):
    PeopleMetricsID = db.Column(db.Integer, primary_key=True)
    DiversityAndInclusion = db.Column(db.Double)
    PayEquality = db.Column(db.Double)
    WageLevel = db.Column(db.Double)
    HealthAndSafetyLevel = db.Column(db.Double)
    SubmissionID = db.Column(db.Integer, db.ForeignKey('submission.SubmissionID'))

class Planetmetrics(db.Model):
    PlanetMetricsID = db.Column(db.Integer, primary_key=True)
    GreenhouseGasEmission = db.Column(db.Double)
    WaterConsumption = db.Column(db.Double)
    LandUse = db.Column(db.Double)
    SubmissionID = db.Column(db.Integer, db.ForeignKey('submission.SubmissionID'))

class Prosperitymetrics(db.Model):
    ProsperityMetricsID = db.Column(db.Integer, primary_key=True)
    TotalTaxPaid = db.Column(db.Double)
    AbsNumberOfNewEmps = db.Column(db.Double)
    AbsNumberOfNewEmpTurnover = db.Column(db.Double)
    EconomicContribution = db.Column(db.Double)
    TotalRNDExpenses = db.Column(db.Double)
    TotalCapitalExpenditures = db.Column(db.Double)
    ShareBuyBacksAndDividendPayments = db.Column(db.Double)
    SubmissionID = db.Column(db.Integer, db.ForeignKey('submission.SubmissionID'))

class Governancemetrics(db.Model):
    GovernanceMetricsID = db.Column(db.Integer, primary_key=True)
    AntiCorruptionTraining = db.Column(db.Double)
    ConfirmedCorruptionIncidentPrev = db.Column(db.Double)
    ConfirmedCorruptionIncidentCurrent = db.Column(db.Double)
    SubmissionID = db.Column(db.Integer, db.ForeignKey('submission.SubmissionID'))

class Transaction(db.Model):
    TransactionID = db.Column(db.String(100), primary_key=True)
    NFTTransactionMintID = db.Column(db.String(100))
    NFTTransactionTransferID = db.Column(db.String(100))
    NFTAssetID = db.Column(db.String(100))
    SubmissionID = db.Column(db.Integer, db.ForeignKey('submission.SubmissionID'))

class Report(db.Model):
    ReportID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    ReportPeriod = db.Column(db.String(100))
    CreatedDate = db.Column(db.DateTime)
    CreatedByID = db.Column(db.Integer, db.ForeignKey('user.UserID'))
    PeopleMetricsID = db.Column(db.Integer, db.ForeignKey('peoplemetrics.PeopleMetricsID'))
    PlanetMetricsID = db.Column(db.Integer, db.ForeignKey('planetmetrics.PlanetMetricsID'))
    ProsperityMetricsID = db.Column(db.Integer, db.ForeignKey('prosperitymetrics.ProsperityMetricsID'))
    GovernanceMetricsID = db.Column(db.Integer, db.ForeignKey('governancemetrics.GovernanceMetricsID'))
    Status = db.Column(db.String(100))