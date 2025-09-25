from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret_key"

db = SQLAlchemy(app)

# Models
class Product(db.Model):
    product_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Location(db.Model):
    location_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(20), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(20), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(20), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

# Home
@app.route('/')
def index():
    return render_template('index.html')

# Products
@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        new_product = Product(product_id=product_id, name=name)
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for('products'))

# Locations
@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_id = request.form['location_id']
        name = request.form['name']
        new_location = Location(location_id=location_id, name=name)
        db.session.add(new_location)
        db.session.commit()
        flash("Location added successfully!", "success")
        return redirect(url_for('locations'))
    return render_template('add_location.html')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        location.name = request.form['name']
        db.session.commit()
        flash("Location updated successfully!", "success")
        return redirect(url_for('locations'))
    return render_template('edit_location.html', location=location)

@app.route('/locations/delete/<location_id>')
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash("Location deleted successfully!", "success")
    return redirect(url_for('locations'))

# Product Movements
@app.route('/movements')
def movements():
    movements = ProductMovement.query.all()
    return render_template('product_movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    products = Product.query.all()
    locations = Location.query.all()
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        product_id = request.form['product_id']
        from_location = request.form['from_location'] or None
        to_location = request.form['to_location'] or None
        qty = int(request.form['qty'])
        new_movement = ProductMovement(
            movement_id=movement_id,
            product_id=product_id,
            from_location=from_location,
            to_location=to_location,
            qty=qty
        )
        db.session.add(new_movement)
        db.session.commit()
        flash("Movement added successfully!", "success")
        return redirect(url_for('movements'))
    return render_template('add_movement.html', products=products, locations=locations)

# Balance
@app.route('/balance')
def balance():
    # Calculate quantity per product per location
    from sqlalchemy import func
    movements = ProductMovement.query.all()
    balance_data = {}
    for m in movements:
        if m.to_location:
            balance_data[(m.product_id, m.to_location)] = balance_data.get((m.product_id, m.to_location), 0) + m.qty
        if m.from_location:
            balance_data[(m.product_id, m.from_location)] = balance_data.get((m.product_id, m.from_location), 0) - m.qty
    balances = []
    for (product_id, location_id), qty in balance_data.items():
        balances.append({'product_id': product_id, 'location_id': location_id, 'qty': qty})
    return render_template('balance.html', balances=balances)

# Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
