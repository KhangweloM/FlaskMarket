from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import pytz  # Importing pytz library


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:201429182@localhost:5432/pagila'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    imported_date = db.Column(db.DateTime, default=datetime.utcnow)  # New column

    def __repr__(self):
        return f"{self.name} - ${self.price}"

with app.app_context():
    db.create_all()




@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market')
def market_page():
    items = [
        {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
        {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
        {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
    ]
    return render_template('market.html', items=items)


@app.route('/products', methods=['GET', 'POST'])
def view_products():
    if request.method == 'POST':
        new_product_name = request.form['name']
        new_product_price = float(request.form['price'])
        new_product = Product(name=new_product_name, price=new_product_price)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('view_products'))

    products = Product.query.all()
    return render_template('products.html', products=products)


# New route to handle form submission
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['product_name']
    price = float(request.form['price'])
    new_product = Product(name=name, price=price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('view_products'))


@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            try:
                # Read the CSV file into a Pandas DataFrame
                df = pd.read_csv(uploaded_file)
                
                # Get the current date and time in UTC
                current_time_utc = datetime.now(pytz.utc)
                
                # Convert to South African time zone
                sa_tz = pytz.timezone('Africa/Johannesburg')
                current_time_sast = current_time_utc.astimezone(sa_tz)
                
                # Iterate through the DataFrame and add each row to the database
                for index, row in df.iterrows():
                    new_product = Product(name=row['name'], price=row['price'], imported_date=current_time_sast)
                    db.session.add(new_product)
                db.session.commit()
                return redirect(url_for('view_products'))
            except Exception as e:
                return str(e), 400  # Return the exception for debugging
    return render_template('upload.html')


