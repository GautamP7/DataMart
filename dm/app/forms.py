from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, RadioField, DecimalField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Email, EqualTo, ValidationError
from app import User

class LoginForm(FlaskForm):
    username = StringField('', validators=[InputRequired(), Length(max=64)], render_kw={'placeholder': 'Username'})
    password = PasswordField('', validators=[InputRequired(), Length(max=64)], render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SignUpForm(FlaskForm):
    email = StringField('', validators=[InputRequired(), Email(), Length(min=6, max=128)], render_kw={'placeholder': 'Email'})
    username = StringField('', validators=[InputRequired(), Length(max=64)], render_kw={'placeholder': 'User Name'})
    password = PasswordField('', validators=[InputRequired(), Length(max=64)], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('', validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={'placeholder': 'Confirm Password'})
    accept_tc = BooleanField('I accept the terms and conditions', validators=[InputRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(UserName=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(EmailId=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class DatasetForm(FlaskForm):
    offering_name = StringField('Name of the Offering*', validators=[InputRequired(), Length(max=128)])
    # category = SelectField('Category*', choices=[('1', 'Aeronautics, Space, Defence'), ('2', 'Agriculture, Agri-food'), ('3', 'Audit, Consulting, Accountancy, Management, HR'), ('4', 'Automotive'), ('5', 'Banks, Insurance, Financial Services'), ('6', 'Building, Public Works'), ('7', 'Business, Distribution, E-commerce'), ('8', 'Chemical, Other Industries'), ('9', 'Economic'), ('10', 'Education, Training'), ('11', 'Environment, Energy'), ('12', 'Food, Dining'), ('13', 'Government'), ('14', 'Health, Medicine'), ('15', 'Legal'), ('16', 'Location Lists'), ('17', 'Luxury, Fashion, Beauty, Wellness'), ('18', 'Machine Learning'), ('19', 'Mailing Lists'), ('20', 'Marketing, Publicity, Communication'), ('21', 'Media, Publishing, Arts, Entertainment'), ('22', 'Non-profit and Foundations'), ('23', 'Real Estate'), ('24', 'Sports, Recreation'), ('25', 'Telecommunications, Technology and IT'), ('26', 'Transport, Logistics'), ('27', 'Travel, Tourism, Hotels, Catering')])
    category = SelectField('Category*', choices=[('Aeronautics, Space, Defence', 'Aeronautics, Space, Defence'), ('Agriculture, Agri-food', 'Agriculture, Agri-food'), ('Audit, Consulting, Accountancy, Management, HR', 'Audit, Consulting, Accountancy, Management, HR'), ('Automotive', 'Automotive'), ('Banks, Insurance, Financial Services', 'Banks, Insurance, Financial Services'), ('Building, Public Works', 'Building, Public Works'), ('Business, Distribution, E-commerce', 'Business, Distribution, E-commerce'), ('Chemical, Other Industries', 'Chemical, Other Industries'), ('Economic', 'Economic'), ('Education, Training', 'Education, Training'), ('Environment, Energy', 'Environment, Energy'), ('Food, Dining', 'Food, Dining'), ('Government', 'Government'), ('Health, Medicine', 'Health, Medicine'), ('Legal', 'Legal'), ('Location Lists', 'Location Lists'), ('Luxury, Fashion, Beauty, Wellness', 'Luxury, Fashion, Beauty, Wellness'), ('Machine Learning', 'Machine Learning'), ('Mailing Lists', 'Mailing Lists'), ('Marketing, Publicity, Communication', 'Marketing, Publicity, Communication'), ('Media, Publishing, Arts, Entertainment', 'Media, Publishing, Arts, Entertainment'), ('Non-profit and Foundations', 'Non-profit and Foundations'), ('Real Estate', 'Real Estate'), ('Sports, Recreation', 'Sports, Recreation'), ('Telecommunications, Technology and IT', 'Telecommunications, Technology and IT'), ('Transport, Logistics', 'Transport, Logistics'), ('Travel, Tourism, Hotels, Catering', 'Travel, Tourism, Hotels, Catering')])
    description = TextAreaField('Description*', validators=[InputRequired()], render_kw={"rows": 4})
    region = StringField('Regions Included*', validators=[InputRequired(), Length(max=128)], render_kw={'placeholder': 'Example: Worldwide, North America, Asia, USA, ...'})
    date_created = DateField('Data Created*', format='%m/%d/%Y', validators=[InputRequired()], render_kw={'placeholder': 'MM/DD/YYYY'})
    last_updated = DateField('Data Last Updated*', format='%m/%d/%Y', validators=[InputRequired()], render_kw={'placeholder': 'MM/DD/YYYY'})
    update_frequency = SelectField('Data Update Frequency*', choices=[('1', 'Daily'), ('2', 'Weekly'), ('3', 'Monthly'), ('4', 'Yearly')], default=0)
    dataset_upload = FileField('Dataset*', validators=[FileRequired()])
    sample_upload = FileField('Sample')
    license_upload = FileField('License*', validators=[FileRequired(), FileAllowed(['txt'], 'Text files only!')])
    price = DecimalField('Price*', validators=[InputRequired()])
    submit = SubmitField('Submit')
    suggested_price = StringField('', render_kw={'readonly': True})
    calc = SubmitField('Get Price Suggestion')

class DownloadForm(FlaskForm):
    download = SubmitField('Download')

class SearchForm(FlaskForm):
    search = StringField()
    submit = SubmitField()

class ContactForm(FlaskForm):
    name = StringField('Name*', validators=[InputRequired(), Length(max=64)])
    email = StringField('Email Address*', validators=[InputRequired(), Email(), Length(min=6, max=128)])
    subject = StringField('Subject*', validators=[InputRequired(), Length(max=128)])
    message = TextAreaField('Message*', validators=[InputRequired()], render_kw={"rows": 4})
    send = SubmitField('Send')

class BankForm(FlaskForm):
    name = StringField('Name*', validators=[InputRequired(), Length(max=64)])
    gov_id = StringField('Government ID  Number*', validators=[InputRequired(), Length(max=64)], render_kw={'placeholder': 'Example: SSN in US, TIN in EU'})
    currency = SelectField('Currency*', choices=[('USD', 'USD'), ('AUD', 'AUD'), ('CAD', 'CAD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('INR', 'INR'), ('JPY', 'JPY'), ('SGD', 'SGD')])
    routing_number = StringField('Routing Number*', validators=[InputRequired()], render_kw={'minlength':9, 'maxlength':9})
    account_number = StringField('Account Number*', validators=[InputRequired()], render_kw={'minlength':6, 'maxlength':16})
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name*', validators=[InputRequired(), Length(max=64)])
    last_name = StringField('Last Name*', validators=[InputRequired(), Length(max=64)])
    dob = DateField('Date of Birth*', format='%m/%d/%Y', validators=[InputRequired()], render_kw={'placeholder': 'MM/DD/YYYY'})
    phone = StringField('Phone Number*', validators=[InputRequired(), Length(max=15)])
    address = StringField('Address*', validators=[InputRequired(), Length(max=256)])
    country = StringField('Country*', validators=[InputRequired(), Length(max=64)])
    submit = SubmitField('Save Changes')

class PasswordForm(FlaskForm):
    password = PasswordField('Current Password*', validators=[InputRequired(), Length(max=64)])
    new_password = PasswordField('New Password*', validators=[InputRequired(), Length(max=64)])
    confirm_password = PasswordField('Confirm Password*', validators=[InputRequired(), EqualTo('new_password', message='Passwords must match')])
    update = SubmitField('Update Password')

class DataFileForm(FlaskForm):
    dataset_upload = FileField('Dataset*', validators=[FileRequired()])
    sample_upload = FileField('Sample')
    submit = SubmitField('Submit')
    back = SubmitField('Back')

class LicenseFileForm(FlaskForm):
    license_upload = FileField('License*', validators=[FileRequired(), FileAllowed(['txt'], 'Text files only!')])
    submit = SubmitField('Submit')
    back = SubmitField('Back')

class DetailsForm(FlaskForm):
    offering_name = StringField('Name of the Offering*', validators=[InputRequired(), Length(max=128)])
    description = TextAreaField('Description*', validators=[InputRequired()], render_kw={"rows": 4})
    region = StringField('Regions Included*', validators=[InputRequired(), Length(max=128)], render_kw={'placeholder': 'Example: Worldwide, North America, Asia, USA, ...'})
    last_updated = DateField('Data Last Updated*', format='%m/%d/%Y', validators=[InputRequired()], render_kw={'placeholder': 'MM/DD/YYYY'})
    update_frequency = SelectField('Data Update Frequency*', choices=[('1', 'Daily'), ('2', 'Weekly'), ('3', 'Monthly'), ('4', 'Yearly')], default=0)
    price = DecimalField('Price*', validators=[InputRequired()])
    submit = SubmitField('Submit')
    back = SubmitField('Back')

class DataRemovalForm(FlaskForm):
    message = TextAreaField('Message*', validators=[InputRequired()], render_kw={"rows": 4})
    submit = SubmitField('Submit')
    back = SubmitField('Back')