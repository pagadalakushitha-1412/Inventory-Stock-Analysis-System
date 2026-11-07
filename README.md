# Inventory and Stock Analysis System

A Flask + MySQL inventory project with product and supplier management, stock movement tracking, low-stock alerts, Pandas/NumPy analysis, Matplotlib charts, and CSV export.

## Features
- Add and edit products and suppliers
- Record stock-in, stock-out, and signed stock adjustments
- Prevent stock-out or adjustments from making stock negative
- Preserve transaction history and calculate stock from opening balance + movements
- Dashboard, reorder alerts, inventory valuation, fast-mover summary
- Three charts and CSV report export
- Health endpoint at `/health`

## Project structure
```text
Inventory_Stock_Analysis_System/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── schema.sql
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── products.html
│   ├── product_form.html
│   ├── suppliers.html
│   ├── transactions.html
│   └── reports.html
└── static/
    └── style.css
```
Charts are generated at runtime under `static/charts/` and are ignored by Git.

## Windows / VS Code setup

### 1. Requirements
Install Python 3.11 or newer, Git for Windows, and MySQL Server 8.0. MySQL Workbench is a database client; it does not replace MySQL Server.

### 2. Create a virtual environment
Open the project folder in VS Code, then choose **Terminal → New Terminal** (PowerShell):
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If PowerShell blocks activation, use Git Bash instead:
```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create the MySQL database
Open MySQL Workbench and connect to your local MySQL Server. Open `schema.sql` and click the lightning-bolt Execute button. If the server is not installed/running, install/start MySQL Server first.

### 4. Configure credentials
Copy `.env.example` to a new file named `.env`. Edit `DATABASE_URL`:
```text
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/inventory_db
SECRET_KEY=put-a-long-random-local-value-here
```
Replace `YOUR_PASSWORD` with your local MySQL root password. Do not include angle brackets. If your password contains URL-special characters such as `@`, `:`, `/`, `#`, or `%`, URL-encode them or create a dedicated MySQL application user. Never commit `.env`.

For a quick local-only trial without MySQL, uncomment the SQLite line in `.env` and comment out the MySQL line:
```text
DATABASE_URL=sqlite:///inventory_dev.db
```
This is a development fallback, not the required MySQL submission configuration.

### 5. Create tables and demo data
With the virtual environment active:
```powershell
flask --app app init-db
```
This creates tables through SQLAlchemy and adds sample data if the database is empty. You may use the SQL schema first; the command remains safe for existing tables.

### 6. Run the application
```powershell
python app.py
```
Open `http://127.0.0.1:5000` in your browser. Test `http://127.0.0.1:5000/health`; a successful database connection returns `{"status":"ok","database":"connected"}`.

## Main routes
- `GET /` — dashboard and charts
- `GET /health` — database health check
- `GET /products` — product list
- `GET, POST /products/add` — create product
- `GET, POST /products/<id>/edit` — edit product details
- `GET, POST /suppliers` — list/add suppliers
- `GET /transactions` — transaction history and form
- `POST /transactions/add` — create stock movement
- `GET /reports` — analysis and valuation
- `GET /reports/csv` — download CSV

## Analysis methodology
- Current stock = opening stock + stock-in − stock-out + signed adjustment quantities.
- Estimated inventory value = current stock × recorded unit cost. This is a simple estimate, not a formal accounting valuation method.
- Low stock means current stock is less than or equal to the configured reorder level.
- Fast-moving products are ranked by cumulative recorded stock-out quantity. No forecasting is performed.
- Charts show stock units by product, stock-in versus stock-out, and estimated value by category.

## Testing checklist
1. Add a product with a unique SKU and non-negative opening stock.
2. Add a supplier and associate it with a product.
3. Record a stock-in transaction and verify current stock rises.
4. Record a stock-out within available stock and verify current stock falls.
5. Attempt a stock-out larger than available stock; it must be rejected.
6. Attempt zero quantity for a movement; it must be rejected.
7. Record a positive and negative adjustment; verify totals reconcile.
8. Check low-stock status at and below reorder level.
9. Try a duplicate SKU and confirm it is rejected by the database.
10. Export the report to CSV.
11. Test `/health` when the database is running and when it is unavailable.

## Important limitation
The application validates stock in the Flask workflow, but this starter project is designed for a single-user academic demo. A production multi-user system should add authentication/authorization, CSRF protection, database-level transactional locking for concurrent stock changes, audit permissions, and automated tests.

## GitHub upload
Create an **empty** GitHub repository. In Git Bash from the project directory:
```bash
git init
git branch -M main
git add .
git status
git commit -m "Initial inventory stock analysis system"
git remote add origin https://github.com/YOUR-USERNAME/Inventory-Stock-Analysis-System.git
git push -u origin main
```
Replace the URL with your repository URL. Confirm `.env` is not listed by `git status` before committing. For later changes:
```bash
git add .
git commit -m "Describe your update"
git push
```
