import pandas as pd
import os

FILE_PATH = "./hotel_bookings.csv"

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
    fill_values = values = {"company": 'n/a', "agent": 'n/a'}
    df = df.fillna(value=fill_values)
    df = df.dropna()
    return df



def main():
    
    hotel_bookings = pd.read_csv(FILE_PATH)

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





if __name__ == "__main__":
    main()

    