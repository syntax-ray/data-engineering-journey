-- create db

create database shop_db;

-- create customers

create table shop_db.public.customers (
    customer_id serial primary key,
    name varchar not null,
    email varchar not null
);

insert into customers (name, email) values
('Alice Otis', 'ao@gmail.com'),
('Bob Kamau', 'bk@gmail.com'),
('Carol Njeri', 'cn@gmail.com');

select * from customers;

-- create products

create table shop_db.public.products (
    product_id serial primary key,
    product_name varchar not null,
    price decimal(6, 2) not null
);

insert into products(product_name, price) values
('Laptop',1200),
('Headphones',150),
('Mouse',40);

select * from products;

-- create orders

create table shop_db.public.orders (
    order_id serial primary key,
    customer_id bigint references customers(customer_id),
    product_id bigint references products(product_id),
    quantity int not null,
    order_date date not null
);

insert into orders(customer_id, product_id, quantity, order_date) values
(1, 1, 1, '2024-01-10'),
(1, 3, 2, '2024-01-12'),
(2, 2, 1, '2024-02-01'),
(3, 1, 1, '2024-02-15'),
(2, 3, 3, '2024-03-05');

select * from orders;

-- Query 1 (Total spent by each customer)

with
joined as (
select
    order_id,
    c.name,
    quantity,
    p.price,
    p.price * quantity  as total_product_amount
from orders
left join public.products p on p.product_id = orders.product_id
left join public.customers c on orders.customer_id = c.customer_id
)

select
    name,
    sum(total_product_amount) as total_amount_spent
from joined
group by
    name

-- Query 2 (Number of orders per product)

select
    p.product_name,
    sum(quantity) as number_of_orders
from orders
left join public.products p on p.product_id = orders.product_id
group by
    p.product_name

-- Query 3 (List all customerrs who ordered laptops)

select
    distinct
    c.name as customer_name
from orders
left join public.customers c on c.customer_id = orders.customer_id
where
    product_id = (select product_id from products where lower(product_name) = 'laptop');

-- Query 4 (Calculate total revenue per month.

with
joined as (
select
    case
        when date_part('month', order_date) = 1 then 'January'
        when date_part('month', order_date) = 2 then 'February'
        when date_part('month', order_date) = 3 then 'March'
    end                 as month,
    p.product_id,
    quantity * price    as total_product_amount

from orders
left join public.products p on p.product_id = orders.product_id)
select
  month,
  sum(total_product_amount) as total_revenue
from joined
group by
    month;

-- Query 5 (Largest single order value)

with
order_value
as (
    select
        o.order_id,
        o.quantity * p.price        as total_amount,
        c.name                      as customer_name,
        p.product_name



    from orders as o
    left join public.products p on p.product_id = o.product_id
    left join public.customers c on c.customer_id = o.customer_id
),

ranked_order_values
as (
    select
        *,
        row_number() over (order by total_amount desc) as rn

    from order_value
)

select
    customer_name,
    product_name,
    total_amount
from ranked_order_values where rn = 1

