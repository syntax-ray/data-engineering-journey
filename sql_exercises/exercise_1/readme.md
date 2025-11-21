# Sample SQL Practice Task

This README provides a complete SQL practice exercise consisting of:

* Creating a database with **3 tables**
* Inserting **dummy data**
* Writing and solving **5 SQL queries** involving joins and aggregates

---

## 1. Database Name & Table Names

**Database Name:** `shop_db`

**Tables:**

1. `customers`
2. `orders`
3. `products`

---

## 2. Dummy Data

### **Table: customers**

| customer_id | name        | email                                         |
| ----------- | ----------- | --------------------------------------------- |
| 1           | Alice Otis  | [alice@example.com](mailto:alice@example.com) |
| 2           | Bob Kamau   | [bob@example.com](mailto:bob@example.com)     |
| 3           | Carol Njeri | [carol@example.com](mailto:carol@example.com) |

### **Table: products**

| product_id | product_name | price |
| ---------- | ------------ | ----- |
| 1          | Laptop       | 1200  |
| 2          | Headphones   | 150   |
| 3          | Mouse        | 40    |

### **Table: orders**

| order_id | customer_id | product_id | quantity | order_date |
| -------- | ----------- | ---------- | -------- | ---------- |
| 1        | 1           | 1          | 1        | 2024-01-10 |
| 2        | 1           | 3          | 2        | 2024-01-12 |
| 3        | 2           | 2          | 1        | 2024-02-01 |
| 4        | 3           | 1          | 1        | 2024-02-15 |
| 5        | 2           | 3          | 3        | 2024-03-05 |

---

## 3. SQL Query Tasks (With Questions & Solutions)

### **Query 1 — Total amount spent by each customer**

**Question:** Calculate the total money spent by each customer.

**SQL:**

```sql
SELECT c.name, SUM(p.price * o.quantity) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.name;
```

**Solution Values:**

| name        | total_spent |                 |
| ----------- | ----------- | --------------- |
| Alice Otis  | 1280        | (1×1200 + 2×40) |
| Bob Kamau   | 270         | (1×150 + 3×40)  |
| Carol Njeri | 1200        |                 |

---

### **Query 2 — Number of orders per product**

**Question:** Count how many total units of each product were ordered.

**SQL:**

```sql
SELECT p.product_name, SUM(o.quantity) AS total_units
FROM products p
JOIN orders o ON p.product_id = o.product_id
GROUP BY p.product_name;
```

**Solution Values:**

| product_name | total_units |
| ------------ | ----------- |
| Laptop       | 2           |
| Headphones   | 1           |
| Mouse        | 5           |

---

### **Query 3 — List all customers who ordered laptops**

**Question:** Return names of all customers who bought the product "Laptop".

**SQL:**

```sql
SELECT DISTINCT c.name
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE p.product_name = 'Laptop';
```

**Solution Values:**

| name        |
| ----------- |
| Alice Otis  |
| Carol Njeri |

---

### **Query 4 — Monthly revenue**

**Question:** Calculate total revenue per month.

**SQL:**

```sql
SELECT DATE_TRUNC('month', order_date) AS month,
       SUM(p.price * o.quantity) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY month
ORDER BY month;
```

**Solution Values:**

| month      | revenue |                  |
| ---------- | ------- | ---------------- |
| 2024-01-01 | 1280    |                  |
| 2024-02-01 | 1350    | (1×150 + 1×1200) |
| 2024-03-01 | 120     |                  |

---

### **Query 5 — Largest single order value**

**Question:** Find the highest value of a single order.

**SQL:**

```sql
SELECT o.order_id, (p.price * o.quantity) AS order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id
ORDER BY order_value DESC
LIMIT 1;
```

**Solution Value:**

| order_id | order_value |
| -------- | ----------- |
| 1        | 1200        |

---

## End of Task

You can copy this into your SQL environment and practice creating the database, inserting data, and writing the queries.
