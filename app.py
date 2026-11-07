

import os
import csv
import io
from datetime import datetime
from decimal import Decimal

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, send_file
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, URL
from dotenv import load_dotenv

load_dotenv(".env", override=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "inventory-secret-key")

db_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "inventory_db")
)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# DATABASE MODELS

class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))

    products = db.relationship("Product", backref="supplier", lazy=True)


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="General")
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.supplier_id"))
    opening_stock = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=5)
    unit_price = db.Column("unit_price", db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    transactions = db.relationship(
        "StockTransaction",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def current_stock(self):
        movements = StockTransaction.query.filter_by(
            product_id=self.product_id
        ).all()

        stock = self.opening_stock

        for movement in movements:
            if movement.transaction_type == "IN":
                stock += movement.quantity
            elif movement.transaction_type == "OUT":
                stock -= movement.quantity

        return stock


class StockTransaction(db.Model):
    __tablename__ = "stock_transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.product_id"),
        nullable=False
    )
    transaction_type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.now)
    note = db.Column("notes", db.Text)


# DASHBOARD

@app.route("/")
def dashboard():
    products = Product.query.all()

    total_units = sum(p.current_stock for p in products)

    total_value = sum(
        (Decimal(p.current_stock) * Decimal(p.unit_price or 0))
        for p in products
    )

    low_stock = [
        p for p in products
        if p.current_stock <= p.reorder_level
    ]

    return render_template(
        "dashboard.html",
        products=products,
        total_units=total_units,
        total_value=total_value,
        low_stock=low_stock
    )


# PRODUCTS

@app.route("/products")
def products():
    all_products = Product.query.all()

    return render_template(
        "products.html",
        products=all_products
    )


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    suppliers = Supplier.query.all()

    if request.method == "POST":
        try:
            product = Product(
                product_name=request.form["product_name"],
                category=request.form.get("category") or "General",
                supplier_id=request.form.get("supplier_id") or None,
                opening_stock=int(request.form.get("opening_stock", 0)),
                reorder_level=int(request.form.get("reorder_level", 5)),
                unit_price=Decimal(request.form.get("unit_price", "0"))
            )

            if product.opening_stock < 0 or product.reorder_level < 0 or product.unit_price < 0:
                flash("Values cannot be negative.", "danger")
                return redirect(url_for("add_product"))

            db.session.add(product)
            db.session.commit()

            flash("Product added successfully!", "success")
            return redirect(url_for("products"))

        except (ValueError, KeyError):
            db.session.rollback()
            flash("Please enter valid product details.", "danger")
            return redirect(url_for("add_product"))

    return render_template(
        "product_form.html",
        product=None,
        suppliers=suppliers
    )


@app.route("/delete_product/<int:product_id>")
def delete_product(product_id):
    product = db.session.get(Product, product_id)

    if product:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully!", "success")

    return redirect(url_for("products"))


# SUPPLIERS

@app.route("/suppliers")
def suppliers():
    all_suppliers = Supplier.query.all()

    return render_template(
        "suppliers.html",
        suppliers=all_suppliers
    )


@app.route("/add_supplier", methods=["GET", "POST"])
def add_supplier():
    if request.method == "POST":
        supplier = Supplier(
            supplier_name=request.form["supplier_name"],
            phone=request.form.get("phone"),
            email=request.form.get("email")
        )

        db.session.add(supplier)
        db.session.commit()

        flash("Supplier added successfully!", "success")
        return redirect(url_for("suppliers"))

    return render_template("add_supplier.html")


# TRANSACTIONS

@app.route("/transactions")
def transactions():
    all_transactions = StockTransaction.query.order_by(
        StockTransaction.transaction_id.desc()
    ).all()

    products = Product.query.all()

    return render_template(
        "transactions.html",
        transactions=all_transactions,
        products=products
    )


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    try:
        product_id = int(request.form["product_id"])
        transaction_type = request.form["transaction_type"]
        quantity = int(request.form["quantity"])

        product = db.session.get(Product, product_id)

        if not product or quantity <= 0:
            flash("Enter valid transaction details.", "danger")
            return redirect(url_for("transactions"))

        if transaction_type not in ("IN", "OUT"):
            flash("Invalid transaction type.", "danger")
            return redirect(url_for("transactions"))

        if transaction_type == "OUT" and quantity > product.current_stock:
            flash("Insufficient stock! Stock cannot become negative.", "danger")
            return redirect(url_for("transactions"))

        transaction = StockTransaction(
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            transaction_date=datetime.now(),
            note=request.form.get("note")
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Stock transaction recorded successfully!", "success")

    except (ValueError, KeyError):
        db.session.rollback()
        flash("Please enter valid transaction details.", "danger")

    return redirect(url_for("transactions"))


# REPORTS

@app.route("/reports")
def reports():
    products = Product.query.all()

    rows = []
    fast_movers = []

    total_units = 0
    total_value = Decimal("0.00")
    low_count = 0

    for product in products:
        stock_in = db.session.query(
            func.coalesce(func.sum(StockTransaction.quantity), 0)
        ).filter_by(
            product_id=product.product_id,
            transaction_type="IN"
        ).scalar()

        stock_out = db.session.query(
            func.coalesce(func.sum(StockTransaction.quantity), 0)
        ).filter_by(
            product_id=product.product_id,
            transaction_type="OUT"
        ).scalar()

        current_stock = product.current_stock
        value = Decimal(current_stock) * Decimal(product.unit_price or 0)

        total_units += current_stock
        total_value += value

        status = (
            "LOW STOCK"
            if current_stock <= product.reorder_level
            else "OK"
        )

        if status == "LOW STOCK":
            low_count += 1

        rows.append({
            "Product ID": product.product_id,
            "Product": product.product_name,
            "Opening stock": product.opening_stock,
            "Stock in": stock_in,
            "Stock out": stock_out,
            "Current stock": current_stock,
            "Reorder level": product.reorder_level,
            "Unit price": product.unit_price,
            "Estimated value": value,
            "Status": status
        })

        if stock_out > 0:
            fast_movers.append({
                "Product": product.product_name,
                "Stock out": stock_out
            })

    fast_movers.sort(
        key=lambda item: item["Stock out"],
        reverse=True
    )

    summary = {
        "product_count": len(products),
        "total_units": total_units,
        "total_value": total_value,
        "low_count": low_count,
        "fast_movers": fast_movers[:5]
    }

    return render_template(
        "reports.html",
        summary=summary,
        rows=rows
    )


# CSV EXPORT

@app.route("/export")
def export():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Product ID",
        "Product Name",
        "Category",
        "Opening Stock",
        "Current Stock",
        "Reorder Level",
        "Unit Price"
    ])

    for product in Product.query.all():
        writer.writerow([
            product.product_id,
            product.product_name,
            product.category,
            product.opening_stock,
            product.current_stock,
            product.reorder_level,
            product.unit_price
        ])

    memory_file = io.BytesIO(output.getvalue().encode("utf-8"))
    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="inventory_report.csv"
    )


# RUN APPLICATION

if __name__ == "__main__":
    app.run(debug=True)
