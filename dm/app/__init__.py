import csv
import datetime
import os
import stripe
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_marshmallow import Marshmallow
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import flask.ext.whooshalchemy as whooshalchemy

from app.pred import *


app = Flask(__name__, template_folder='/var/www/html/dm/app/templates')
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
login = LoginManager()
login.init_app(app)
login.login_view = 'login'

categories = {1:'Aeronautics, Space, Defence', 2:'Agriculture, Agri-food', 3:'Audit, Consulting, Accountancy, Management, HR', 4:'Automotive', 5:'Banks, Insurance, Financial Services', 6:'Building, Public Works', 7:'Business, Distribution, E-commerce', 8:'Chemical, Other Industries', 9:'Economic', 10:'Education, Training', 11:'Environment, Energy', 12:'Food, Dining', 13:'Government', 14:'Health, Medicine', 15:'Legal', 16:'Location Lists', 17:'Luxury, Fashion, Beauty, Wellness', 18:'Machine Learning', 19:'Mailing Lists', 20:'Marketing, Publicity, Communication', 21:'Media, Publishing, Arts, Entertainment', 22:'Non-profit and Foundations', 23:'Real Estate', 24:'Sports, Recreation', 25:'Telecommunications, Technology and IT', 26:'Transport, Logistics', 27:'Travel, Tourism, Hotels, Catering'}
u_freq = {0:'Never', 1:'Daily', 2:'Weekly', 3:'Monthly', 4:'Yearly'}

public_key = 'pk_test_PMPhhrnozYIagucJFWEmIYMb'
secret_key = 'sk_test_oJz6hYp91RRBhj2wvZuZrXf0'
stripe.api_key = secret_key

from app.models import User, UserProfile, Dataset, Sale, BankDetails, DatasetSchema
from app.forms import LoginForm, SignUpForm, DatasetForm, DownloadForm, SearchForm, ContactForm, BankForm, ProfileForm, PasswordForm, \
                        DataFileForm, LicenseFileForm, DetailsForm, DataRemovalForm

