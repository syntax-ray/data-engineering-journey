import json
import pandas as pd
import os

# ==========================================
# PART 0: SETUP (Generates Dummy Data Files)
# ==========================================
# I am writing these files to your disk so the rest of the script has something to read.

def create_dummy_files():
    # 1. Create the JSON Data (Raw Orders)
    dummy_json = [
        {
            "order_id": "ORD-1001",
            "customer": {"id": 501, "name": "Alice Smith", "vip": True},
            "items": [
                {"product": "Laptop", "price_gbp": 800.00},
                {"product": "Mouse", "price_gbp": 25.50}
            ],
            "status": "completed"
        },
        {
            "order_id": "ORD-1002",
            "customer": {"id": 502, "name": "Bob Jones", "vip": False},
            "items": [
                {"product": "Monitor", "price_gbp": 150.00}
            ],
            "status": "pending"
        },
        {
            "order_id": "ORD-1003",
            "customer": {"id": 503, "name": "Charlie Day", "vip": True},
            "items": [
                {"product": "Keyboard", "price_gbp": 45.00},
                {"product": "Headset", "price_gbp": 30.00},
                {"product": "Webcam", "price_gbp": 25.00}
            ],
            "status": "completed"
        }
    ]

    # 2. Create the CSV Data (Exchange Rates)
    # A simple reference table mapping currency codes to conversion rates
    dummy_csv_content = "currency_code,rate_to_usd,last_updated\nGBP,1.27,2025-01-01\nEUR,1.08,2025-01-01\nJPY,0.0065,2025-01-02"

    # Write files to disk
    with open('./orders.json', 'w') as f:
        json.dump(dummy_json, f, indent=4)
    
    with open('./exchange_rates.csv', 'w') as f:
        f.write(dummy_csv_content)

    print("✅ Setup complete: 'orders.json' and 'exchange_rates.csv' created.")
    print("-" * 50)

# Run the setup
create_dummy_files()


# ==========================================
# TASK 1: PARSE JSON (Using standard library)
# ==========================================
print("\n--- Task 1: Parsing JSON ---")

# Load the file
with open('./orders.json', 'r') as f:
    raw_data = json.load(f)

# Challenge: The data is nested. We want a "flat" list of orders.
# We want to extract: Order ID, Customer Name, and the Sum of all item prices.
parsed_orders = []

for entry in raw_data:
    # 1. Extract simple fields
    o_id = entry['order_id']
    c_name = entry['customer']['name']
    
    # 2. Calculate total price from the list of items
    # List comprehension to sum the 'price_gbp' of every item in the list
    total_gbp = sum([item['price_gbp'] for item in entry['items']])
    
    parsed_orders.append({
        "order_id": o_id,
        "customer_name": c_name,
        "total_gbp": total_gbp
    })

print("Parsed Data (List of Dicts):")
for order in parsed_orders:
    print(order)


# ==========================================
# TASK 2: READ/WRITE CSV (Using Pandas)
# ==========================================
print("\n--- Task 2: Pandas CSV Operations ---")

# Read the CSV file into a DataFrame
df_rates = pd.read_csv('./exchange_rates.csv')

print("Raw Exchange Rates DataFrame:")
print(df_rates)

# Let's filter to get just the GBP rate for later use
# We look for the row where currency_code is 'GBP', and grab the 'rate_to_usd' column
gbp_rate = df_rates.loc[df_rates['currency_code'] == 'GBP', 'rate_to_usd'].values[0]

print(f"\nExtracted GBP Rate: {gbp_rate}")


# ==========================================
# TASK 3: TRANSFORMATION FUNCTION
# ==========================================
print("\n--- Task 3: Data Transformation ---")

def transform_currency(order_list, conversion_rate):
    """
    Takes a list of order dictionaries and a conversion rate.
    Returns a new list with an added 'total_usd' field.
    """
    transformed_data = []
    
    for order in order_list:
        # Create a copy so we don't mess up the original list
        new_order = order.copy()
        
        # Apply transformation: GBP * Rate = USD
        # round(value, 2) keeps it to 2 decimal places
        usd_amount = round(new_order['total_gbp'] * conversion_rate, 2)
        
        # Add new field
        new_order['total_usd'] = usd_amount
        transformed_data.append(new_order)
        
    return transformed_data

# Run the transformation
final_dataset = transform_currency(parsed_orders, gbp_rate)

# Create a final Pandas DataFrame to look at the results nicely
df_final = pd.DataFrame(final_dataset)

print("Final Transformed Data (Ready for Loading):")
print(df_final)

# Bonus: Write the result to a new CSV
df_final.to_csv('./final_report.csv', index=False)
print("\n✅ Success! Saved 'final_report.csv' to disk.")