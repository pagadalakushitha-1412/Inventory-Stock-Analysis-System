CREATE DATABASE IF NOT EXISTS inventory_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE inventory_db;

CREATE TABLE IF NOT EXISTS suppliers (
  supplier_id INT AUTO_INCREMENT PRIMARY KEY,
  supplier_name VARCHAR(120) NOT NULL UNIQUE,
  phone VARCHAR(30),
  email VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50) NOT NULL UNIQUE,
  product_name VARCHAR(150) NOT NULL,
  category VARCHAR(80) NOT NULL DEFAULT 'General',
  opening_stock INT NOT NULL DEFAULT 0,
  reorder_level INT NOT NULL DEFAULT 5,
  unit_cost DECIMAL(10,2) NOT NULL DEFAULT 0,
  supplier_id INT NULL,
  CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id)
    REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
  CONSTRAINT chk_opening_stock CHECK (opening_stock >= 0),
  CONSTRAINT chk_reorder_level CHECK (reorder_level >= 0),
  CONSTRAINT chk_unit_cost CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS stock_transactions (
  transaction_id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  transaction_date DATE NOT NULL,
  transaction_type ENUM('IN','OUT','ADJUST') NOT NULL,
  quantity INT NOT NULL,
  supplier_id INT NULL,
  note VARCHAR(255),
  CONSTRAINT fk_transactions_product FOREIGN KEY (product_id)
    REFERENCES products(product_id),
  CONSTRAINT fk_transactions_supplier FOREIGN KEY (supplier_id)
    REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
  CONSTRAINT chk_transaction_quantity CHECK (quantity <> 0)
);

CREATE INDEX idx_transaction_product_date
  ON stock_transactions(product_id, transaction_date);