whooshalchemy.whoosh_index(app, Dataset)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(UserName=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(UserName=form.username.data, EmailId=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/dataset/upload', methods=['GET', 'POST'])
@login_required
def upload_dataset():
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()

    form = DatasetForm()

    if form.submit.data and form.validate_on_submit():    
        
        odesc = Dataset.query.order_by(Dataset.OfferingId.desc()).first()
        if not odesc:
            o_id = 1
        else:
            o_id = odesc.OfferingId + 1

        o_type = int(request.form['offering_type'])
        df_ext = form.dataset_upload.data.filename.rsplit('.', 1)[1]
        df_name = secure_filename(str(user.UserAccountId) + '-' + str(o_id) + '-df.' + df_ext)
        df_path = os.path.join(app.root_path, 'dataset-files', df_name)
        form.dataset_upload.data.save(os.path.join(app.root_path, 'dataset-files', df_name))

        if form.sample_upload.data:
            sf_ext = form.sample_upload.data.filename.rsplit('.', 1)[1]
            sf_name = secure_filename(str(user.UserAccountId) + '-' + str(o_id) + '-sf.' + sf_ext)
            sf_path = os.path.join(app.root_path, 'sample-files', sf_name)
            form.sample_upload.data.save(os.path.join(app.root_path, 'sample-files', sf_name))
        else:
            sf_name = None
            sf_path = None

        lf_ext = form.license_upload.data.filename.rsplit('.', 1)[1]
        lf_name = secure_filename(str(user.UserAccountId) + '-' + str(o_id) + '-lf.' + lf_ext)
        lf_path = os.path.join(app.root_path, 'license-files', lf_name)
        form.license_upload.data.save(os.path.join(app.root_path, 'license-files', lf_name))

        if o_type == 1:
            uf = 0
        elif o_type == 2:
            uf = int(form.update_frequency.data)

        dataset = Dataset(OfferingName=form.offering_name.data, OfferingType=o_type, Category=form.category.data, \
            Description=form.description.data, Region=form.region.data, DateCreated=form.date_created.data, \
            DateLastUpdated=form.last_updated.data, UpdateFrequency=uf, DataFileName=df_name, DataFilePath=df_path, \
            SampleFileName=sf_name, SampleFilePath=sf_path, LicenseFileName=lf_name, LicenseFilePath=lf_path, \
            Price=form.price.data, owner=user)
        db.session.add(dataset)
        db.session.commit()

        # new_row = [form.offering_name.data, user.UserName, form.category.data, form.region.data, o_type, uf, form.description.data, form.price.data]
        # train_file = os.path.join(app.root_path, 'train.csv')
        # with open(train_file,'a') as fd:
        #     writer = csv.writer(fd, lineterminator='\n')
        #     writer.writerow(new_row)
        
        return redirect(url_for('my_offerings'))

    if form.calc.data and form.offering_name.data and form.description.data and form.region.data:
        
        o_type = int(request.form['offering_type'])
        if o_type == 1:
            uf = 0
        elif o_type == 2:
            uf = int(form.update_frequency.data)

        data = {'name':[form.offering_name.data], 'seller':[user.UserName], 'category':[form.category.data], 'region':[form.region.data], 'offering_type':[o_type], 'update_frequency':[uf], 'description':[form.description.data], 'price':[0]}
        df = pd.DataFrame(data)
        train_file = os.path.join(app.root_path, 'train.csv')
        sug_price = calc_price(df, train_file)
        form.suggested_price.data = 'Suggested Price: $' + str(round(sug_price, 2))

    elif form.calc.data:
        form.suggested_price.data = ''
        flash('Name, Region and Description are required for suggesting price!')

    return render_template('dataset-upload.html', title='Upload Data', form=form)


@app.route('/update-dataset/<int:oid>', methods=['GET', 'POST'])
@login_required
def update_dataset(oid):
    form = DataFileForm()
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    dataset = Dataset.query.filter_by(OfferingId=oid).first()

    if form.submit.data and form.validate_on_submit():
        df_ext = form.dataset_upload.data.filename.rsplit('.', 1)[1]
        df_name = secure_filename(str(user.UserAccountId) + '-' + str(oid) + '-df.' + df_ext)
        df_path = os.path.join(app.root_path, 'data-files', df_name)
        form.dataset_upload.data.save(os.path.join(app.root_path, 'dataset-files', df_name))
        
        if form.sample_upload.data:
            sf_ext = form.sample_upload.data.filename.rsplit('.', 1)[1]
            sf_name = secure_filename(str(user.UserAccountId) + '-' + str(o_id) + '-sf.' + sf_ext)
            sf_path = os.path.join(app.root_path, 'sample-files', sf_name)
            form.sample_upload.data.save(os.path.join(app.root_path, 'sample-files', sf_name))
            dataset.SampleFileName = sf_name
            dataset.SampleFilePath = sf_path
        
        dataset.DataFileName = df_name
        dataset.DataFilePath = df_path
        db.session.commit()
        return redirect(url_for('my_offerings'))

    elif form.back.data:
        return redirect(url_for('my_offerings'))
    
    return render_template('update-dataset.html', title='Update Dataset', form=form, dataset=dataset)


@app.route('/edit-details/<int:oid>', methods=['GET', 'POST'])
@login_required
def update_dataset_details(oid):
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    form = DetailsForm(description=dataset.Description, last_updated=dataset.DateLastUpdated, update_frequency=dataset.UpdateFrequency)
    
    if form.submit.data and form.validate():
        dataset.OfferingName = form.offering_name.data
        dataset.Description = form.description.data
        dataset.Region = form.region.data
        dataset.DateLastUpdated = form.last_updated.data
        dataset.Price = form.price.data
        dataset.UpdateFrequency = form.update_frequency.data
        db.session.commit()
        return redirect(url_for('my_offerings'))

    elif form.back.data:
        return redirect(url_for('my_offerings'))

    return render_template('update-data-details.html', title='Edit Details', form = form, dataset=dataset)


@app.route('/request-removal/<int:oid>', methods=['GET', 'POST'])
@login_required
def remove_dataset(oid):
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    form = DataRemovalForm()
    form.message.data = 'Please delete my dataset, ' + dataset.OfferingName + '.'
    if form.submit.data or form.back.data:
        return redirect(url_for('my_offerings'))        
    return render_template('remove-dataset.html', title='Update Dataset', form=form)


@app.route('/dataset/download/<int:oid>', methods=['GET', 'POST'])
@login_required
def download_dataset(oid):
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    ext = dataset.DataFileName.rsplit('.', 1)[1]
    file_name = dataset.OfferingName.replace(' ', '-').lower() + '.' + ext
    return send_from_directory(directory=os.path.join(app.root_path, 'dataset-files'), filename=dataset.DataFileName, as_attachment=True, \
        attachment_filename=file_name)


@app.route('/sample/download/<int:oid>', methods=['GET', 'POST'])
@login_required
def download_sample(oid):
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    ext = dataset.DataFileName.rsplit('.', 1)[1]
    file_name = dataset.OfferingName.replace(' ', '-').lower() + '-sample.' + ext
    return send_from_directory(directory=os.path.join(app.root_path, 'sample-files'), filename=dataset.SampleFileName, as_attachment=True, \
        attachment_filename=file_name)
    

@app.route('/license/download/<int:oid>', methods=['GET', 'POST'])
@login_required
def download_license(oid):
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    return send_from_directory(directory=os.path.join(app.root_path, 'license-files'), filename=dataset.LicenseFileName, as_attachment=True, \
        attachment_filename='License.txt')
    


@app.route('/update-license/<int:oid>', methods=['GET', 'POST'])
@login_required
def update_license(oid):
    form = LicenseFileForm()
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    dataset = Dataset.query.filter_by(OfferingId=oid).first()

    if form.submit.data and form.validate_on_submit():
        lf_ext = form.license_upload.data.filename.rsplit('.', 1)[1]
        lf_name = secure_filename(str(user.UserAccountId) + '-' + str(oid) + '-lf.' + lf_ext)
        lf_path = os.path.join(app.root_path, 'license-files', lf_name)
        form.license_upload.data.save(os.path.join(app.root_path, 'license-files', lf_name))
        
        dataset.LicenseFileName = lf_name
        dataset.LicenseFilePath = lf_path
        db.session.commit()
        return redirect(url_for('my_offerings'))

    elif form.back.data:
        return redirect(url_for('my_offerings'))
    
    return render_template('update-license.html', title='Update License', form=form, dataset=dataset)


@app.route('/categories', methods=['GET', 'POST'])
def show_category():
    return render_template('categories.html', title='Browse Market', categories=categories)


@app.route('/datasets', methods=['GET', 'POST'])
def show_datasets():
    category_num = int(request.args.get('cn', None))
    category_name = categories[category_num] 
    datasets = Dataset.query.filter_by(Category=category_name).all()
    return render_template('datasets.html', title='Browse Market', category_name=category_name, datasets=datasets)


@app.route('/datasets/all', methods=['GET', 'POST'])
def show_datasets_all():
    datasets = Dataset.query.filter_by().all()
    category_name = 'Full Dataset Listing'
    return render_template('datasets.html', title='Browse Market', category_name=category_name, datasets=datasets)

@app.route('/datasets/<int:oid>/<string:dn>', methods=['GET', 'POST'])
@login_required
def show_dataset_details(oid, dn):
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    uf = u_freq[dataset.UpdateFrequency]
    buyer = Sale.query.filter_by(DatasetId=oid, BuyerId=user.UserAccountId).first()
    return render_template('dataset-description.html', title='Browse Market', dataset=dataset, user=user, buyer=buyer, uf = uf)


@app.route('/datasets/search', methods=['GET', 'POST'])
def search_datasets():
    form = SearchForm()
    query = request.form['search']
    datasets = Dataset.query.whoosh_search(query).all()
    return render_template('search-dataset.html', title='Browse Datasets', form=form, query=query, datasets=datasets)


@app.route('/buy/<int:oid>', methods=['POST'])
@login_required
def buy(oid):
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    dataset = Dataset.query.filter_by(OfferingId=oid).first()
    sale = Sale(SaleDate=datetime.datetime.now(), SellerId=dataset.owner.UserAccountId, BuyerId=user.UserAccountId, \
        SalePrice=dataset.Price,  dataset=dataset)
    
    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=int(dataset.Price*100),
        currency='usd'
    )

    db.session.add(sale)
    db.session.commit()

    new_row = [dataset.OfferingName, dataset.owner.UserName, dataset.Category, dataset.Region, dataset.OfferingType, dataset.UpdateFrequency, dataset.Description, dataset.Price]
    train_file = os.path.join(app.root_path, 'train.csv')
    with open(train_file,'a') as fd:
        writer = csv.writer(fd, lineterminator='\n')
        writer.writerow(new_row)
    
    return redirect(url_for('show_dataset_details', oid=oid, dn=dataset.OfferingName.replace(' ', '-').lower()))

@app.route('/account/offerings', methods=['GET', 'POST'])
@login_required
def my_offerings():
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    offerings = Dataset.query.filter_by(OwnerId=user.UserAccountId).all()
    sales = Sale.query.filter_by(SellerId=user.UserAccountId).all()
    return render_template('account-offerings.html', title='My Data Offerings', offerings=offerings, sales=sales)

@app.route('/account/purchases', methods=['GET', 'POST'])
@login_required
def my_purchases():
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    purchases = Sale.query.filter_by(BuyerId=user.UserAccountId).all()
    return render_template('account-purchases.html', title='My Purchases', purchases=purchases)

@app.route('/account/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form1 = ProfileForm()
    form2 = PasswordForm()
    user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
    
    if form1.submit.data and form1.validate_on_submit():
        if user.Profile == None:
            user_profile = UserProfile(FirstName=form1.first_name.data, LastName=form1.last_name.data, DOB=form1.dob.data, \
                Phone=form1.phone.data, Address=form1.address.data, Country=form1.country.data, owner=user)
            db.session.add(user_profile)
            db.session.commit()
        else:
            user.Profile.FirstName = form1.first_name.data
            user.Profile.LastName = form1.last_name.data
            user.Profile.DOB = form1.dob.data
            user.Profile.Phone = form1.phone.data
            user.Profile.Address = form1.address.data
            user.Profile.Country =  form1.country.data
            db.session.commit()
        flash('Changes succesfully saved!')
        return redirect(url_for('profile'))

    if form2.update.data and form2.validate_on_submit():
        if user is None or not user.check_password(form2.password.data):
            flash('Invalid current password')
            return redirect(url_for('profile'))
        user.set_password(form2.new_password.data)
        db.session.commit()
        flash('Password succesfully updated!')
        return redirect(url_for('profile'))

    return render_template('account-profile.html', title='Profile', form1=form1, form2=form2)

@app.route('/account/payment-details', methods=['GET', 'POST'])
@login_required
def payment_details():
    form = BankForm()
    if form.validate_on_submit():
        user = User.query.filter_by(UserAccountId=current_user.get_id()).first()
        if user.BankDetails == None:
            bank_details = BankDetails(Name=form.name.data, GovId=form.gov_id.data, Currency=form.currency.data, \
                RoutingNumber=form.routing_number.data, AccountNumber=form.account_number.data, owner=user)
            db.session.add(bank_details)
            db.session.commit()
        else:
            user.BankDetails.Name = form.name.data
            user.BankDetails.GovId = form.gov_id.data
            user.BankDetails.Currency = form.currency.data
            user.BankDetails.RoutingNumber = form.routing_number.data
            user.BankDetails.AccountNumber = form.account_number.data
            db.session.commit()
        flash('Details successfully saved')
        return redirect(url_for('payment_details'))
    return render_template('account-payment.html', title='Payment Details', form=form)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/faqs')
def faqs():
    return render_template('faqs.html', title='FAQs')


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html', title='Privacy Policy')


@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms-of-service.html', title='Terms of Service')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        return render_template('contact-ty.html', title='Contact')
    return render_template('contact.html', title='Contact', form=form)

# REST APIs

@app.route('/resources/datasets/all', methods=['GET'])
def get_all_datasets():
    datasets = Dataset.query.with_entities(Dataset.OfferingName, Dataset.Category, Dataset.Description, Dataset.Region, \
        Dataset.DateCreated, Dataset.DateLastUpdated, Dataset.Price).all()
    data_schema = DatasetSchema(many=True)
    ds = data_schema.dump(datasets).data
    return jsonify(datasets=ds)

@app.route('/resources/datasets', methods=['GET'])
def get_datasets():
    if 'cn' in request.args:
        category_num = int(request.args['cn'])
    else:
        return "Error: No cn field provided. Please specify a cn (Catergory number) as a query parameter."
    if category_num > 0 and category_num < 28:
        category_name = categories[category_num]
    else:
        return "Error: No such Catergory number exists."
    datasets = Dataset.query.filter_by(Category=category_name).with_entities(Dataset.OfferingName, Dataset.Category, Dataset.Description, Dataset.Region, \
        Dataset.DateCreated, Dataset.DateLastUpdated, Dataset.Price).all()
    data_schema = DatasetSchema(many=True)
    ds = data_schema.dump(datasets).data
    return jsonify(datasets=ds)    

if __name__ == "__main__":
    app.run(debug=True)
