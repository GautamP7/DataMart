# DataMart

DataMart is an online data marketplace web application that allows buying and selling of data. It is developed as part of Master's Project at UIC. The web application is developed in Python and hosted on an AWS EC2 instance. The website can be accessed [here](http://ec2-3-16-246-166.us-east-2.compute.amazonaws.com).

### Salient features
----
The website has the following salient features:  
1. Allows users to buy and sell data of any format.
2. Supports payments through Stripe.
3. Suggests prices for new datasets using machine learning.

### Requirements
----
The high level requirements required for the core functionality of the web application are given here. The rest of the required packages are specied in the `requirements.txt` file.

- Python3
- Flask
- MySQL
- SQLAlchemy
- Stripe
- LightGBM

### Steps to set up the web application
----
1. Create an AWS EC2 instance
2. Install pip3 (`~$ sudo apt-get install python3-pip`)
3. Install virtualenv (`~$ pip3 install virtualenv`)
4. Copy the `dm` directory to the home directory of the EC2 instance using `scp`
5. Setup the virtual environment inside the `dm` directory using `~/dm$ virtualenv venv`
6. Activate the virtual environment using `~/dm$ . venv/bin/activate` 
7. Install the required packages from the `requirements.txt` file using `(venv) ~/dm$ pip install -r requirements.txt`
8. Setup Apache using `~$ sudo apt-get install apache2 libapache2-mod-wsgi-py3`
9. Create a symlink so that the project directory appears in /var/www/html (`~$ sudo ln -sT ~/dm /var/www/html/dm`)
10. Enable wsgi (`~$ sudo a2enmod wsgi`)
11. Configure Apache by copying the contents of the file `000-default.conf` to the file `/etc/apache2/sites-enabled/000-default.conf`
12. Install MySQL (`~$ sudo apt-get install mysql-server`)
13. Create the database, say DataMarket, for the web application (`mysql> create database DataMarket;`)
14. Change the database name, password and other parameters in the `config.py` file accordingly
15. Create the database tables using the following:  
    `(venv) ~/dm$ python`  
    `>>> from app.models import db`  
    `>>> db.create_all()`  
    `>>> exit()`
16. Restart the server using `sudo apachectl restart`
