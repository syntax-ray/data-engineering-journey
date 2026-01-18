import pandas as pd
import os
import iso3166
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv


def check_valid_column_names(names: list):
    for name in names:
        if " " in name:
            return False
    return True


def check_missing_values(df: pd.DataFrame):
    columns = df.isna().sum().to_dict()
    missing_values_present = False
    trouble_columns = {}
    highest_missing_values_count = max(columns.values())
    print(f'The column with the most missing values has {highest_missing_values_count} missing values')
    if highest_missing_values_count > 0:
        for column, count in columns.items():
            if count > 0:
                trouble_columns[column] = count 
                missing_values_present = True 
    return missing_values_present, trouble_columns


def handle_missing_values(df: pd.DataFrame):
    # fill company column values with n/a because the columns missing values cover ~= 94% of the data. Agent covers 14%
    fill_values = {"company": -99, "agent": -99}
    df = df.fillna(value=fill_values)
    df = df.dropna()
    return df

def check_datatypes_ok(df: pd.DataFrame):
    trouble_columns = {}
    datatypes_ok = True
    expected_datatypes = {
        'hotel': 'object',                      
        'is_canceled': 'int64',                       
        'lead_time': 'float64',                         
        'arrival_date_year':  'int64',                 
        'arrival_date_month': 'object',                 
        'arrival_date_week_number': 'int64',       
        'arrival_date_day_of_month': 'int64',        
        'stays_in_weekend_nights': 'int64',            
        'stays_in_week_nights': 'int64',  
        'days_in_waiting_list': 'float64',             
        'adults': 'int64',                             
        'children': 'int64',                            
        'babies': 'int64',                             
        'meal': 'object',                              
        'country': 'object',                            
        'market_segment': 'object',                     
        'distribution_channel': 'object',               
        'is_repeated_guest': 'int64',                  
        'previous_cancellations': 'int64',             
        'previous_bookings_not_canceled': 'int64',     
        'reserved_room_type': 'object',             
        'assigned_room_type': 'object',                  
        'booking_changes': 'int64',                    
        'deposit_type': 'object',                       
        'agent': 'int64',                              
        'company': 'int64',                            
        'days_in_waiting_list,': 'float64',              
        'customer_type': 'object',                     
        'adr': 'float64',                               
        'required_car_parking_spaces': 'int64',       
        'total_of_special_requests': 'int64',         
        'reservation_status': 'object',                  
        'reservation_status_date': 'object'           
    }
    actual_datatypes = df.dtypes.to_dict()
    for column, dtype in actual_datatypes.items():
        if dtype != expected_datatypes[column]:
            datatypes_ok = False
            trouble_columns[column] =  f'The actual value is {dtype} it should be {expected_datatypes[column]}'
    return datatypes_ok, trouble_columns


def handle_invalid_datatypes(df: pd.DataFrame):
       df['hotel'] = df['hotel'].astype('object')
       df['is_canceled'] = df['is_canceled'].astype('int64')               
       df['lead_time'] =  df['lead_time'].astype('float64')                      
       df['arrival_date_year'] = df['arrival_date_year'].astype('int64')                                  
       df['arrival_date_month'] = df['arrival_date_month'].astype('object')  
       df['arrival_date_week_number'] = df['arrival_date_week_number'].astype('int64')
       df['arrival_date_day_of_month'] = df['arrival_date_day_of_month'].astype('int64')  
       df['stays_in_weekend_nights'] = df['stays_in_weekend_nights'].astype('int64')  
       df['stays_in_week_nights'] = df['stays_in_week_nights'].astype('int64')   
       df['days_in_waiting_list'] = df['days_in_waiting_list'].astype('float64')
       df['adults'] = df['adults'].astype('int64')   
       df['children'] = df['children'].astype('int64')
       df['babies'] = df['babies'].astype('int64') 
       df['meal'] = df['meal'].astype('object')
       df['country'] = df['country'].astype('object')
       df['market_segment'] = df['market_segment'].astype('object')
       df['distribution_channel'] = df['distribution_channel'].astype('object')
       df['is_repeated_guest'] = df['is_repeated_guest'].astype('int64')
       df['previous_cancellations'] = df['previous_cancellations'].astype('int64')
       df['previous_bookings_not_canceled'] = df['previous_bookings_not_canceled'].astype('int64')
       df['reserved_room_type'] = df['reserved_room_type'].astype('object')
       df['assigned_room_type'] = df['assigned_room_type'].astype('object')
       df['booking_changes'] = df['booking_changes'].astype('int64')
       df['deposit_type'] = df['deposit_type'].astype('object')
       df['agent'] = df['agent'].astype('int64')
       df['company'] = df['company'].astype('int64')
       df['days_in_waiting_list,'] = df['days_in_waiting_list'].astype('float64')
       df['customer_type'] = df['customer_type'].astype('object')
       df['adr'] = df['adr'].astype('float64')
       df['required_car_parking_spaces'] = df['required_car_parking_spaces'].astype('int64')
       df['total_of_special_requests'] = df['total_of_special_requests'].astype('int64')
       df['reservation_status'] = df['reservation_status'].astype('object')
       df['reservation_status_date'] = df['reservation_status_date'].astype('object')
       return df

