from app import db, login, ma
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'UserAccount'
    
    UserAccountId = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(64), index=True, unique=True, nullable=False)
    EmailId = db.Column(db.String(128), index=True, unique=True, nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)
    Datasets = db.relationship('Dataset', backref='owner', cascade="all, delete", lazy=True)
    Profile = db.relationship('UserProfile', backref='owner', cascade="all, delete", lazy=True, uselist=False)
    BankDetails = db.relationship('BankDetails', backref='owner', cascade="all, delete", lazy=True, uselist=False)
    Sales = db.relationship('Sale', backref='buyer')

    def get_id(self):
        return(self.UserAccountId)

    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.PasswordHash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Dataset(db.Model):
    __tablename__ = 'Dataset'
    __searchable__ = ['OfferingName', 'Category', 'Description']

    OfferingId = db.Column(db.Integer, primary_key=True)
    OfferingName = db.Column(db.String(128), index=True, nullable=False)
    OfferingType = db.Column(db.Integer, index=True, nullable=False)
    Category = db.Column(db.String(128), index=True, nullable=False)
    Description = db.Column(db.Text, nullable=False)
    Region = db.Column(db.String(128), index=True, nullable=False)
    DateCreated = db.Column(db.DateTime, index=True, nullable=False)
    DateLastUpdated = db.Column(db.DateTime, index=True, nullable=False)
    UpdateFrequency = db.Column(db.Integer, index=True, nullable=False)
    DataFileName = db.Column(db.String(128), index=True, nullable= False)
    DataFilePath = db.Column(db.String(256), nullable=False)
    SampleFileName = db.Column(db.String(128), index=True, nullable= True)
    SampleFilePath = db.Column(db.String(256), nullable=True)
    LicenseFileName = db.Column(db.String(128), index=True, nullable= False)
    LicenseFilePath = db.Column(db.String(256), nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Sales = db.relationship('Sale', backref='dataset', cascade="all, delete", lazy=True)
    OwnerId = db.Column(db.Integer, db.ForeignKey('UserAccount.UserAccountId'), nullable=False)

    def get_id(self):
        return(self.OfferingId)
    
class UserProfile(db.Model):
    __tablename__ = 'UserProfile'
    
    UserProfileId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(64), index=True, nullable=False)
    LastName = db.Column(db.String(64), index=True, nullable=False)
    DOB = db.Column(db.DateTime, nullable=False)
    Phone = db.Column(db.String(15), nullable=False)
    Address = db.Column(db.String(256), nullable=False)
    Country = db.Column(db.String(64), index=True, nullable=False)
    OwnerId = db.Column(db.Integer, db.ForeignKey('UserAccount.UserAccountId'), nullable=False, unique=True)

    def get_id(self):
        return(self.UserProfileId)

class Sale(db.Model):
    __tablename__ = 'Sale'

    SaleId = db.Column(db.Integer, primary_key=True)
    SaleDate = db.Column(db.DateTime, nullable=False)
    SellerId = db.Column(db.Integer, nullable=False)
    BuyerId = db.Column(db.Integer, db.ForeignKey('UserAccount.UserAccountId'), nullable=False)
    SalePrice = db.Column(db.Float, nullable=False)
    DatasetId = db.Column(db.Integer, db.ForeignKey('Dataset.OfferingId'), nullable=False)
    
    def get_id(self):
        return(self.SaleId)

class BankDetails(db.Model):
    __tablename__ = 'BankDetails'

    UserBankId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(64), nullable=False)
    GovId = db.Column(db.String(64), nullable=False)
    Currency = db.Column(db.String(3), nullable=False)
    RoutingNumber = db.Column(db.String(9), nullable=False)
    AccountNumber = db.Column(db.String(16), nullable=False)
    OwnerId = db.Column(db.Integer, db.ForeignKey('UserAccount.UserAccountId'), nullable=False, unique=True)

    def get_id(self):
        return(self.UserBankId)

class DatasetSchema(ma.ModelSchema):
    class Meta:
        model = Dataset