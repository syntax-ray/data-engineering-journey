import json
import pandas as pd

# dumps is into json.
# loads is from json

def calculate_total_gbp(items):
    total = 0 
    for item in items:
        total += item["price_gbp"] 
    return total

def convert_gbp_usd(gbp):
    exchange_rates = pd.read_csv('./exchange_rates.csv')
    gbp_to_usd_rate = exchange_rates[exchange_rates['currency_code'] == 'GBP']['rate_to_usd'].iloc[0]
    return gbp * float(gbp_to_usd_rate)

def main():
    customer_totals = {}
    with open("./orders.json") as f:
        orders = json.loads(f.read())
    for order in orders:
        # if order['status'] == 'completed':
        total_order_price_gbp = calculate_total_gbp(order["items"])
        total_order_price_usd = convert_gbp_usd(total_order_price_gbp)
        if order['customer']['id'] in customer_totals:
            customer_totals[order['customer']['id']]['orders'].append(
                {
                    'order_id': order['order_id'],
                    'total_gbp': total_order_price_gbp,
                    'total_usd': total_order_price_usd
                }
            )
        else:
            customer_totals[order['customer']['id']] = {
                    'name': order['customer']['name'],
                    'orders': [{
                        'order_id': order['order_id'],
                        'total_gbp': total_order_price_gbp,
                        'total_usd': total_order_price_usd
                    }]
                }
    output_dict = {
        'order_id': [],
        'customer_name': [],
        'total_gbp': [],
        'total_usd' : []
    }
 
    for _, customer in customer_totals.items():
        customer_name = customer['name']
        for order in customer['orders']:
            output_dict['order_id'].append(order['order_id'])
            output_dict['customer_name'].append(customer_name)
            output_dict['total_gbp'].append(order['total_gbp'])
            output_dict['total_usd'].append(order['total_usd'])
    
    output_df = pd.DataFrame(output_dict)
    output_df.to_csv('generated_final_report.csv',index=False)
        

    

if __name__ == "__main__":
    main()