def check_duplicates(df: pd.DataFrame):
    duplicate_count = df.duplicated().sum()
    return duplicate_count > 0, duplicate_count

def handle_duplicates(df: pd.DataFrame):
    return df.drop_duplicates()


def check_business_logic(df: pd.DataFrame):
    business_logic_ok = True
    trouble_columns = set()
    if df['hotel'].nunique() > 2 or not set(df['hotel'].unique()).issubset({'Resort Hotel', 'City Hotel'}):
        business_logic_ok = False
        trouble_columns.add('hotel')
    
    if df['is_canceled'].nunique() > 2 or not set(df['is_canceled'].unique()).issubset({0, 1}):
        business_logic_ok = False
        trouble_columns.add('is_canceled')

    if df['lead_time'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('lead_time')

    if df['arrival_date_year'].min() < 2000 or df['arrival_date_year'].max() > 2025:
        business_logic_ok = False
        trouble_columns.add('arrival_date_year')

    if df['arrival_date_month'].nunique() != 12 or not set(df['arrival_date_month'].unique()).issubset(
        {'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'}):
        business_logic_ok = False
        trouble_columns.add('arrival_date_month')
    
    if df['arrival_date_week_number'].min() < 1 or df['arrival_date_week_number'].max() > 53:
        business_logic_ok = False
        trouble_columns.add('arrival_date_week_number')

    if df['arrival_date_day_of_month'].min() < 1 or df['arrival_date_day_of_month'].max() > 31:
        business_logic_ok = False
        trouble_columns.add('arrival_date_day_of_month')

    if df['stays_in_weekend_nights'].min() < 0 or df['stays_in_week_nights'].max() > 1000:
        business_logic_ok = False
        trouble_columns.add('lead_time')

    if df['adults'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('adults')

    if df['children'].min() < 0:  
        business_logic_ok = False
        trouble_columns.add('children')

    if df['babies'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('babies')

    if df['meal'].nunique() != 5:
        business_logic_ok = False
        trouble_columns.add('meal')


    valid_country_codes = set([c.alpha3 for c in iso3166.countries])
    valid_country_codes.add('TMP')


    if not set(df['country'].unique()).issubset(valid_country_codes):
        business_logic_ok = False
        trouble_columns.add('country')

    if df['market_segment'].nunique() != 7 or not set(df['market_segment'].unique()).issubset(
        {'Direct', 'Corporate', 'Online TA', 'Offline TA/TO', 'Complementary', 'Groups', 'Aviation'}):
        business_logic_ok = False
        trouble_columns.add('market_segment')
    
    if df['distribution_channel'].nunique() != 5 or not set(df['distribution_channel'].unique()).issubset(
        {'Direct', 'Corporate', 'TA/TO', 'Undefined', 'GDS'}):
        business_logic_ok = False
        trouble_columns.add('distribution_channel')
    
    
    if df['is_repeated_guest'].nunique() > 2 or not set(df['is_repeated_guest'].unique()).issubset({0, 1}):
        business_logic_ok = False
        trouble_columns.add('is_repeated_guest')

    if df['previous_cancellations'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('previous_cancellations')

    if df['previous_bookings_not_canceled'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('previous_bookings_not_canceled')

    if df['reserved_room_type'].nunique() > 26 or not set(df['reserved_room_type'].unique()).issubset(
        {'C', 'A', 'D', 'E', 'G', 'F', 'H', 'L', 'B', 'P', 'I', 'K', 'J', 'M', 'N', 'O', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}):
        business_logic_ok = False
        trouble_columns.add('reserved_room_type')

    if df['assigned_room_type'].nunique() > 26 or not set(df['assigned_room_type'].unique()).issubset(
        {'C', 'A', 'D', 'E', 'G', 'F', 'H', 'L', 'B', 'P', 'I', 'K', 'J', 'M', 'N', 'O', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}):
        business_logic_ok = False
        trouble_columns.add('assigned_room_type')

    if df['booking_changes'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('booking_changes') 

    if df['deposit_type'].nunique() != 3 or not set(df['deposit_type'].unique()).issubset(
        {'No Deposit', 'Non Refund', 'Refundable'}):
        business_logic_ok = False
        trouble_columns.add('deposit_type') 

    if df['agent'].min() < -1 and df['agent'].min() != -99:
        business_logic_ok = False
        trouble_columns.add('agent')

    if df['company'].min() < -1 and df['company'].min() != -99:
        business_logic_ok = False
        trouble_columns.add('company')

    if df['days_in_waiting_list'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('days_in_waiting_list')

    if df['customer_type'].nunique() != 4 or not set(df['customer_type'].unique()).issubset(
        {'Contract', 'Group', 'Transient', 'Transient-Party'}):
        business_logic_ok = False
        trouble_columns.add('customer_type')

    if df['adr'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('adr')

    if df['required_car_parking_spaces'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('required_car_parking_spaces')

    if df['total_of_special_requests'].min() < 0:
        business_logic_ok = False
        trouble_columns.add('total_of_special_requests')

    if df['reservation_status'].nunique() != 3 or not set(df['reservation_status'].unique()).issubset(
        {'Canceled', 'Check-Out', 'No-Show'}):
        business_logic_ok = False
        trouble_columns.add('reservation_status')

    if not pd.to_datetime(df['reservation_status_date'], errors='coerce').notnull().all() or pd.to_datetime(df['reservation_status_date']).min() < pd.Timestamp('2000-01-01') or pd.to_datetime(df['reservation_status_date']).max() > pd.Timestamp('2025-01-01'):
        business_logic_ok = False
        trouble_columns.add('reservation_status_date')
    
    return business_logic_ok, trouble_columns


def handle_business_logic_issues(df: pd.DataFrame):
    # Update China country code.
    df.loc[df['country'] == 'CN', 'country'] = 'CHN'
    df.loc[df['adr'] < 0, 'adr'] = 0
    return df


def save_cleaned_data(df: pd.DataFrame):
    # to csv
    df.to_csv("./hotel_bookings_cleaned.csv", index=False)

    # to postgresql

    # this script can either connect to postgres from inside the service network or from ouside this handles that.
    full_curr_path = os.getcwd()
    split_path = full_curr_path.split("/")
    curr_dir_name = split_path[-1]

    load_dotenv()

    database = os.getenv("DATABASE")
    user = os.getenv("DB_USER")
    password = os.getenv("PASSWORD")
    if curr_dir_name == "app":
        host_name = os.getenv("DOCKER_HOST_NAME")
        port = os.getenv("DOCKER_PORT")
    else:
        host_name = os.getenv("LOCAL_HOST_NAME")
        port = os.getenv("LOCAL_PORT")

    conn_str = f'postgresql://{user}:{password}@{host_name}:{port}/{database}'
    print(f'The connection string to be used is shown below')
    print(conn_str)
    engine = create_engine(f'postgresql://{user}:{password}@{host_name}:{port}/{database}') 

    df.to_sql('hotel_bookings', engine, if_exists='replace', index=False)

    print("Saving complete")


'''

Cleaning Pipeline:
   Check column names -> Handle missing values -> Fix column datatypes  -> Fix duplicates -> Business logic checks
   Save cleaned data to new CSV file

'''
def main():

    file_path = "./hotel_bookings.csv"
    hotel_bookings = pd.read_csv(file_path)

    print(f'The column has {hotel_bookings.shape[0]} rows')



    if check_valid_column_names(hotel_bookings.columns.values):
        print("Column names are valid")
    else:
        print("Invalid column names present")
        # handle_invalid_column_names(hotel_bookings_raw)

    while True:  
        missing_values_check = check_missing_values(hotel_bookings)
        if not missing_values_check[0]:
            print("Columns do not have missing values")
            break
        else:
            print("Columns have missing values")
            print(f"The trouble columns are {missing_values_check[1]}")
            hotel_bookings = handle_missing_values(df=hotel_bookings)


    while True:  
        datatypes_check = check_datatypes_ok(hotel_bookings)
        if datatypes_check[0]:
            print("Data types are okay")
            break
        else:
            print(f' {len(datatypes_check[1])} column data types are off')
            print(datatypes_check[1])
            hotel_bookings =  handle_invalid_datatypes(df=hotel_bookings)

    while True:
        duplicates_check = check_duplicates(hotel_bookings)
        if duplicates_check[0]:
            print(f"Dataset contains {duplicates_check[1]} duplicates")
            hotel_booking_dup = hotel_bookings[hotel_bookings.duplicated(hotel_bookings.columns.values.tolist(), keep=False)].sort_values(hotel_bookings.columns.values.tolist(),)
            hotel_booking_dup.to_csv("./hotel_bookings_duplicates.csv", index=False)
            print("Duplicates have been saved to hotel_bookings_duplicates.csv for inspection")
            drop_duplicates = input("Do you want to drop duplicates? (yes/no): ")
            if drop_duplicates.lower().strip() != 'yes':
                print("Exiting without dropping duplicates")
                break
            hotel_bookings = handle_duplicates(hotel_bookings)
            if os.path.exists("./hotel_bookings_duplicates.csv"):
                os.remove("./hotel_bookings_duplicates.csv")
        else:
            print("No duplicates found")
            break

    while True:
         business_check = check_business_logic(hotel_bookings)
         if business_check[0]:
             print("Business logic checks passed")
             break
         else:
             print(f"Business logic checks failed for columns: {business_check[1]}")
             hotel_bookings = handle_business_logic_issues(hotel_bookings)

    save_cleaned_data(hotel_bookings)

if __name__ == "__main__":
    main()

    